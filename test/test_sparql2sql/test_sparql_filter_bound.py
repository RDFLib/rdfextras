from rdflib import Literal, BNode, Namespace #, URIRef
from rdflib.graph import ConjunctiveGraph
import unittest
DC = Namespace(u"http://purl.org/dc/elements/1.1/")
FOAF = Namespace(u"http://xmlns.com/foaf/0.1/")

graph = ConjunctiveGraph()
s = BNode()
graph.add((s, FOAF['givenName'], Literal('Alice')))
b = BNode()
graph.add((b, FOAF['givenName'], Literal('Bob')))
graph.add((b, DC['date'], Literal("2005-04-04T04:04:04Z")))

class TestSparqlFilterBound(unittest.TestCase):
    debug=False
    def test_bound(self):
        res = list(graph.query("""PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        PREFIX dc:  <http://purl.org/dc/elements/1.1/>
        PREFIX xsd:  <http://www.w3.org/2001/XMLSchema#>
        SELECT ?name
        WHERE { ?x foaf:givenName  ?name .
                        OPTIONAL { ?x dc:date ?date } .
                        FILTER ( bound(?date) ) }""",
        processor="sparql2sql",
        DEBUG=self.debug))
        expected = [Literal('Bob', lang=None, datatype=None)]
        assert res == expected, "Expected %s but got %s" % (expected, res)

if __name__ == '__main__':
    TestSparqlFilterBound.test_bound()

