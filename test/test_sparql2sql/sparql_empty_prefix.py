from rdflib.graph import ConjunctiveGraph
import rdflib
from StringIO import StringIO
import unittest

from rdflib import plugin

test_data = """
@prefix foaf:       <http://xmlns.com/foaf/0.1/> .
@prefix rdf:        <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .

_:a  foaf:name       "Alice" .
"""

test_query = """BASE <http://xmlns.com/foaf/0.1/>
SELECT ?name
WHERE {
    ?x :name ?name .
}"""

correct = '"name" : {"type": "literal", "xml:lang" : "None", "value" : "Alice"}'
                
class Query(unittest.TestCase):

    def testQueryPlus(self):
        graph = ConjunctiveGraph()
        graph.parse(StringIO(test_data), format="n3")
        result_json = graph.query(test_query, processor='sparql2sql').serialize(format='json')
        self.failUnless(result_json.find(correct) > 0)

if __name__ == "__main__":
    unittest.main()
