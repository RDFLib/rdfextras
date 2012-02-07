"""
This module implements two hash tables for identifiers and values that
facilitate maximal index lookups and minimal redundancy (since identifiers and
values are stored once only and referred to by integer half-md5-hashes). The
identifier hash uses the half-md5-hash (converted by base conversion to an
integer) to key on the identifier's full lexical form (for partial matching by
REGEX) and their term types. The use of a half-hash introduces a collision
risk that is currently not accounted for. The volume at which the risk becomes
significant is calculable, though through the 'birthday paradox'.

The value hash is keyed off the half-md5-hash (as an integer also) and stores
the identifier's full lexical representation (for partial matching by REGEX)

These classes are meant to automate the creation, management, linking,
insertion of these hashes (by SQL) automatically

see: http://en.wikipedia.org/wiki/Birthday_Paradox
"""

from rdflib.term import Literal
from rdflib.namespace import RDF
from rdflib.graph import QuotedGraph
from rdflib.graph import Graph
from rdfextras.utils.termutils import OBJECT
from rdfextras.utils.termutils import escape_quotes
from rdfextras.store.REGEXMatching import REGEXTerm
from rdfextras.store.FOPLRelationalModel.QuadSlot import normalizeValue
Any = None

COLLISION_DETECTION = False
REGEX_IDX = False
CREATE_HASH_TABLE = """
CREATE TABLE %s (
    %s
) %s"""

IDENTIFIER_GARBAGE_COLLECTION_SQL = """\
CREATE TEMPORARY TABLE danglingIds
    SELECT %s.%s FROM %s %s where %s and %s.%s <> %s;"""
VALUE_GARBAGE_COLLECTION_SQL="""\
CREATE TEMPORARY TABLE danglingIds SELECT %s.%s FROM %s %s where %s"""
PURGE_KEY_SQL="""\
DELETE %s FROM %s INNER JOIN danglingIds on danglingIds.%s = %s.%s;"""

# IDEA: Could we store a refcount in the DB instead of doing this GC?  That
# might also allow for some interesting statistical queries.  -
# clarkj@ccf.org, 2008-02-18

def GarbageCollectionQUERY(idHash,valueHash,aBoxPart,binRelPart,litPart):
    """
    Performs garbage collection on interned identifiers and their references.
    Joins the given KB partitions against the identifiers and values and
    removes the 'danglers'. This must be performed after every removal of an
    assertion and so becomes a primary bottleneck
    """
    purgeQueries = ["drop temporary table if exists danglingIds"]
    rdfTypeInt = normalizeValue(RDF.type,'U')
    idHashKeyName = idHash.columns[0][0]
    valueHashKeyName = valueHash.columns[0][0]
    idHashJoinees    = [aBoxPart,binRelPart,litPart]
    idJoinClauses = []
    idJoinColumnCandidates = []
    explicitJoins = []
    for part in idHashJoinees:
        partJoinClauses = []
        for colName in part.columnNames:
            if part.columnNames.index(colName) >= 4:
                colName,sqlType,index = colName
                if sqlType.lower()[:6]=='bigint':
                    partJoinClauses.append("%s.%s = %s.%s" % \
                            (part,colName,idHash,idHashKeyName))
                    idJoinColumnCandidates.append("%s.%s" % (part,colName))
            elif colName:
                partJoinClauses.append("%s.%s = %s.%s" % \
                                (part,colName,idHash,idHashKeyName))
                idJoinColumnCandidates.append("%s.%s" % (part,colName))
        explicitJoins.append("left join %s on (%s)" % \
                            (part,' or '.join(partJoinClauses)))
        idJoinClauses.extend(partJoinClauses)
    
    intersectionClause = " and ".join([col + " is NULL"
                                        for col in idJoinColumnCandidates])
    idGCQuery = IDENTIFIER_GARBAGE_COLLECTION_SQL%(
        idHash,
        idHashKeyName,
        idHash,
        ' '.join(explicitJoins),
        intersectionClause,
        idHash,
        idHashKeyName,
        rdfTypeInt
    )
    
    idPurgeQuery = PURGE_KEY_SQL % \
            (idHash,idHash,idHashKeyName,idHash,idHashKeyName)
    purgeQueries.append(idGCQuery)
    purgeQueries.append(idPurgeQuery)
    
    partJoinClauses = []
    idJoinColumnCandidates = []
    explicitJoins = []
    partJoinClauses.append("%s.%s = %s.%s" % \
            (litPart,litPart.columnNames[OBJECT],valueHash,valueHashKeyName))
    idJoinColumnCandidates.append("%s.%s" % \
            (litPart,litPart.columnNames[OBJECT]))
    
    intersectionClause = " and ".join([col + " is NULL" 
                            for col in idJoinColumnCandidates])
    valueGCQuery = VALUE_GARBAGE_COLLECTION_SQL%(
        valueHash,
        valueHashKeyName,
        valueHash,
        "left join %s on (%s)"%(litPart,' or '.join(partJoinClauses)),
        intersectionClause
    )
    
    valuePurgeQuery = PURGE_KEY_SQL % \
        (valueHash,valueHash,valueHashKeyName,valueHash,valueHashKeyName)
    purgeQueries.append("drop temporary table if exists danglingIds")
    purgeQueries.append(valueGCQuery)
    purgeQueries.append(valuePurgeQuery)
    return purgeQueries

