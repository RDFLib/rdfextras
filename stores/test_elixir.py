import test_context
import test_graph
import rdflib
from test_n3_2 import implies
from test_n3_2 import testN3
from test_n3_2 import testN3Store
from rdflib import URIRef
from rdflib import BNode
from rdflib import RDF
from rdflib import RDFS
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
# mysqluri="mysql://user:password@host/database"

from configstrings import postgresqluri, mysqluri
sqlitememory = "sqlite:///:memory:"
sqlitefile = "sqlite:////var/tmp/test.db"
storetest = True
storename = "Elixir"
non_core = True

rdflib.plugin.register(
        'Elixir', rdflib.store.Store,
        'rdfextras.store.Elixir', 'Elixir')

class Elixir0SQLiteMemGraphTestCase(test_graph.GraphTestCase):
    """Elixir SQLite memory"""
    store_name = storename
    path = sqlitememory

class Elixir0SQLiteMemContextTestCase(test_context.ContextTestCase):
    """Elixir SQLite memory"""
    store_name = storename
    path = sqlitememory

# class Elixir1SQLiteFileGraphTestCase(test_graph.GraphTestCase):
#     """Elixir SQLite file"""
#     non_core = True
#     store_name = storename
#     path = sqlitefile

# class Elixir1SQLiteFileContextTestCase(test_context.ContextTestCase):
#     """Elixir SQLite file"""
#     store_name = storename
#     path = sqlitefile

# class Elixir4MySQLGraphTestCase(test_graph.GraphTestCase):
#     """Elixir MySQL"""
#     store_name = storename
#     path = mysqluri

# class Elixir4MySQLContextTestCase(test_context.ContextTestCase):
#     """Elixir MySQL"""
#     store_name = storename
#     path = mysqluri

class Elixir3PostgreSQLGraphTestCase(test_graph.GraphTestCase):
    """Elixir memory"""
    store_name = storename
    path = postgresqluri

class Elixir3PostgreSQLContextTestCase(test_context.ContextTestCase):
    """Elixir memory"""
    store_name = storename
    path = postgresqluri

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
        testN3Store(self.store_name, self.path)

    def testRegex(self):
        g = self.graph
        g.parse(data=testN3, format="n3")
        try:
            formulaA = BNode()
            formulaB = BNode()
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
