import unittest
from rdflib import RDF
from rdflib.graph import ConjunctiveGraph

testgraph = """\
@prefix    : <http://example.org/> .
@prefix rdf: <%s> .
:foo rdf:value 1 .
:bar rdf:value -2 .""" % RDF.uri

testquery = """\
SELECT ?node 
WHERE {
    ?node rdf:value ?val .
    FILTER (?val < -1) 
}"""

class TestIssue11(unittest.TestCase):
    debug = False
    sparql = True
    
    def setUp(self):
        NS = u"http://example.org/"
        self.graph = ConjunctiveGraph()
        self.graph.parse(data=testgraph, format="n3", publicID=NS)

    def testSPARQL_lessthan_filter_using_negative_integer(self):
        rt = self.graph.query(testquery, initNs={'rdf':RDF }, DEBUG=True)
        for row in rt:
            assert str(row[0]) == "http://example.org/bar"

if __name__ == '__main__':
    TestIssue11.testSPARQL_lessthan_filter_using_negative_integer()
