from rdflib import RDF, ConjunctiveGraph
import unittest

testgraph = """\
@prefix    : <http://example.org/> .
@prefix rdf: <%s> .
:foo rdf:value 1.
:bar rdf:value 2.""" % RDF.uri

testquery = """\
SELECT ?node 
WHERE {
    ?node rdf:value ?val.
    FILTER (?val != 1)
}"""

class TestSPARQLFilters(unittest.TestCase):
    debug = False
    sparql = True
    
    def setUp(self):
        NS = u"http://example.org/"
        self.graph = ConjunctiveGraph()
        self.graph.parse(data=testgraph, format="n3", publicID=NS)

    def testSPARQLNotEquals(self):
        rt = self.graph.query(testquery, initNs={'rdf': RDF.uri}, DEBUG=False)
        for row in rt:
            assert str(row[0]) == "http://example.org/bar" #, "unexpected item of '%s'" % repr(row[0])

if __name__ == '__main__':
    TestSPARQLFilters.testSPARQLNotEquals()
