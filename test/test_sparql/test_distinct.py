from rdflib.graph import ConjunctiveGraph
from StringIO import StringIO
import unittest

import rdflib
rdflib.plugin.register('sparql', rdflib.query.Processor,
                       'rdfextras.sparql.processor', 'Processor')
rdflib.plugin.register('sparql', rdflib.query.Result,
                       'rdfextras.sparql.query', 'SPARQLQueryResult')


test_data = """
@prefix foaf:       <http://xmlns.com/foaf/0.1/> .
@prefix rdf:        <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

_:a  foaf:name       "Alice" .
_:a  foaf:surName      "Carol" . 
_:a  foaf:lastName      "Carol" . 

_:b  foaf:name       "Alice" . 
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


                
class Query(unittest.TestCase):

    def testQuery1(self):
        graph = ConjunctiveGraph()
        graph.parse(StringIO(test_data), format="n3")
        r=list(graph.query(test_query_literal))
        print r
        self.assertEqual(len(r), 1)

    def testQuery2(self):
        graph = ConjunctiveGraph()
        graph.parse(StringIO(test_data), format="n3")
        r=list(graph.query(test_query_resource))
        print r
        self.assertEqual(len(r), 1)


if __name__ == "__main__":
    unittest.main()
