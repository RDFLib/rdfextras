import rdflib
from rdflib import RDF
from rdflib import URIRef
from rdflib.graph import ConjunctiveGraph
from rdflib.parser import StringInputSource

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
        item = row
        assert item == rdflib.term.URIRef("http://example.org/bar"), "unexpected item of '%s'" % repr(item)

def testSPARQLNotEqualsNegative():

    """
    This is rdfextras issue 9
    """

    # NS = u"http://example.org/"
    graph = ConjunctiveGraph()
    graph.parse(StringInputSource("""
       @prefix    : <http://example.org/> .
       @prefix rdf: <%s> .
       :foo rdf:value 1.
       :bar rdf:value -2.""" % RDF.uri), format="n3")
    rt = graph.query("""SELECT ?node 
                        WHERE {
                                ?node rdf:value ?val.
                                FILTER (?val < -1)
                               }""",
                           initNs={'rdf': RDF.uri},
                           DEBUG=False)
    for row in rt:        
        item = row
        assert item == URIRef("http://example.org/bar"), "unexpected item of '%s'" % repr(item)

if __name__ == '__main__':
    testSPARQLNotEquals()