class Table(object):
    def get_name(self):
        '''
        Returns the name of this table in the backing SQL database.
        '''
        raise NotImplementedError('`Table` is an abstract base class.')
    
    def createStatements(self):
        '''
        Returns a list of SQL statements that, when executed, will create this
        table (and any other critical data structures).
        '''
        raise NotImplementedError('`Table` is an abstract base class.')
    
    def defaultStatements(self):
        '''
        Returns a list of SQL statements that, when executed, will provide an
        initial set of rows for this table.
        '''
        return []
    
    def indexingStatements(self):
        '''
        Returns a list of SQL statements that, when executed, will create
        appropriate indices for this table.
        '''
        return []
    
    def removeIndexingStatements(self):
        '''
        Returns a list of SQL statements that, when executed, will remove all of
        the indices corresponding to `indexingStatements`.
        '''
        return []
    
    def foreignKeyStatements(self):
        '''
        Returns a list of SQL statements that, when executed, will initialize
        appropriate foreign key references for this table.
        '''
        return []
    
    def removeForeignKeyStatements(self):
        '''
        Returns a list of SQL statements that, when executed, will remove all
        the foreign key references corresponding to `foreignKeyStatements`.
        '''
        return []
    

class RelationalHash(Table):
    def __init__(
                 self, identifier,
                 useSignedInts=False, hashFieldType='BIGINT unsigned',
                 engine='ENGINE=InnoDB', declareEnums=False):
        self.useSignedInts = useSignedInts
        self.hashFieldType = hashFieldType
        self.engine = engine
        self.declareEnums = declareEnums
        self.identifier = identifier
        self.hashUpdateQueue = {}
    
    def EscapeQuotes(self,qstr):
        return escape_quotes(qstr)

    def normalizeTerm(self,term):
        if isinstance(term,(QuotedGraph, Graph)):
            return term.identifier.encode('utf-8')
        elif isinstance(term,Literal):
            return self.EscapeQuotes(term).encode('utf-8')
        elif term is None or isinstance(term,(tuple,list,REGEXTerm)):
            return term
        else:
            return term.encode('utf-8')
    
    def __repr__(self):
        return "%s_%s"%(self.identifier,self.tableNameSuffix)
    
    def get_name(self):
        return "%s_%s"%(self.identifier,self.tableNameSuffix)
    
    def indexingStatements(self):
        idxSQLStmts = []
        for colName, colType, indexMD in self.columns:
            if indexMD:
                indexName, indexCol = indexMD
                if indexName:
                    idxSQLStmts.append("CREATE INDEX %s_%s ON %s (%s)" %
                                       (self, indexName, self, indexCol))
                else:
                    idxSQLStmts.append(
                      "ALTER TABLE %s ADD PRIMARY KEY (%s)" %
                      (self, indexCol))
        return idxSQLStmts
    
    def removeIndexingStatements(self):
        idxSQLStmts = []
        for colName, colType, indexMD in self.columns:
            if indexMD:
                indexName, indexCol = indexMD
                if indexName:
                    idxSQLStmts.append("DROP INDEX %s_%s ON %s" %
                                       (self, indexName, self))
                else:
                    idxSQLStmts.append("ALTER TABLE %s DROP PRIMARY KEY" %
                                       (self,))
        return idxSQLStmts
    
    def createStatements(self):
        statements = []
        columnSQLStmts = []
        for colName, colType, indexMD in self.columns:
            if isinstance(colType, list):
                if self.declareEnums:
                    # This is disabled until PostgreSQL grows enums (8.3)
                    if False:
                      enumName = '%s_enum' % (colName,)
                      statements.append(
                        'CREATE TYPE %s AS ENUM (%s)' %
                        (enumName, ', '.join(
                          ["'%s'" % item for item in colType])))
                    enumName = 'char'
                    columnSQLStmts.append("\t%s %s not NULL" %
                                            (colName, enumName))
                else:
                    columnSQLStmts.append("\t%s\t%s not NULL" %
                      (colName, 'enum(%s)' % ', '.join(
                        ["'%s'" % item for item in colType])))
            else:
                columnSQLStmts.append("\t%s\t%s not NULL" %
                                        (colName, colType))
        
        statements.append(CREATE_HASH_TABLE % (
            self,
            ',\n'.join(columnSQLStmts),
            self.engine))
        return statements
    
    def getRowsByHash(self, db, hash):
        c = db.cursor()
        keyCol = self.columns[0][0]
        c.execute('SELECT * FROM %s WHERE %s = %s' % (self, keyCol, hash))
        return c.fetchall()
    
    def dropSQL(self):
        pass
    

