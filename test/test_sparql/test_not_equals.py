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
        item = row[0]
        assert item == URIRef("http://example.org/bar"), "unexpected item of '%s'" % repr(item)


def testSPARQLNotEqualsNegative():

    """
    This is rdfextras issue 9
    """

    NS = u"http://example.org/"
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
        item = row[0]
        assert item == URIRef("http://example.org/bar"), "unexpected item of '%s'" % repr(item)

testSPARQLNotEqualsNegative.known_issue = True
"""
ERROR: test_describe (test_describe.TestDescribe)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "test/test_sparql/test_describe.py", line 19, in test_describe
    res=g.query("DESCRIBE <urn:a>")
  File "rdflib/graph.py", line 804, in query
    return result(processor.query(query_object, initBindings, initNs, **kwargs))
  File "rdfextras/sparql/processor.py", line 45, in query
    extensionFunctions=extensionFunctions)
  File "rdfextras/sparql/algebra.py", line 322, in TopEvaluate
    expr = reduce(ReduceToAlgebra,query.query.whereClause.parsedGraphPattern.graphPatterns,
  AttributeError: 'NoneType' object has no attribute 'parsedGraphPattern'
"""

if __name__ == '__main__':
    testSPARQLNotEquals()
