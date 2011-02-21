from rdflib import URIRef, RDF, ConjunctiveGraph

from rdflib.parser import StringInputSource


import rdflib
rdflib.plugin.register('sparql', rdflib.query.Processor,
                       'rdfextras.sparql.processor', 'Processor')
rdflib.plugin.register('sparql', rdflib.query.Result,
                       'rdfextras.sparql.query', 'SPARQLQueryResult')


def testSPARQLNotEquals():
    NS = u"http://example.org/"
    graph = ConjunctiveGraph()
    graph.parse(StringInputSource("""
       @prefix    : <http://example.org/> .
       @prefix rdf: <%s> .
       :foo rdf:value 1.
       :bar rdf:value 2.""" % RDF.uri), format="n3")
    rt = graph.query("""SELECT ?node 
                        WHERE {
                                ?node rdf:value ?val.
                                FILTER (?val != 1)
                               }""",
                           initNs={'rdf': RDF.uri},
                           DEBUG=False)
    for row in rt:        
        #item = row[0]
        item = row
        assert item == URIRef("http://example.org/bar"), "unexpected item of '%s'" % repr(item)

if __name__ == '__main__':
    testSPARQLNotEquals()
