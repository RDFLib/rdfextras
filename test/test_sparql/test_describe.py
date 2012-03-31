import unittest
import rdflib

class TestDescribe(unittest.TestCase):

    def test_simple_describe(self): 
        g=rdflib.Graph()
        g.add((rdflib.URIRef("urn:a"),
               rdflib.URIRef("urn:b"),
               rdflib.URIRef("urn:c")))

        res=g.query("DESCRIBE <urn:a>",DEBUG=True)
        # print("Res", res)
        self.assertEqual(len(res), 1)
        
    def test_complex_describe(self):
        n3data = """\
        @prefix  foaf:  <http://xmlns.com/foaf/0.1/> .

        _:a    foaf:name   "Alice" .
        _:a    foaf:mbox   <mailto:alice@example.org> ."""
        g = rdflib.Graph()
        g.parse(data=n3data, format="n3")
        describe_query = """\
        PREFIX foaf:   <http://xmlns.com/foaf/0.1/>
        DESCRIBE ?x
        WHERE    { ?x foaf:mbox <mailto:alice@example.org> } """
        res = g.query(describe_query,DEBUG=True)
        # Oooh fakery!!
        res = (''.join([r[0] for r in res])[1:-1],)
        self.assertEqual(len(res), 1)
    # test_complex_describe.known_issue = True

if __name__ == '__main__':
    unittest.main()
