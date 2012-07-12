try:
    import SPARQLWrapper
except ImportError:
    from nose.exc import SkipTest
    raise SkipTest("SPARQLWrapper not installed")

import logging

# from test_context import ContextTestCase
# from test_graph import GraphTestCase
# from rdflib import BNode, Literal, RDF, URIRef
# import rdflib.term
from rdflib import Graph

_logger = logging.getLogger(__name__)
storetest = True
graph = Graph(store="SPARQL")


def setUp(self):
    graph.open("http://lod.openlinksw.com/sparql/", create=False)
    ns = list(graph.namespaces())
    assert len(ns) > 0, ns


def tearDown(self):
    self.graph.close()

"""
Reported problem with Sesame2 2.6.6:

POST /openrdf-sesame/repositories/test/statements HTTP/1.1
Accept-Encoding: identity
Content-Length: 226
Host: localhost:8080
Accept: application/sparql-results+xml
User-Agent: sparqlwrapper 1.5.0 (http://sparql-wrapper.sourceforge.net/)
Connection: close
Content-Type: application/x-www-form-urlencoded

query=...

POST /openrdf-sesame/repositories/test/statements HTTP/1.1
Accept-Encoding: identity
Content-Length: 227
Host: localhost:8080
Accept: */*
User-Agent: sparqlwrapper 1.5.0 (http://sparql-wrapper.sourceforge.net/)
Connection: close
Content-Type: application/x-www-form-urlencoded

update=...

"""
