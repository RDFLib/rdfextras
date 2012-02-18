from rdflib.graph import ConjunctiveGraph
from rdflib.term import URIRef
from rdflib.namespace import RDFS
from StringIO import StringIO
import unittest

import rdflib



testContent = """
    @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
    <http://example.org/doc/1> rdfs:label "Document 1","Document 2".
    <http://example.org/doc/2> rdfs:label "Document 1"."""
    

doc1 = URIRef("http://example.org/doc/1")
doc2 = URIRef("http://example.org/doc/2")

QUERY = u"""
SELECT ?X
WHERE { 
    ?X ?label "Document 1".
    OPTIONAL { ?X ?label ?otherLabel.  FILTER ( ?otherLabel != "Document 1" ) } 
    FILTER (!bound(?otherLabel)) }"""

class TestSparqlOPT_FILTER(unittest.TestCase):
    def setUp(self):
        self.graph = ConjunctiveGraph()
        self.graph.load(StringIO(testContent), format='n3')
    def test_OPT_FILTER(self):
        results = self.graph.query(QUERY,
                                   DEBUG=False,
                                   initBindings={'?label':RDFS.label})
        print results.vars
        self.failUnless(list(results) == [(doc2,)],
                "expecting : %s, got %s"%(repr([(doc2,)]), repr(list(results))))

if __name__ == "__main__":
    unittest.main()