class IdentifierHash(RelationalHash):
    
    tableNameSuffix = 'identifiers'
    
    def __init__(
                 self, identifier,
                 useSignedInts=False, hashFieldType='BIGINT unsigned',
                 engine='ENGINE=InnoDB', declareEnums=False):
        super(IdentifierHash, self).__init__(
          identifier, useSignedInts, hashFieldType, engine, declareEnums)
        self.columns = [
          ('id', self.hashFieldType, [None, 'id']),
          ('term_type',
           ['U', 'B', 'F', 'V', 'L'],
           ['termTypeIndex', 'term_type']),
        ]
        
        if REGEX_IDX:
            self.columns.append(
              ('lexical', 'text', ['lexicalIndex', 'lexical(100)']),)
        else:
            self.columns.append(('lexical', 'text', None))
    
    def viewUnionSelectExpression(self,relations_only=False):
        return "select * from %s"%(repr(self))
    
    def defaultStatements(self):
        """
        Since rdf:type is modeled explicitely (in the ABOX partition) it
        must be inserted as a 'default' identifier.
        """
        return ["INSERT INTO %s VALUES (%s, 'U', '%s');" %
                  (self, normalizeValue(RDF.type, 'U', self.useSignedInts),
                   RDF.type)]
    
    def generateDict(self,db):
        c=db.cursor()
        c.execute("select * from %s"%self)
        rtDict = {}
        for rt in c.fetchall():
            rtDict[rt[0]] = (rt[1],rt[2])
        c.close()
        return rtDict
    
    def updateIdentifierQueue(self,termList):
        for term,termType in termList:
            md5Int = normalizeValue(term, termType, self.useSignedInts)
            self.hashUpdateQueue[md5Int] = (termType,
                                            self.normalizeTerm(term))
    
    def insertIdentifiers(self,db):
        c=db.cursor()
        keyCol = self.columns[0][0]
        if self.hashUpdateQueue:
            params = [(md5Int, termType, lexical)
                      for md5Int, (termType, lexical)
                        in self.hashUpdateQueue.items()
                        if len(self.getRowsByHash(db, md5Int)) == 0]
            if len(params) > 0:
                c.executemany(
                  "INSERT INTO %s" % (self,) + " VALUES (%s,%s,%s)", params)
            
            if COLLISION_DETECTION:
                insertedIds = self.hashUpdateQueue.keys()
                if len(insertedIds) > 1:
                    c.execute("SELECT * FROM %s" % \
                            (self)+" WHERE %s" % \
                                keyCol+" in %s",(tuple(insertedIds),))
                else:
                    c.execute("SELECT * FROM %s" % \
                            (self)+" WHERE %s" % \
                                keyCol+" = %s",tuple(insertedIds))
                for key,termType,lexical in c.fetchall():
                    if self.hashUpdateQueue[key] != (termType,lexical):
                        # Collision!!! Raise an exception (allow the app to 
                        # rollback the transaction if it wants to)
                        raise Exception(
                            "Hash Collision (in %s) on %s,%s vs %s,%s!" % \
                                (self, termType, lexical, 
                                self.hashUpdateQueue[key][0],
                                self.hashUpdateQueue[key][1]))
            
            self.hashUpdateQueue = {}
        c.close()
    

