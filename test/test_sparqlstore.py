import logging
import unittest
_logger = logging.getLogger(__name__)

# from test_context import ContextTestCase
# from test_graph import GraphTestCase
from rdflib import Graph, URIRef
from rdflib import plugin, store

plugin.register(
        'SPARQL', store.Store,
        'rdfextras.store.SPARQL', 'SPARQLStore')

class SPARQLStoreTestCase(unittest.TestCase):
    store_name = 'SPARQL'
    path = "http://dbpedia.org/sparql"
    storetest = True
    create = False

    def setUp(self):
        self.graph = Graph(store="SPARQL")
        self.graph.open(self.path, create=self.create)
        self.graph.store.baseURI = self.path
        ns = list(self.graph.namespaces())
        assert len(ns) > 0, ns

    def tearDown(self):
        self.graph.close()

    def test_Query(self):
        query = "select distinct ?Concept where {[] a ?Concept} LIMIT 1"
        res = self.graph.query(query, initNs={})
        for i in res.serialize(format="python"):
            assert type(i) == URIRef, i.n3()

from nose import SkipTest
import urllib2
try:
    assert len(urllib2.urlopen("http://dbpedia.org/sparql").read()) > 0
except:
    raise SkipTest("No HTTP connection.")

