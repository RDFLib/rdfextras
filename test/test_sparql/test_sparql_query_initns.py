import unittest
from rdflib import OWL, RDF, Graph, Namespace
import rdflib

xmldata = """\
<?xml version="1.0"?>
<!DOCTYPE rdf:RDF [
    <!ENTITY i "http://bug.rdflib/i.owl#" >
    <!ENTITY owl "http://www.w3.org/2002/07/owl#" >
    <!ENTITY xsd "http://www.w3.org/2001/XMLSchema#" >
    <!ENTITY rdfs "http://www.w3.org/2000/01/rdf-schema#" >
    <!ENTITY rdf "http://www.w3.org/1999/02/22-rdf-syntax-ns#" >
]>
<rdf:RDF xmlns="http://bug.rdflib/i.owl#"
     xml:base="http://bug.rdflib/i.owl"
     xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
     xmlns:owl="http://www.w3.org/2002/07/owl#"
     xmlns:xsd="http://www.w3.org/2001/XMLSchema#"
     xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
     xmlns:i="http://bug.rdflib/i.owl#">
    <owl:Ontology rdf:about="http://bug.rdflib/i.owl"/>
    <owl:NamedIndividual rdf:about="&i;individual"/>
</rdf:RDF>"""

q = """\
SELECT ?x
WHERE {
 ?x rdf:type owl:NamedIndividual .
}"""

p = """\
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
"""

"""
Seems to me that this is a bug or at least an oversight in rdfextras:
the graph's bound prefixes are apparently not passed to queries.
Here's a helper function that may or may not work (sorry, can't test):
"""

def query(graph, querystring):
    processor = rdflib.plugin.get('sparql', rdflib.query.Processor)(graph)
    result = rdflib.plugin.get('sparql', rdflib.query.Result)
    ns = dict(graph.namespace_manager.namespaces())
    return result(processor.query(querystring, initNs=ns))

class TestSPARQLQueryinitNs(unittest.TestCase):

    def setUp(self):
        self.graph = Graph()
        self.graph.parse(data=xmldata)
        self.expect = set([x for x,_,_ in self.graph.triples(
                    (None, RDF['type'], OWL['NamedIndividual'])) ])

    def testnoprefix(self):
        ns = {u'owl':Namespace("http://www.w3.org/2002/07/owl#"),
              u'rdf':Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")}
        got = set([ x for (x,) in self.graph.query(q, initNs=ns, DEBUG=True)])
        assert self.expect == got, (self.expect, got)

