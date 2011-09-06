"""
Elixir.py
SQLAlchemy/Elixir ORM implementation of AbstractSQLStore
"""

import logging
import re
import os

from rdflib import Literal
from rdflib import RDF
from rdflib.graph import Graph
from rdflib.graph import QuotedGraph
from rdfextras.store.REGEXMatching import PYTHON_REGEX
from rdfextras.store.REGEXMatching import REGEXTerm
from rdfextras.store.AbstractSQLStore import TRIPLE_SELECT_NO_ORDER
from rdfextras.store.AbstractSQLStore import ASSERTED_NON_TYPE_PARTITION
from rdfextras.store.AbstractSQLStore import ASSERTED_TYPE_PARTITION
from rdfextras.store.AbstractSQLStore import QUOTED_PARTITION
from rdfextras.store.AbstractSQLStore import ASSERTED_LITERAL_PARTITION
from rdfextras.store.AbstractSQLStore import table_name_prefixes
from rdfextras.store.AbstractSQLStore import AbstractSQLStore
from rdfextras.store.AbstractSQLStore import extractTriple
from rdfextras.store.AbstractSQLStore import unionSELECT
from rdfextras.tools.term_utils import escape_quotes

import elixir
from elixir import *
from sqlalchemy import *
from sqlalchemy.orm import scoped_session, sessionmaker

logging.basicConfig(level=logging.ERROR,format="%(message)s")
_logger = logging.getLogger('rdfextras.store.Elixir')
_logger.setLevel(logging.ERROR)

_literal = re.compile(
    r'''"(?P<value>[^@&]*)"(?:@(?P<lang>[^&]*))?(?:&<(?P<datatype>.*)>)?''')

Any = None
LITERAL = 0
URI = 1
NO_URI = 'uri://oops/'
tablename_prefix = "rdflib"

index_listing = [
    ("%s_asserted_statements",
     [("%s_A_termComb_index",('termComb',)),
      ("%s_A_s_index",('subject',)),
      ("%s_A_p_index",('predicate',)),
      ("%s_A_o_index",('object',)),
      ("%s_A_c_index",('context',))]),
    ("%s_type_statements",
     [("%s_T_termComb_index",('termComb',)),
      ("%s_member_index",('member',)),
      ("%s_klass_index",('klass',)),
      ("%s_c_index",('context',))]),
    ("%s_literal_statements",
     [("%s_L_termComb_index",('termComb',)),
      ("%s_L_s_index",('subject',)),
      ("%s_L_p_index",('predicate',)),
      ("%s_L_c_index",('context',))]),
    ("%s_quoted_statements",
     [("%s_Q_termComb_index",('termComb',)),
      ("%s_Q_s_index",('subject',)),
      ("%s_Q_p_index",('predicate',)),
      ("%s_Q_o_index",('object',)),
      ("%s_Q_c_index",('context',))]),
    ("%s_namespace_binds",
     [("%s_uri_index",('uri',))])]

# User-defined REGEXP operator
def regexp(expr, item):
    r = re.compile(expr)
    return r.match(item) is not None


