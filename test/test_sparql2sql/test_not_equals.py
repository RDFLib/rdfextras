from rdflib import RDF, ConjunctiveGraph
import rdflib
# from rdflib import plugin
from rdflib.parser import StringInputSource

# import sys
# from pprint import pprint

def testSPARQLNotEquals():
    # NS = u"http://example.org/"
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
                           processor="sparql2sql",
                           initNs={'rdf': RDF.uri},
                           DEBUG=False)
    for row in rt:        
        #item = row[0]
        item = row
        assert item == rdflib.term.URIRef("http://example.org/bar"), "unexpected item of '%s'" % repr(item)

if __name__ == '__main__':
    testSPARQLNotEquals()
