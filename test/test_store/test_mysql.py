try:
    import MySQLdb
except ImportError:
    import warnings
    warnings.warn("MySQLdb is not installed")
    __test__=False
import sys
import test_graph
import test_context
import unittest
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
sys.path.append('..')
# ../configstrings.py holds deployment-specific db params, e.g.
# mysqlconfigString="user=rdflib,password=seekrit,host=localhost,db=test"
# postgresqlconfigString="user=user,password=password,host=host,db=dbname"
# mysqluri="mysql://user:password@host/database"

from configstrings import mysqlconfigString as configString

plugin.register('MySQL', store.Store,
                'rdfextras.store.MySQL', 
                'MySQL')

class MySQLGraphTestCase(test_graph.GraphTestCase):
    store_name = "MySQL"
    storetest = True
    path = configString
    create = True

class MySQLContextTestCase(test_context.ContextTestCase):
    store_name = "MySQL"
    storetest = True
    path = configString
    create = True

class MySQLStoreTests(unittest.TestCase):
    storetest = True
    store_name = "MySQL"
    path = configString
    create = True
    identifier = "rdflib_test"

    def setUp(self):
        self.graph = Graph(store=self.store_name)
        if isinstance(self.path, type(None)):
            if self.store_name in ["SQLite"]: 
                self.path = mkstemp(prefix='test',dir='/var/tmp')
            else:
                self.path = mkdtemp(prefix='test',dir='/var/tmp')
	        self.graph.store.identifier = self.identifier
	    # Remove the db detritus that remains after a test run
	    # has been interrupted with ^C.
        self.graph.destroy(self.path)
        self.graph.open(self.path, create=self.create)

    def tearDown(self):
        self.graph.destroy(self.path)
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
            # g.store.destroy(configString)
            raise

# To enable profiling data, use nose's built-in hookup with hotshot:
# nosetests --with-profile --profile-stats-file stats.pf test/test_store/test_mysql
# Also see Tarek Ziade's gprof2dot explorations:
# http://tarekziade.wordpress.com/2008/08/25/visual-profiling-with-nose-and-gprof2dot/

