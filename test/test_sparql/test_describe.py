import unittest

import rdflib

rdflib.plugin.register('sparql', rdflib.query.Processor,
                       'rdfextras.sparql.processor', 'Processor')
rdflib.plugin.register('sparql', rdflib.query.Result,
                       'rdfextras.sparql.query', 'SPARQLQueryResult')


class TestDescribe(unittest.TestCase):

    def test_describe(self): 
        g=rdflib.Graph()
        g.add((rdflib.URIRef("urn:a"),
               rdflib.URIRef("urn:b"),
               rdflib.URIRef("urn:c")))

        res=g.query("DESCRIBE <urn:a>")
        
        self.assertEqual(len(res), 1)
        
        

if __name__ == '__main__':
    unittest.main()
