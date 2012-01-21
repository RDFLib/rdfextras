from rdflib import ConjunctiveGraph, URIRef #, Literal
from StringIO import StringIO
import unittest

testContent = """
@prefix foaf:  <http://xmlns.com/foaf/0.1/> .
<http://purl.org/net/chimezie/foaf#chime> 
  foaf:name   "Chime";
  a foaf:Person.
<http://eikeon.com/> foaf:knows 
  <http://purl.org/net/chimezie/foaf#chime>,<http://www.ivan-herman.net/>.
<http://www.ivan-herman.net/> foaf:name "Ivan"."""
    
doc1 = URIRef("http://eikeon.com/")

QUERY = u"""
PREFIX foaf:   <http://xmlns.com/foaf/0.1/>
SELECT ?X
WHERE { 
    ?P a foaf:Person .
    ?X foaf:knows ?P .
    OPTIONAL { 
      ?X foaf:knows ?OP .
      ?OP foaf:name "Judas" } 
    FILTER (!bound(?OP)) }"""

class TestSparqlOPT_FILTER2(unittest.TestCase):
    debug = False
    def setUp(self):
        self.graph = ConjunctiveGraph()
        self.graph.load(StringIO(testContent), format='n3')
    def test_OPT_FILTER(self):
        results = self.graph.query(QUERY,
                                   processor="sparql2sql", 
                                   DEBUG=self.debug) #.serialize(format='python')
        results = list(results)
        self.failUnless(
            results == [doc1],
            "expecting : %s .  Got: %s"%([doc1],repr(results)))

if __name__ == "__main__":
    unittest.main()
