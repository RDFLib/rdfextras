from rdflib.graph import ConjunctiveGraph
from StringIO import StringIO
import unittest

import rdflib



test_data = """
@prefix foaf:       <http://xmlns.com/foaf/0.1/> .
@prefix rdf:        <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .

_:a  foaf:name       "Alice" .
"""

test_query = """PREFIX :<http://xmlns.com/foaf/0.1/>
SELECT ?name
WHERE {
    ?x :name ?name .
}"""

correct = '"name" : {"type": "literal", "xml:lang" : "None", "value" : "Alice"}'
                
class Query(unittest.TestCase):

    def testQueryPlus(self):
        graph = ConjunctiveGraph()
        graph.parse(StringIO(test_data), format="n3")
        results = graph.query(test_query)
        
        self.failUnless(results.bindings[0]["name"]=="Alice")

if __name__ == "__main__":
    unittest.main()
