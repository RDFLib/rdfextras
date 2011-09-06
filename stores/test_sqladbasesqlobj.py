# -*- coding: utf-8 -*-
import sys
sys.path.append('..')
import test_graph
import test_context
from test_n3_2 import implies
from test_n3_2 import testN3
from test_n3_2 import testN3Store
from rdflib import URIRef
from rdflib import BNode
from rdflib import RDF
from rdflib import RDFS
from rdflib import plugin
from rdflib import store
from rdflib.graph import ConjunctiveGraph
from rdflib.graph import Graph
from rdflib.graph import QuotedGraph
from rdfextras.store.REGEXMatching import REGEXTerm
import unittest

# ../configstrings.py holds deployment-specific db params, e.g.
# mysqlconfigString="user=rdflib,password=seekrit,host=localhost,db=test"
# postgresqlconfigString="user=user,password=password,port=port,host=host,db=dbname"
# mysqluri="mysql+mysqldb://user:password@host:port/database"
# postgresqluri="postgresql+psycopg://user:password@host:port/database""

from configstrings import postgresqluri, mysqluri #, drizzleuri
sqlitememory = "sqlite:///:memory:"
sqlitefile = "sqlite:////var/tmp/test.db"
storetest = True
storename = 'SQLAlchemy' # SQLAlchemy declarative Base with SQLObject's Store 

plugin.register(storename, store.Store,
                'rdfextras.store.SQLAdbapi2SQLObj', 
                'SQLAlchemyStore')

# SQLA SQLite memory
class SQLAlchemySQLiteGraphTestCase(test_graph.GraphTestCase):
    store_name = storename
    path = sqlitememory

class SQLAlchemySQLiteContextTestCase(test_context.ContextTestCase):
    store_name = "SQLAlchemy" # SQLAlchemy_dbapi2
    path = sqlitememory

# SQLA fronting PostgreSQL
class SQLAlchemyPgGraphTestCase(test_graph.GraphTestCase):
    store_name = storename
    path = postgresqluri

class SQLAlchemyPgContextTestCase(test_context.ContextTestCase):
   store_name = storename
   path = postgresqluri

# SQLA fronting MySQL
class SQLAlchemyMySQLGraphTestCase(test_graph.GraphTestCase):
    store_name = storename
    path = mysqluri

class SQLAlchemyORMMySQLContextTestCase(test_context.ContextTestCase):
    store_name = storename
    path = mysqluri

# # SQLA fronting Drizzle
# class SQLAchemyDrizzleGraphTestCase(test_graph.GraphTestCase):
#     store_name = storename
#     path = drizzleuri

# class SQLAlchemyDrizzleContextTestCase(test_context.ContextTestCase):
#     store_name = storename
#     path = drizzleuri

class SQLAlchemyStoreTests(unittest.TestCase):
    store_name = storename
    path = sqlitememory

    def setUp(self):
        self.graph = Graph(store=self.store_name)
        self.graph.open(self.path, create=True)

    def tearDown(self):
        # self.graph.destroy(self.path)
        self.graph.close()

    def test_SQLAlchemy_testN3_store(self):
        testN3Store('SQLAlchemy',sqlitememory)

    def testRegex(self):
        g = self.graph
        g.parse(data=testN3, format="n3")
        try:
            for s,p,o in g.triples((None,implies,None)):
                formulaA = s
                formulaB = o
            
            assert type(formulaA)==QuotedGraph and type(formulaB)==QuotedGraph
            a = URIRef('http://test/a')
            b = URIRef('http://test/b')
            c = URIRef('http://test/c')
            d = URIRef('http://test/d')
            
            universe = ConjunctiveGraph(g.store)
            
            #REGEX triple matching
            assert len(list(universe.triples((None,REGEXTerm('.*22-rdf-syntax-ns.*'),None))))==1
            assert len(list(universe.triples((None,REGEXTerm('.*'),None))))==3
            assert len(list(universe.triples((REGEXTerm('.*formula.*$'),None,None))))==1
            assert len(list(universe.triples((None,None,REGEXTerm('.*formula.*$')))))==1
            assert len(list(universe.triples((None,REGEXTerm('.*implies$'),None))))==1
            for s,p,o in universe.triples((None,REGEXTerm('.*test.*'),None)):
                assert s==a
                assert o==c
            
            for s,p,o in formulaA.triples((None,REGEXTerm('.*type.*'),None)):
                assert o!=c or isinstance(o,BNode)
            
            #REGEX context matching
            assert len(list(universe.contexts((None,None,REGEXTerm('.*schema.*')))))==1
            assert len(list(universe.contexts((None,REGEXTerm('.*'),None))))==3
            
            #test optimized interfaces
            assert len(list(g.store.subjects(RDF.type,[RDFS.Class,c])))==1
            for subj in g.store.subjects(RDF.type,[RDFS.Class,c]):
                assert isinstance(subj,BNode)
            
            assert len(list(g.store.subjects(implies,[REGEXTerm('.*')])))==1
            
            for subj in g.store.subjects(implies,[formulaB,RDFS.Class]):
                assert subj.identifier == formulaA.identifier
            
            assert len(list(g.store.subjects(REGEXTerm('.*'),[formulaB,c])))==2
            assert len(list(g.store.subjects(None,[formulaB,c])))==2
            assert len(list(g.store.subjects(None,[formulaB,c])))==2
            assert len(list(g.store.subjects([REGEXTerm('.*rdf-syntax.*'),d],None)))==2
            
            assert len(list(g.store.objects(None,RDF.type)))==1
            assert len(list(g.store.objects(a,[d,RDF.type])))==1
            assert len(list(g.store.objects(a,[d])))==1
            assert len(list(g.store.objects(a,None)))==1
            assert len(list(g.store.objects(a,[REGEXTerm('.*')])))==1
            assert len(list(g.store.objects([a,c],None)))==1
        
        except:
            g.store.destroy(sqlitememory)
            raise

# To enable profiling data, use nose's built-in hookup with hotshot:
# nosetests --with-profile --profile-stats-file stats.pf test/test_store/test_mysql
# Also see Tarek Ziade's gprof2dot explorations:
# http://tarekziade.wordpress.com/2008/08/25/visual-profiling-with-nose-and-gprof2dot/
