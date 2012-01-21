try:
    import SPARQLWrapper
except ImportError:
    from nose.exc import SkipTest
    raise SkipTest("SPARQLWrapper not installed")

import logging

_logger = logging.getLogger(__name__)

from test_context import ContextTestCase
from test_graph import GraphTestCase
from rdflib import URIRef, BNode, Literal, RDF, Graph
import rdflib.term
storetest = True

graph = Graph(store="SPARQL")

def setUp(self):
    graph.open("http://lod.openlinksw.com/sparql/", create=False)
    ns = list(graph.namespaces())
    assert len(ns) > 0, ns

def tearDown(self):
    self.graph.close()
