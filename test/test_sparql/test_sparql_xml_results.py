import sys
from nose.exc import SkipTest
if sys.platform.startswith('java'):
    raise SkipTest("Skipped failing test in Jython")
if sys.version_info[:2] < (2, 6):
    raise SkipTest("Skipped, known XML namespace issue with Python < 2.6")

from rdflib.graph import ConjunctiveGraph
from rdflib.py3compat import b
import re
import unittest


test_data = """
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

<http://example.org/word>
    rdfs:label "Word"@en;
    rdf:value 1;
    rdfs:seeAlso [] .

"""

PROLOGUE = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl:  <http://www.w3.org/2002/07/owl#>
"""

query = PROLOGUE+"""
SELECT ?s ?o WHERE { ?s ?p ?o . }
"""

expected_fragments = [
    #u"""<sparql:sparql xmlns="http://www.w3.org/2005/sparql-results#"><sparql:head>""",

    b("</sparql:head><sparql:results>"),

    b('<sparql:binding name="s"><sparql:uri>http://example.org/word</sparql:uri></sparql:binding>'),

    b('<sparql:binding name="o"><sparql:bnode>'),

    b('<sparql:binding name="o"><sparql:literal datatype="http://www.w3.org/2001/XMLSchema#integer">1</sparql:literal></sparql:binding>'),

    b('<sparql:result><sparql:binding name="s"><sparql:uri>http://example.org/word</sparql:uri>'
      '</sparql:binding><sparql:binding name="o"><sparql:literal xml:lang="en">Word</sparql:literal>'
      '</sparql:binding></sparql:result>')
]


# TODO:
#   - better canonicalization of results to compare with (4Suite-XML has support for this)
#   - test expected 'variable'-elems in head


class TestSparqlXmlResults(unittest.TestCase):

    sparql = True

    def setUp(self):
        self.graph = ConjunctiveGraph()
        self.graph.parse(data=test_data, format="n3")

    def testSimple(self):
        self._query_result_contains(query, expected_fragments)

    def _query_result_contains(self, query, fragments):
        results = self.graph.query(query)
        result_xml = results.serialize(format='xml')
        result_xml = normalize(result_xml) # TODO: poor mans c14n..
        # print result_xml
        for frag in fragments:
            # print(frag, result_xml)
            self.failUnless(frag in result_xml)


def normalize(s, exp=re.compile(b(r'\s+'), re.MULTILINE)):
    return exp.sub(b(' '), s)


if __name__ == "__main__":
    unittest.main()

