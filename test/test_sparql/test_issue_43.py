import unittest
from rdflib import RDF
from rdflib.graph import ConjunctiveGraph

testgraph = """\
@prefix rdf: <%s> .
<http://example.org/a> rdf:value "a" .""" % RDF.uri

testquery = """\
SELECT ?node1 ?val1
WHERE {
    ?node1 rdf:value ?val1 .
    FILTER (
        ?val1="never match0" || ?val1="never match1" && ?val1="never match2"
    )
}
"""

disjunctionquery = """\
SELECT ?node1 ?val1
WHERE {
    ?node1 rdf:value ?val1 .
    FILTER (?val1="never match" && ?val1="never match")
}
"""

conjunctionquery = """\
SELECT ?node1 ?val1
WHERE {
    ?node1 rdf:value ?val1 .
    FILTER (?val1="never match" || ?val1="never match")
}
"""


class TestIssue43(unittest.TestCase):
    debug = False
    sparql = True
    known_issue = True

    def setUp(self):
        NS = u"http://example.org/"
        self.graph = ConjunctiveGraph()
        self.graph.parse(data=testgraph, format="n3", publicID=NS)

    def testSPARQL_disjunction(self):
        rt = self.graph.query(
            disjunctionquery, initNs={'rdf': RDF}, DEBUG=False)
        self.assertEquals(len(list(rt)), 0)

    def testSPARQL_conjunction(self):
        rt = self.graph.query(
            conjunctionquery, initNs={'rdf': RDF}, DEBUG=False)
        self.assertEquals(len(list(rt)), 0)

    def testSPARQL_disjunction_with_conjunction(self):
        rt = self.graph.query(
            testquery, initNs={'rdf': RDF}, DEBUG=True)
        self.assertEquals(len(list(rt)), 0, list(rt))

if __name__ == '__main__':
    TestIssue43.testSPARQL_disjunction_with_conjunction()


"""
<ConditionalExpressionList: [
    (val1 = never match),
    <RelationalExpressionList: [(val1 = never match), (val1 = never match)]>]>
    <class 'rdfextras.sparql.components.ParsedConditionalAndExpressionList'>
    sparql-p operator(s):
        lambda i: operators.eq("?val1",rdflib.term.Literal(u'never match'))(i)
            or operators.eq("?val1",rdflib.term.Literal(u'never match'))
            and operators.eq("?val1",rdflib.term.Literal(u'never match'))
"""
