try:
    import psycopg2
except ImportError:
    from nose.exc import SkipTest
    raise SkipTest("psycopg2 not installed")

import sys
sys.path.append('..')
from nose.exc import SkipTest
from tempfile import mkdtemp
from tempfile import mkstemp
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
from rdflib import plugin
from rdflib import store
from rdfextras.store.REGEXMatching import REGEXTerm
import test_graph
import test_context
import unittest

# ../configstrings.py holds deployment-specific db params, e.g.
# mysqlconfigString="user=rdflib,password=seekrit,host=localhost,db=test"
# postgresqlconfigString="user=user,password=password,host=host,db=dbname"
# mysqluri="mysql://user:password@host/database"
from configstrings import postgresqlconfigString as configString

plugin.register('PostgreSQL', store.Store,
                'rdfextras.store.PostgreSQL', 
                'PostgreSQL')

class PostgreSQLGraphTestCase(test_graph.GraphTestCase):
    store_name = "PostgreSQL"
    storetest = True
    path = configString
    create = True

    def testStatementNode(self):
        raise SkipTest("Known issue.")

class PostgreSQLContextTestCase(test_context.ContextTestCase):
    store_name = "PostgreSQL"
    storetest = True
    path = configString
    create = True

    def testLenInMultipleContexts(self):
        raise SkipTest("Known issue.")

    def testConjunction(self):
        raise SkipTest("Known issue.")

class PostgreSQLStoreTests(unittest.TestCase):
    storetest = True
    store_name = "PostgreSQL"
    path = configString
    create = True

    def setUp(self):
        self.graph = Graph(store=self.store_name)
        if isinstance(self.path, type(None)):
            if self.store_name == "SQLite":
                self.path = mkstemp(prefix='test',dir='/tmp')
            else:
                self.path = mkdtemp(prefix='test',dir='/tmp')
            self.graph.store.identifier = self.identifier
        self.graph.open(self.path, create=self.create)

    def tearDown(self):
        # self.graph.destroy(self.path)
        self.graph.close()
        import os
        if hasattr(self,'path') and self.path is not None:
            if os.path.exists(self.path):
                if os.path.isdir(self.path):
                    for f in os.listdir(self.path): os.unlink(self.path+'/'+f)
                    os.rmdir(self.path)
                elif len(self.path.split(':')) == 1:
                    os.unlink(self.path)
                else:
                    os.remove(self.path)

    def test_PostgreSQL_testN3_store(self):
        testN3Store('PostgreSQL',configString)

    def testRegex(self):
        raise SkipTest("Known issue.")
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
            g.store.destroy(configString)
            raise

# To enable profiling data, use nose's built-in hookup with hotshot:
# nosetests --with-profile --profile-stats-file stats.pf test/test_store/test_mysql
# Also see Tarek Ziade's gprof2dot explorations:
# http://tarekziade.wordpress.com/2008/08/25/visual-profiling-with-nose-and-gprof2dot/