class Elixir(AbstractSQLStore):
    """
    SQLite store formula-aware implementation.  It stores its triples in the
    following partitions:
    
    - Asserted non rdf:type statements
    - Asserted rdf:type statements (in a table which models Class membership)
    The motivation for this partition is primarily query speed and scalability
    as most graphs will always have more rdf:type statements than others
    
    - All Quoted statements
    
    In addition it persists namespace mappings in a seperate table
    """
    context_aware = True
    formula_aware = True
    transaction_aware = True
    regex_matching = PYTHON_REGEX
    autocommit_default = False
    _Store__node_pickler = None
    
    def __init__(self, uri=None):
        self.uri = uri
        self.path = uri
        self.engine = None
        self.dbsession = scoped_session(sessionmaker())
        self.elixir_session = elixir.session = self.dbsession
        self.elixir_metadata = elixir.metadata = MetaData()

        class AssertedStatement(Entity):
            """
            CREATE_ASSERTED_STATEMENTS_TABLE = '''
            CREATE TABLE %s_asserted_statements (
                subject       text not NULL,
                predicate     text not NULL,
                object        text not NULL,
                context       text not NULL,
                termComb      tinyint unsigned not NULL)'''
            """
            using_options(shortnames=True,
                            tablename='%s_asserted_statements'%tablename_prefix)
            subject = Field(String, nullable=False)
            predicate = Field(String(20), nullable=False)
            object = Field(String, nullable=False)
            context = Field(String, nullable=False)
            termComb = Field(Integer, nullable=False)
            def __repr__(self):
                return "<Asserted Statement (%s)>" % (self.value)

        class AssertedTypeStatement(Entity):
            """
            CREATE_ASSERTED_TYPE_STATEMENTS_TABLE = '''
            CREATE TABLE %s_type_statements (
                member        text not NULL,
                klass         text not NULL,
                context       text not NULL,
                termComb      tinyint unsigned not NULL)'''
            """
            using_options(shortnames=True,
                            tablename='%s_type_statements'%tablename_prefix)
            member = Field(String, nullable=False)
            klass = Field(String, nullable=False)
            context = Field(String, nullable=False)
            termComb = Field(Integer, nullable=False)
            def __repr__(self):
                return "<Asserted Type Statement (%s)>" % (self.value)

        class LiteralStatement(Entity):
            """
            CREATE_LITERAL_STATEMENTS_TABLE = '''
            CREATE TABLE %s_literal_statements (
                subject       text not NULL,
                predicate     text not NULL,
                object        text,
                context       text not NULL,
                termComb      tinyint unsigned not NULL,
                objLanguage   varchar(3),
                objDatatype   text)'''
            """
            using_options(shortnames=True,
                          tablename='%s_literal_statements'%tablename_prefix)
            subject = Field(String, nullable=False)
            predicate = Field(String(20), nullable=False)
            object = Field(Unicode)
            context = Field(String, nullable=False)
            termComb = Field(Integer, nullable=False)
            objLanguage = Field(String(3), nullable=False)
            objDatatype = Field(String)
            def __repr__(self):
                return "<Literal Statement (%s)>" % (self.value)

        class QuotedStatement(Entity):
            """
            CREATE_QUOTED_STATEMENTS_TABLE = '''
            CREATE TABLE %s_quoted_statements (
                subject       text not NULL,
                predicate     text not NULL,
                object        text,
                context       text not NULL,
                termComb      tinyint unsigned not NULL,
                objLanguage   varchar(3),
                objDatatype   text)'''
            """
            using_options(shortnames=True,
                          tablename='%s_quoted_statements'%tablename_prefix)
            subject = Field(String, nullable=False)
            predicate = Field(String(20), nullable=False)
            object = Field(Unicode)
            context = Field(String, nullable=False)
            termComb = Field(Integer, nullable=False)
            objLanguage = Field(String(3), nullable=False)
            objDatatype = Field(String)
            def __repr__(self):
                return "<Quoted Statement (%s)>"%self.value

        class Namespace(Entity):
            """
            CREATE_NS_BINDS_TABLE = '''
            CREATE TABLE %s_namespace_binds (
                prefix        varchar(20) UNIQUE not NULL,
                uri           text,
                PRIMARY KEY (prefix))'''
            """
            using_options(shortnames=True,
                          tablename='%s_namespace_binds'%tablename_prefix)
            prefix = Field(String(20), 
                            unique=True, nullable=False, primary_key=True)
            uri = Field(String)
            def __repr__(self):
                return "<Namespace (%s)>"%self.value
        elixir.setup_all()

        super(Elixir, self).__init__(uri)

    def open(self, home, create=True):
        """
        Opens the store specified by the configuration string. If
        create is True a store will be created if it does not already
        exist. If create is False and a store does not already exist
        an exception is raised. An exception is also raised if a store
        exists, but there is insufficient permissions to open the
        store."""
        self._internedId = 'rdflib'
        self.identifier = home
        
        self.engine = create_engine(home)
        self.elixir_session.configure(bind=self.engine)
        self.elixir_metadata.bind = self.engine
        self._db = self.elixir_metadata.bind.raw_connection()
        if create:
            # metadata.connect(os.path.join(home,self.identifier))
            # metadata.bind = home
            elixir.create_all()
            self.elixir_session.commit()
            c = self._db.cursor()
            for tblName,indices in index_listing:
                for indexName, columns in indices:
                    c.execute(
                        '''CREATE INDEX %s on %s ("%s")''' % \
                        (indexName % self._internedId,
                         tblName % (self._internedId),
                         ','.join(columns)))
            self._db = self.elixir_metadata.bind.raw_connection()
            self.elixir_session.commit()
            # Only required for sqlite
            if self.identifier.startswith('sqlite'):
                self._db.create_function("regexp", 2, regexp)
        else:
            self._db = self.elixir_metadata.bind.raw_connection()
        # The database doesn't exist - nothing is there
        # return -1
        return 1
    
    def destroy(self, uri):
        """
        FIXME: Add documentation
        """
        # metadata.connect(os.path.join(home,self.identifier))
        self.engine = create_engine(uri)
        self.elixir_session.configure(bind=self.engine)
        self.elixir_metadata.bind = self.engine
        self._db = self.elixir_metadata.bind.raw_connection()
        c = self._db.cursor()
        for tblsuffix in table_name_prefixes:
            try:
                c.execute('DROP table IF EXISTS %s' % \
                                    tblsuffix%(self._internedId))
            except Exception, emsg:
                _logger.error("unable to drop table: %s - %s" % (
                        tblsuffix%(self._internedId), str(emsg)))
        # Note, this only removes the associated tables for the closed 
        # world universe given by the identifier
        _logger.debug(
            "Destroyed Close World Universe '%s' in database %s"%(
                self.identifier,uri))
        for tblName,indices in index_listing:
            for indexName, columns in indices:
                c.execute('''DROP INDEX IF EXISTS %s''' % \
                            (indexName % self._internedId))
        self._db.commit()
        self._db.close()
        try:
            os.remove(os.path.join(uri,self.identifier))
        except:
            pass
    
    def EscapeQuotes(self, qstr):
        """
        Overridden because PostgreSQL is in its own quoting world
        """
        if qstr is None:
            return ''
        
        # Based on http://www.sqlalchemy.org/docs/core/engines.html#database-urls
        if store_name == "PostgreSQL" or self.path.startswith('postgresql'):
            tmp = qstr.replace("'", "''")
        else:
            tmp = escape_quotes(qstr)
        return tmp
    
    # This is overridden to leave unicode terms as is
    # Instead of converting them to ascii (the default behavior)
    def normalizeTerm(self,term):
        if isinstance(term,(QuotedGraph,Graph)):
            return term.identifier
        elif isinstance(term,Literal):
            return self.EscapeQuotes(term)
        elif term is None or isinstance(term,(list,REGEXTerm)):
            return term
        else:
            return term
    
    # Where Clause utility Functions
    # The predicate and object clause builders are modified in order to
    # optimize subject and object utility functions which can take lists
    # as their last argument (object, predicate - respectively)
    def buildSubjClause(self,subject,tableName):
        if isinstance(subject,REGEXTerm):
            return " REGEXP (%s,"+" %s)" % \
                (tableName and '%s.subject'%tableName or 'subject'),[subject]
        elif isinstance(subject,list):
            clauseStrings=[]
            paramStrings = []
            for s in subject:
                if isinstance(s,REGEXTerm):
                    clauseStrings.append(" REGEXP (%s,"+" %s)" % \
                        (tableName and '%s.subject' % \
                            tableName or 'subject') + " %s")
                    paramStrings.append(self.normalizeTerm(s))
                elif isinstance(s,(QuotedGraph,Graph)):
                    clauseStrings.append("%s=" % \
                            (tableName and '%s.subject' % \
                                tableName or 'subject')+"%s")
                    paramStrings.append(self.normalizeTerm(s.identifier))
                else:
                    clauseStrings.append("%s=" % \
                            (tableName and '%s.subject' % \
                                tableName or 'subject')+"%s")
                    paramStrings.append(self.normalizeTerm(s))
            return '('+ ' or '.join(clauseStrings) + ')', paramStrings
        elif isinstance(subject,(QuotedGraph,Graph)):
            return "%s=" % \
                    (tableName and '%s.subject' \
                        % tableName or 'subject') + \
                        "%s", [self.normalizeTerm(subject.identifier)]
        else:
            return subject is not None and "%s=" % \
                (tableName and '%s.subject' % tableName \
                        or 'subject')+"%s",[subject] or None
    
    # Capable of taking a list of predicates as well (in which case sub clauses
    # are joined with 'OR')
    def buildPredClause(self,predicate,tableName):
        if isinstance(predicate,REGEXTerm):
            return " REGEXP (%s,"+" %s)" % \
                (tableName and '%s.predicate' % \
                    tableName or 'predicate'),[predicate]
        elif isinstance(predicate,list):
            clauseStrings=[]
            paramStrings = []
            for p in predicate:
                if isinstance(p,REGEXTerm):
                    clauseStrings.append(" REGEXP (%s,"+" %s)" % \
                        (tableName and '%s.predicate' % \
                            tableName or 'predicate'))
                else:
                    clauseStrings.append("%s=" % \
                            (tableName and '%s.predicate' % \
                            tableName or 'predicate') + "%s")
                paramStrings.append(self.normalizeTerm(p))
            return '('+ ' or '.join(clauseStrings) + ')', paramStrings
        else:
            return predicate is not None and "%s=" % \
                    (tableName and '%s.predicate' % \
                        tableName or 'predicate') + \
                            "%s", [predicate] or None
    
    # Capable of taking a list of objects as well (in which case subclauses are
    # joined with 'OR')
    def buildObjClause(self,obj,tableName):
        if isinstance(obj,REGEXTerm):
            return " REGEXP (%s,"+" %s)" % \
                (tableName and '%s.object' % tableName or 'object'),[obj]
        elif isinstance(obj,list):
            clauseStrings=[]
            paramStrings = []
            for o in obj:
                if isinstance(o,REGEXTerm):
                    clauseStrings.append(" REGEXP (%s,"+" %s)" % \
                        (tableName and '%s.object' % tableName or 'object'))
                    paramStrings.append(self.normalizeTerm(o))
                elif isinstance(o,(QuotedGraph,Graph)):
                    clauseStrings.append("%s=" % (tableName and '%s.object' % \
                        tableName or 'object') + "%s")
                    paramStrings.append(self.normalizeTerm(o.identifier))
                else:
                    clauseStrings.append("%s=" % \
                        (tableName and '%s.object' % \
                            tableName or 'object') + "%s")
                    paramStrings.append(self.normalizeTerm(o))
            return '('+ ' or '.join(clauseStrings) + ')', paramStrings
        elif isinstance(obj,(QuotedGraph,Graph)):
            return "%s="%(tableName and '%s.object'%tableName or 'object')+"%s",[self.normalizeTerm(obj.identifier)]
        else:
            return obj is not None and "%s="%(tableName and '%s.object'%tableName or 'object')+"%s",[obj] or None
    
    def buildContextClause(self,context,tableName):
        context = context is not None \
                and self.normalizeTerm(context.identifier) \
                or context
        if isinstance(context,REGEXTerm):
            return " REGEXP (%s,"+" %s)" % (tableName and '%s.context' % \
                    tableName or 'context'),[context]
        else:
            return context is not None and "%s=" % \
                    (tableName and '%s.context' % tableName or 'context') + \
                    "%s" ,[context] or None
    
    def buildTypeMemberClause(self,subject,tableName):
        if isinstance(subject,REGEXTerm):
            return " REGEXP (%s,"+" %s)" % \
                (tableName and '%s.member' % tableName or 'member'),[subject]
        elif isinstance(subject,list):
            clauseStrings=[]
            paramStrings = []
            for s in subject:
                clauseStrings.append("%s.member=" % tableName + "%s")
                if isinstance(s,(QuotedGraph,Graph)):
                    paramStrings.append(self.normalizeTerm(s.identifier))
                else:
                    paramStrings.append(self.normalizeTerm(s))
            return '('+ ' or '.join(clauseStrings) + ')', paramStrings
        else:
            return subject and u"%s.member = "%(tableName)+"%s",[subject]
    
    def buildTypeClassClause(self,obj,tableName):
        if isinstance(obj,REGEXTerm):
            return " REGEXP (%s,"+" %s)" % \
                    (tableName and '%s.klass'%tableName or 'klass'),[obj]
        elif isinstance(obj,list):
            clauseStrings=[]
            paramStrings = []
            for o in obj:
                clauseStrings.append("%s.klass="%tableName+"%s")
                if isinstance(o,(QuotedGraph,Graph)):
                    paramStrings.append(self.normalizeTerm(o.identifier))
                else:
                    paramStrings.append(self.normalizeTerm(o))
            return '('+ ' or '.join(clauseStrings) + ')', paramStrings
        else:
            return obj is not None and "%s.klass = " % \
                                        tableName+"%s",[obj] or None
    
    def triples(self, (subject, predicate, obj), context=None):
        """
        A generator over all the triples matching pattern. Pattern can
        be any objects for comparing against nodes in the store, for
        example, RegExLiteral, Date? DateRange?
        
        quoted table:                <id>_quoted_statements
        asserted rdf:type table:     <id>_type_statements
        asserted non rdf:type table: <id>_asserted_statements
        
        triple columns:
        subject, predicate, object, context, termComb, objLanguage, objDatatype
        class membership columns:
        member, klass, context termComb
        
        FIXME:  These union all selects *may* be further optimized by joins
        
        """
        quoted_table="%s_quoted_statements"%self._internedId
        asserted_table="%s_asserted_statements"%self._internedId
        asserted_type_table="%s_type_statements"%self._internedId
        literal_table = "%s_literal_statements"%self._internedId
        c=self._db.cursor()
        
        parameters = []
        
        if predicate == RDF.type:
            #select from asserted rdf:type partition and quoted table
            #(if a context is specified)
            clauseString,params = self.buildClause(
                            'typeTable', subject, RDF.type, obj,context, True)
            parameters.extend(params)
            selects = [(asserted_type_table,
                        'typeTable',
                        clauseString,
                        ASSERTED_TYPE_PARTITION),]
        
        elif isinstance(predicate,REGEXTerm) and \
                predicate.compiledExpr.match(RDF.type) or not predicate:
            #Select from quoted partition (if context is specified), literal
            # partition if (obj is Literal or None) and asserted non rdf:type
            # partition (if obj is URIRef or None)
            selects = []
            if not self.STRONGLY_TYPED_TERMS or isinstance(obj,Literal) or not obj \
                    or (self.STRONGLY_TYPED_TERMS and isinstance(obj,REGEXTerm)):
                clauseString,params = self.buildClause(
                            'literal', subject, predicate, obj, context)
                parameters.extend(params)
                selects.append(
                            (literal_table,
                            'literal',
                            clauseString,
                            ASSERTED_LITERAL_PARTITION))
            
            if not isinstance(obj,Literal) \
                    and not (isinstance(obj,REGEXTerm) \
                    and self.STRONGLY_TYPED_TERMS) \
                    or not obj:
                clauseString, params = self.buildClause(
                            'asserted',subject,predicate,obj,context)
                parameters.extend(params)
                selects.append(
                            (asserted_table,
                            'asserted',
                            clauseString,
                            ASSERTED_NON_TYPE_PARTITION))
            
            clauseString,params = self.buildClause(
                            'typeTable',subject,RDF.type,obj,context,True)
            parameters.extend(params)
            selects.append(
                            (asserted_type_table,
                             'typeTable',
                             clauseString,
                             ASSERTED_TYPE_PARTITION))
        
        elif predicate:
            #select from asserted non rdf:type partition (optionally), quoted
            #partition (if context is speciied), and literal partition
            #(optionally)
            selects = []
            if not self.STRONGLY_TYPED_TERMS \
                    or isinstance(obj,Literal) \
                    or not obj \
                    or (self.STRONGLY_TYPED_TERMS \
                                and isinstance(obj,REGEXTerm)):
                clauseString,params = self.buildClause(
                            'literal',subject,predicate,obj,context)
                parameters.extend(params)
                selects.append(
                        (literal_table,
                        'literal',
                        clauseString,
                        ASSERTED_LITERAL_PARTITION))
            if not isinstance(obj,Literal) \
                    and not (isinstance(obj,REGEXTerm) \
                    and self.STRONGLY_TYPED_TERMS) \
                    or not obj:
                clauseString,params = self.buildClause(
                            'asserted',subject,predicate,obj,context)
                parameters.extend(params)
                selects.append(
                        (asserted_table,
                         'asserted',
                         clauseString,
                         ASSERTED_NON_TYPE_PARTITION))
        
        if context is not None:
            clauseString,params = self.buildClause(
                            'quoted',subject,predicate, obj,context)
            parameters.extend(params)
            selects.append(
                        (quoted_table,
                         'quoted',
                         clauseString,
                         QUOTED_PARTITION))
        
        q = self._normalizeSQLCmd(unionSELECT(
                    selects, selectType = TRIPLE_SELECT_NO_ORDER))
        _logger.debug(c, q, parameters)
        self.executeSQL(c,q,parameters)
        #NOTE: SQLite does not support ORDER BY terms that aren't
        #integers, so the entire result set must be iterated
        #in order to be able to return a generator of contexts
        tripleCoverage = {}
        if c.rowcount > 0:
            result = c.fetchall()
            c.close()
        else:
            result = []
        for rt in result:
            s, p, o, (graphKlass, idKlass, graphId) = \
                                extractTriple(rt,self,context)
            contexts = tripleCoverage.get((s, p, o), [])
            contexts.append(graphKlass(self, idKlass(graphId)))
            tripleCoverage[(s, p, o)] = contexts
        
        for (s, p, o),contexts in tripleCoverage.items():
            yield (s, p, o), (c for c in contexts)


    def __repr__(self):
        c = self._db.cursor()
        quoted_table = "%s_quoted_statements" % self._internedId
        asserted_table = "%s_asserted_statements" % self._internedId
        asserted_type_table = "%s_type_statements" % self._internedId
        literal_table = "%s_literal_statements" % self._internedId
        
        selects = [
            (
              asserted_type_table,
              'typeTable',
              '',
              ASSERTED_TYPE_PARTITION
            ),
            (
              quoted_table,
              'quoted',
              '',
              QUOTED_PARTITION
            ),
            (
              asserted_table,
              'asserted',
              '',
              ASSERTED_NON_TYPE_PARTITION
            ),
            (
              literal_table,
              'literal',
              '',
              ASSERTED_LITERAL_PARTITION
            ),
        ]
        q = unionSELECT(selects, distinct=False, selectType=COUNT_SELECT)
        self.executeSQL(c, self._normalizeSQLCmd(q))
        rt = c.fetchall()
        typeLen, quotedLen, assertedLen, literalLen = [rtTuple[0] for rtTuple in rt]
        try:
            return "<Partitioned SQL N3 Store: %s contexts, %s classification assertions, %s quoted statements, %s property/value assertions, and %s other assertions>" % (
                len([c for c in self.contexts()]), typeLen, quotedLen, literalLen, assertedLen)
        except Exception:
            return "<Partitioned MySQL N3 Store>"


