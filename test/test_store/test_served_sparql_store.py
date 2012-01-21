import unittest
import threading
import rdflib
import rdfextras
import rdfextras.web.endpoint
import rdfextras.store.SPARQL

rdflib.plugin.register('sparql', rdflib.query.Processor,
                       'rdfextras.sparql.processor', 'Processor')
rdflib.plugin.register('sparql', rdflib.query.Result,
                       'rdfextras.sparql.query', 'SPARQLQueryResult')
rdflib.plugin.register('xml', rdflib.query.ResultParser, 
                           'rdfextras.sparql.results.xmlresults','XMLResultParser')
rdflib.plugin.register('xml', rdflib.query.ResultSerializer, 
                           'rdfextras.sparql.results.xmlresults','XMLResultSerializer')


class TestSPARQLStore(unittest.TestCase): 

    def testSPARQLStore(self): 
        g=rdflib.Graph()

        data="""<http://example.org/book/book1> <http://purl.org/dc/elements/1.1/title> "SPARQL Tutorial" .
<http://example.org/book/b\xc3\xb6\xc3\xb6k8> <http://purl.org/dc/elements/1.1/title> "M\xc3\xb6se bite can be very nasty."@se .
 
"""

        g.parse(data=data, format='n3')

        # # create our own SPARQL endpoint

        app=rdfextras.web.endpoint.get(g)
        t=threading.Thread(target=lambda : app.run(port=57234))
        t.daemon=True
        t.start()
        import time
        time.sleep(1)
        store=rdfextras.store.SPARQL.SPARQLStore("http://localhost:57234/sparql")
        g2=rdflib.Graph(store)
        b=rdflib.URIRef("http://example.org/book/book1")
        b2=rdflib.URIRef("http://example.org/book/b\xc3\xb6\xc3\xb6k8")
        DCtitle=rdflib.URIRef("http://purl.org/dc/elements/1.1/title")
        self.assertEqual(len(list(g2.triples((b,None,None)))), 1)
        self.assertEqual(list(g2.objects(b,DCtitle))[0], rdflib.Literal("SPARQL Tutorial"))

        self.assertEqual(list(g2.objects(b2,DCtitle))[0], list(g.objects(b2,DCtitle))[0])
        


        
        