class LiteralHash(RelationalHash):
    tableNameSuffix = 'literals'
    
    def __init__(
                 self, identifier,
                 useSignedInts=False, hashFieldType='BIGINT unsigned',
                 engine='ENGINE=InnoDB', declareEnums=False):
        super(LiteralHash, self).__init__(
          identifier, useSignedInts, hashFieldType, engine, declareEnums)
        self.columns = [('id', self.hashFieldType, [None, 'id']),]
        
        if REGEX_IDX:
            self.columns.append(
              ('lexical', 'text', ['lexicalIndex', 'lexical(100)']),)
        else:
            self.columns.append(('lexical', 'text', None))
    
    def viewUnionSelectExpression(self,relations_only=False):
        return "select %s, 'L' as term_type, lexical from %s" % \
                (self.columns[0][0],repr(self))
    
    def generateDict(self,db):
        c=db.cursor()
        c.execute("select * from %s"%self)
        rtDict = {}
        for rt in c.fetchall():
            rtDict[rt[0]] = rt[1]
        c.close()
        return rtDict
    
    def updateIdentifierQueue(self,termList):
        for term,termType in termList:
            md5Int = normalizeValue(term, termType, self.useSignedInts)
            self.hashUpdateQueue[md5Int]=self.normalizeTerm(term)
    
    def insertIdentifiers(self,db):
        c=db.cursor()
        keyCol = self.columns[0][0]
        if self.hashUpdateQueue:
            params = [(md5Int, lexical) for md5Int, lexical
                        in self.hashUpdateQueue.items()
                        if len(self.getRowsByHash(db, md5Int)) == 0]
            if len(params) > 0:
                c.executemany(
                  "INSERT INTO %s" % (self,) + " VALUES (%s,%s)", params)
            
            if COLLISION_DETECTION:
                insertedIds = self.hashUpdateQueue.keys()
                if len(insertedIds) > 1:
                    c.execute("SELECT * FROM %s" % \
                        (self)+" WHERE %s" % \
                            keyCol+" in %s",(tuple(insertedIds),))
                else:
                    c.execute("SELECT * FROM %s" % \
                            (self)+" WHERE %s" % \
                                keyCol+" = %s",tuple(insertedIds))
                for key,lexical in c.fetchall():
                    if self.hashUpdateQueue[key] != lexical:
                        # Collision!!! Raise an exception (allow the app to 
                        # rollback the transaction if it wants to)
                        raise Exception(
                            "Hash Collision (in %s) on %s vs %s!" % \
                                (self,lexical,self.hashUpdateQueue[key][0]))
            self.hashUpdateQueue = {}
        c.close()
    
# Convenience
# from rdfextras.store.FOPLRelationalModel.RelationalHash import COLLISION_DETECTION
# from rdfextras.store.FOPLRelationalModel.RelationalHash import REGEX_IDX
# from rdfextras.store.FOPLRelationalModel.RelationalHash import CREATE_HASH_TABLE
# from rdfextras.store.FOPLRelationalModel.RelationalHash import IDENTIFIER_GARBAGE_COLLECTION_SQL
# from rdfextras.store.FOPLRelationalModel.RelationalHash import VALUE_GARBAGE_COLLECTION_SQL
# from rdfextras.store.FOPLRelationalModel.RelationalHash import PURGE_KEY_SQL
# from rdfextras.store.FOPLRelationalModel.RelationalHash import Table
# from rdfextras.store.FOPLRelationalModel.RelationalHash import RelationalHash
# from rdfextras.store.FOPLRelationalModel.RelationalHash import IdentifierHash
# from rdfextras.store.FOPLRelationalModel.RelationalHash import LiteralHash
# from rdfextras.store.FOPLRelationalModel.RelationalHash import GarbageCollectionQUERY