import unittest

from rdflib import Graph
from rdflib import Literal
from rdflib import URIRef
from rdflib.store import NodePickler


canned_result = u"""\
<?xml version="1.0" encoding="UTF-8"?>
<rdf:RDF
   xmlns:ns1="http://example.org/foo#"
   xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
>
  <rdf:Description rdf:about="http://example.org/foo#bar1">
    <ns1:bar2 rdf:resource="http://example.org/foo#bar3"/>
  </rdf:Description>
</rdf:RDF>
""".encode('utf-8')

class UtilTestCase(unittest.TestCase):
    storetest = True
    
    def test_to_bits_from_bits_round_trip(self):
        np = NodePickler()
        
        a = Literal(u'''A test with a \\n (backslash n), "\u00a9" , and newline \n and a second line.
''')
        b = np.loads(np.dumps(a))
        self.assertEquals(a, b)
    
    def test_default_namespaces_method(self):
        g = Graph()
        g.add((URIRef("http://example.org/foo#bar1"),
               URIRef("http://example.org/foo#bar2"),
               URIRef("http://example.org/foo#bar3")))
        self.assertEqual(g.serialize(), canned_result)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
