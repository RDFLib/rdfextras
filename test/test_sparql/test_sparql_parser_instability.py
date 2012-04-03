import unittest
from pyparsing import ParseException
BAD_SPARQL=\
"""
BASE <tag:chimezie@ogbuji.net,2007:exampleNS>.
SELECT ?s
WHERE { ?s ?p ?o }"""

class TestBadSPARQL(unittest.TestCase):

  def test_bad_sparql(self):
      from rdflib import Graph
      g = Graph()
      self.assertRaises(ParseException, g.query, BAD_SPARQL)

if __name__ == '__main__':
    TestBadSPARQL.test_bad_sparql()
