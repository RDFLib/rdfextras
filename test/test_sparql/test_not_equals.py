from rdflib import URIRef, RDF, ConjunctiveGraph

from rdflib.parser import StringInputSource
from rdflib.py3compat import b

import rdflib



def testSPARQLNotEquals():
    NS = u"http://example.org/"
    graph = ConjunctiveGraph()
    graph.parse(StringInputSource(b("""
       @prefix    : <http://example.org/> .
       @prefix rdf: <%s> .
       :foo rdf:value 1.
       :bar rdf:value 2.""" % RDF.uri)), format="n3")
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
======================================================================
ERROR: This is rdfextras issue 9
----------------------------------------------------------------------
Traceback (most recent call last):
  File "test/test_sparql/test_not_equals.py", line 52, in testSPARQLNotEqualsNegative
    DEBUG=False)
  File "rdflib/rdflib/graph.py", line 804, in query
    return result(processor.query(query_object, initBindings, initNs, **kwargs))
  File "rdfextras/rdfextras/sparql/processor.py", line 45, in query
    extensionFunctions=extensionFunctions)
  File "rdfextras/rdfextras/sparql/algebra.py", line 349, in TopEvaluate
    None)
  File "rdfextras/rdfextras/sparql/algebra.py", line 197, in ReduceToAlgebra
    prolog))
  File "rdfextras/rdfextras/sparql/evaluate.py", line 389, in createSPARQLPConstraint
    return eval(rt)
  File "<string>", line 1, in <module>
TypeError: bad operand type for unary -: 'Literal'
"""

if __name__ == '__main__':
    testSPARQLNotEquals()
