#=======================================================================
from rdflib import ConjunctiveGraph
from rdflib import URIRef
from StringIO import StringIO

#=======================================================================

import rdflib




testRdf = """
    @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
    @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
    @prefix : <tag://example.org,2007/literals-test#> .

    <http://example.org/thing>
        :plain "plain";
        :integer 1;
        :float 1.1e0;
        :decimal 1.1 ; 
        :string "string"^^xsd:string;
        :date "2007-04-28"^^xsd:date;
        :escape "a \\"test\\"";
        rdfs:label "Thing"@en, "Sak"@sv .
"""
graph = ConjunctiveGraph()
graph.load(StringIO(testRdf), format='n3')

PROLOGUE = """
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX t: <tag://example.org,2007/literals-test#>
"""

thing = URIRef("http://example.org/thing")

SPARQL = PROLOGUE+" SELECT ?uri WHERE { ?uri %s . } "
TEST_DATA = [
    ('plain', SPARQL % 't:plain "plain"', [(thing,)]),
    ('integer', SPARQL % 't:integer 1', [(thing,)]),
    ('decimal', SPARQL % 't:decimal 1.1', [(thing,)]),
    ('float', SPARQL % 't:float 1.1e0', [(thing,)]),
    ('langlabel_en', SPARQL % 'rdfs:label "Thing"@en', [(thing,)]),
    ('langlabel_sv', SPARQL % 'rdfs:label "Sak"@sv', [(thing,)]),
    ('string', SPARQL % 't:string "string"^^xsd:string', [(thing,)]),
    ('date', SPARQL % 't:date "2007-04-28"^^xsd:date', [(thing,)]),
    ('escape', SPARQL % 't:escape "a \\"test\\""', [(thing,)])
]

def assert_equal(name, sparql, real, expected):
    assert real == expected, 'Failed test "%s":\n%s\n, expected\n\t%s\nand got\n\t%s\n'\
            % (name, sparql, expected, real)

def test_generator():
    for name, sparql, expected in TEST_DATA:
        res = graph.query(sparql)

        yield assert_equal, name, sparql, list(res), expected


test_generator.sparql = True

#=======================================================================


# if __name__ == '__main__':
#     from sys import argv
#     name, sparql, expected = TEST_DATA[int(argv[1])]
#     res = graph.query(sparql)
#     assert_equal(name, sparql, list(res), expected)


