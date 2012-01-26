from rdflib.graph import ConjunctiveGraph
from rdflib.term import Literal
from StringIO import StringIO
import unittest

import rdflib



test_data = """
@prefix foaf:       <http://xmlns.com/foaf/0.1/> .
@prefix rdf:        <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .

<http://example.org/alice> a foaf:Person;
    foaf:name "Alice";
    foaf:knows <http://example.org/bob> ."""

test_query = """
BASE <http://xmlns.com/foaf/0.1/>
SELECT ?name
WHERE { [ a :Person ; :name ?name ] }"""

class TestSparqlJsonResults(unittest.TestCase):

    sparql = True

    def setUp(self):
        self.graph = ConjunctiveGraph()
        self.graph.parse(StringIO(test_data), format="n3")

    def test_base_ref(self):
        rt=list(self.graph.query(test_query))
        self.failUnless(rt[0][0] == Literal("Alice"),"Expected:\n 'Alice' \nGot:\n %s" % rt)

if __name__ == "__main__":
    unittest.main()

