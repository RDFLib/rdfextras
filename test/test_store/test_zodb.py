try:
    import ZODB
except ImportError:
    from nose.exc import SkipTest
    raise SkipTest("ZODB not installed")

import logging

_logger = logging.getLogger(__name__)

import os
import transaction
from rdflib import RDF, URIRef, ConjunctiveGraph, Graph
import test_graph
from rdflib.graph import GraphValue


class ZODBGraphTestCase(test_graph.GraphTestCase):
    store_name = "ZODB"
    storetest = True
    path = '/var/tmp/zodb_local2.fs'
    url='file:///var/tmp/zodb_local2.fs'
    
    def setUp(self):
        if self.url.endswith('.fs'): 
            from ZODB.FileStorage import FileStorage
            if os.path.exists(self.path):
                os.unlink('/var/tmp/zodb_local2.fs')
                os.unlink('/var/tmp/zodb_local2.fs.index')
                os.unlink('/var/tmp/zodb_local2.fs.tmp')
                os.unlink('/var/tmp/zodb_local2.fs.lock')
            openstr = os.path.abspath(os.path.expanduser(self.url[7:])) 
            fs=FileStorage(openstr) 
        else: 
            from ZEO.ClientStorage import ClientStorage 
            schema,opts = _parse_rfc1738_args(self.url) 
            fs=ClientStorage((opts['host'],int(opts['port']))) 
        zdb=ZODB.DB(fs) 
        conn=zdb.open() 
        root=conn.root() 
        if 'rdflib' not in root: 
            root['rdflib'] = ConjunctiveGraph(self.store_name)
        root['rdflib'].zdb = zdb
        self.graph = self.g = root['rdflib']
        
        self.michel = URIRef(u'michel')
        self.tarek = URIRef(u'tarek')
        self.bob = URIRef(u'bob')
        self.likes = URIRef(u'likes')
        self.hates = URIRef(u'hates')
        self.pizza = URIRef(u'pizza')
        self.cheese = URIRef(u'cheese')
        transaction.commit()
    
    def tearDown(self):
        self.graph.close()
        os.unlink('/var/tmp/zodb_local2.fs')
        os.unlink('/var/tmp/zodb_local2.fs.index')
        os.unlink('/var/tmp/zodb_local2.fs.tmp')
        os.unlink('/var/tmp/zodb_local2.fs.lock')
    
    def addStuff(self):
        tarek = self.tarek
        michel = self.michel
        bob = self.bob
        likes = self.likes
        hates = self.hates
        pizza = self.pizza
        cheese = self.cheese
        
        self.graph.add((tarek, likes, pizza))
        self.graph.add((tarek, likes, cheese))
        self.graph.add((michel, likes, pizza))
        self.graph.add((michel, likes, cheese))
        self.graph.add((bob, likes, cheese))
        self.graph.add((bob, hates, pizza))
        self.graph.add((bob, hates, michel)) # gasp!
        transaction.commit()
    
    def removeStuff(self):
        tarek = self.tarek
        michel = self.michel
        bob = self.bob
        likes = self.likes
        hates = self.hates
        pizza = self.pizza
        cheese = self.cheese
        
        self.graph.remove((tarek, likes, pizza))
        self.graph.remove((tarek, likes, cheese))
        self.graph.remove((michel, likes, pizza))
        self.graph.remove((michel, likes, cheese))
        self.graph.remove((bob, likes, cheese))
        self.graph.remove((bob, hates, pizza))
        self.graph.remove((bob, hates, michel)) # gasp!
    
    def testAdd(self):
        self.addStuff()
    
    def testRemove(self):
        self.addStuff()
        self.removeStuff()
    
    def testTriples(self):
        tarek = self.tarek
        michel = self.michel
        bob = self.bob
        likes = self.likes
        hates = self.hates
        pizza = self.pizza
        cheese = self.cheese
        asserte = self.assertEquals
        triples = self.graph.triples
        Any = None
        
        self.addStuff()
        
        # unbound subjects
        asserte(len(list(triples((Any, likes, pizza)))), 2)
        asserte(len(list(triples((Any, hates, pizza)))), 1)
        asserte(len(list(triples((Any, likes, cheese)))), 3)
        asserte(len(list(triples((Any, hates, cheese)))), 0)
        
        # unbound objects
        asserte(len(list(triples((michel, likes, Any)))), 2)
        asserte(len(list(triples((tarek, likes, Any)))), 2)
        asserte(len(list(triples((bob, hates, Any)))), 2)
        asserte(len(list(triples((bob, likes, Any)))), 1)
        
        # unbound predicates
        asserte(len(list(triples((michel, Any, cheese)))), 1)
        asserte(len(list(triples((tarek, Any, cheese)))), 1)
        asserte(len(list(triples((bob, Any, pizza)))), 1)
        asserte(len(list(triples((bob, Any, michel)))), 1)
        
        # unbound subject, objects
        asserte(len(list(triples((Any, hates, Any)))), 2)
        asserte(len(list(triples((Any, likes, Any)))), 5)
        
        # unbound predicates, objects
        asserte(len(list(triples((michel, Any, Any)))), 2)
        asserte(len(list(triples((bob, Any, Any)))), 3)
        asserte(len(list(triples((tarek, Any, Any)))), 2)
        
        # unbound subjects, predicates
        asserte(len(list(triples((Any, Any, pizza)))), 3)
        asserte(len(list(triples((Any, Any, cheese)))), 3)
        asserte(len(list(triples((Any, Any, michel)))), 1)
        
        # all unbound
        asserte(len(list(triples((Any, Any, Any)))), 7)
        self.removeStuff()
        asserte(len(list(triples((Any, Any, Any)))), 0)
    
    def testStatementNode(self):
        graph = self.graph
        
        from rdflib.term import Statement
        c = URIRef("http://example.org/foo#c")
        r = URIRef("http://example.org/foo#r")
        s = Statement((self.michel, self.likes, self.pizza), c)
        graph.add((s, RDF.value, r))
        self.assertEquals(r, graph.value(s, RDF.value))
        self.assertEquals(s, graph.value(predicate=RDF.value, object=r))
    
    def testGraphValue(self):
        pass
    
    def testZGraphValue(self):
        
        graph = self.graph
        
        alice = URIRef("alice")
        bob = URIRef("bob")
        pizza = URIRef("pizza")
        cheese = URIRef("cheese")
        
        g1 = Graph()
        g1.add((alice, RDF.value, pizza))
        g1.add((bob, RDF.value, cheese))
        g1.add((bob, RDF.value, pizza))
        
        g2 = Graph()
        g2.add((bob, RDF.value, pizza))
        g2.add((bob, RDF.value, cheese))
        g2.add((alice, RDF.value, pizza))
        
        gv1 = GraphValue(store=graph.store, graph=g1)
        gv2 = GraphValue(store=graph.store, graph=g2)
        graph.add((gv1, RDF.value, gv2))
        v = graph.value(gv1)
        # print type(v)
        self.assertEquals(gv2, v)
        # print list(gv2)
        # print gv2.identifier
        # print(len(graph))
        graph.remove((gv1, RDF.value, gv2))
        # print(len(graph))
    
