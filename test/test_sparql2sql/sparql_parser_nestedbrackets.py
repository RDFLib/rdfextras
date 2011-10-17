import unittest
try:
    from rdfextras.sparql2sql.parser import parse
except ImportError:
    from rdflib.sparql.parser import parse

# second query from here:
# http://www.w3.org/TR/rdf-sparql-query/#GroupPatterns

query = """
PREFIX foaf:    <http://xmlns.com/foaf/0.1/>
SELECT ?name ?mbox
WHERE  { { ?x foaf:name ?name . }
         { ?x foaf:mbox ?mbox . }
       }
"""

correct = """{ [<SPARQLParser.GraphPattern: [[?x [foaf:name([u'?name'])], ?x [foaf:mbox([u'?mbox'])]]]>] }"""
correct = """{ [( { [[x [u'foaf:name': [?name]]]] } '.'?  ), ( { [[x [u'foaf:mbox': [?mbox]]]] } '.'?  )] }"""

class TestOrderBy(unittest.TestCase):

    def testOrderBy(self):
        p = parse(query)
        tmp = p.query.whereClause.parsedGraphPattern
        assert str(tmp) == correct


if __name__ == "__main__":
    unittest.main()
