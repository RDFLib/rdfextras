from rdflib.graph import ConjunctiveGraph
from StringIO import StringIO
import unittest

import rdflib



test_data = """
@prefix : <http://ex.org> .
@prefix foaf:       <http://xmlns.com/foaf/0.1/> .
@prefix rdf:        <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

:a  foaf:name "Alice" .
:b  foaf:name "Alice"@no . 
:c  foaf:name "Alice"@fr-BE . 

"""

test_query1 = """PREFIX foaf:<http://xmlns.com/foaf/0.1/>
PREFIX : <http://ex.org>
SELECT ?x
WHERE {
 :a foaf:name ?x . 
FILTER (lang(?x)="")
}"""


test_query2 = """PREFIX foaf:<http://xmlns.com/foaf/0.1/>
PREFIX : <http://ex.org>
SELECT ?x
WHERE {
 :b foaf:name ?x . 
FILTER (lang(?x)="no")
}"""

test_query3 = """PREFIX foaf:<http://xmlns.com/foaf/0.1/>
PREFIX : <http://ex.org>
SELECT ?x
WHERE {
 :c foaf:name ?x . 
FILTER (langMatches(lang(?x),"FR"))
}"""

test_query4 = """PREFIX foaf:<http://xmlns.com/foaf/0.1/>
PREFIX : <http://ex.org>
SELECT ?x
WHERE {
 :c foaf:name ?x . 
FILTER (langMatches(lang(?x),"*"))
}"""

test_query5 = """PREFIX foaf:<http://xmlns.com/foaf/0.1/>
PREFIX : <http://ex.org>
SELECT ?x
WHERE {
 :c foaf:name ?x . 
FILTER (langMatches(lang(?x),"NO"))
}"""

test_queries=[ test_query1, test_query2, test_query3, test_query4 ]
                
class Query(unittest.TestCase):

    def setUp(self):
        self.graph = ConjunctiveGraph()
        self.graph.parse(StringIO(test_data), format="n3")
    
    def test1(self):
        r=list(self.graph.query(test_query1))
        self.assertEqual(len(r), 1)

    def test2(self):
        r=list(self.graph.query(test_query2))
        self.assertEqual(len(r), 1)

    def test3(self):
        r=list(self.graph.query(test_query3))
        self.assertEqual(len(r), 1)

    def test4(self):
        r=list(self.graph.query(test_query4))
        self.assertEqual(len(r), 1)

    def test5(self):
        r=list(self.graph.query(test_query5))
        self.assertEqual(len(r), 0)


if __name__ == "__main__":
    unittest.main()
