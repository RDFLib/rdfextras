from rdflib.graph import ConjunctiveGraph
from StringIO import StringIO
import unittest

import rdflib
from rdflib import Literal



test_data = """
@prefix foaf:       <http://xmlns.com/foaf/0.1/> .
@prefix rdf:        <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

_:a  foaf:name       "Alice" .
_:a  foaf:surName      "Carol" . 
_:a  foaf:lastName      "Carol" . 

_:b  foaf:name       "Alice" . 

_:c  foaf:surName "Emerson" .

_:d  foaf:surName "Emerson" .
"""

test_query_literal = """PREFIX foaf:<http://xmlns.com/foaf/0.1/>
SELECT DISTINCT ?x
WHERE {
    ?y foaf:name ?x .
}"""

test_query_resource = """PREFIX foaf:<http://xmlns.com/foaf/0.1/>
SELECT DISTINCT ?x
WHERE {
    ?x ?p 'Carol' .
}"""

test_query_order = """PREFIX foaf:<http://xmlns.com/foaf/0.1/>
SELECT DISTINCT ?name
WHERE {
    ?x foaf:surName ?name . 
} ORDER by ?name
"""

                
class Query(unittest.TestCase):

    def setUp(self):
        self.graph = ConjunctiveGraph()
        self.graph.parse(StringIO(test_data), format="n3")


    def testQuery1(self):
        r=list(self.graph.query(test_query_literal))
        print r
        self.assertEqual(len(r), 1)

    def testQuery2(self):
        r=list(self.graph.query(test_query_resource))
        print r
        self.assertEqual(len(r), 1)


    def testQuery3(self):
        r=list(self.graph.query(test_query_order))
        print r
        self.assertEqual(list(r), [(Literal("Carol"), ), (Literal("Emerson"),)])

if __name__ == "__main__":
    unittest.main()
