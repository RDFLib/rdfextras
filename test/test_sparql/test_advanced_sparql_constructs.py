import unittest
from rdflib import plugin
from rdflib.namespace import Namespace,RDF,RDFS
from rdflib.term import URIRef
from rdflib.store import Store
from cStringIO import StringIO
from rdflib import Graph

import rdflib


try:
    set
except NameError:
    from sets import Set as set


testGraph1N3="""
@prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix : <http://test/> .
:foo :relatedTo [ a rdfs:Class ];
     :parentOf ( [ a rdfs:Class ] ).
:bar :relatedTo [ a rdfs:Resource ];
     :parentOf ( [ a rdfs:Resource ] ).
     
( [ a rdfs:Resource ] ) :childOf :bar.     
( [ a rdfs:Class ] )    :childOf :foo.
"""

sparqlQ1 = \
"""
BASE <http://test/>
PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?node WHERE { ?node :relatedTo [ a rdfs:Class ] }"""


sparqlQ2 = \
"""
BASE <http://test/>
PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?node WHERE { ?node :parentOf ( [ a rdfs:Class ] ) }"""


sparqlQ3 = \
"""
BASE <http://test/>
PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?node WHERE { ( [ a rdfs:Resource ] ) :childOf ?node }"""

sparqlQ4 = \
"""
PREFIX owl:  <http://www.w3.org/2002/07/owl#> 

SELECT DISTINCT ?class 
FROM <http://www.w3.org/2002/07/owl#>
WHERE { ?thing a ?class }"""

class AdvancedTests(unittest.TestCase):
    def setUp(self):
        memStore = plugin.get('IOMemory',Store)()
        self.testGraph = Graph(memStore)
        self.testGraph.parse(StringIO(testGraph1N3),format='n3')
        
    def testNamedGraph(self):
        # I am not sure this is the behaviour we DO want. 
        # see https://github.com/RDFLib/rdfextras/issues/27
        OWL_NS = Namespace("http://www.w3.org/2002/07/owl#")
        rt =  self.testGraph.query(sparqlQ4)
        self.assertEquals(set(rt),set((x,) for x in [OWL_NS.DatatypeProperty, OWL_NS.ObjectProperty, OWL_NS.OntologyProperty,OWL_NS.Class,OWL_NS.Ontology,OWL_NS.AnnotationProperty,RDF.Property,RDFS.Class]))

    def testScopedBNodes(self):
        rt =  self.testGraph.query(sparqlQ1)
        self.assertEquals(list(rt)[0][0],URIRef("http://test/foo"))

    def testCollectionContentWithinAndWithout(self):
        rt =  self.testGraph.query(sparqlQ3)
        self.assertEquals(list(rt)[0][0],URIRef("http://test/bar"))

    def testCollectionAsObject(self):
        rt =  self.testGraph.query(sparqlQ2)
        self.assertEquals(list(rt)[0][0],URIRef("http://test/foo"))
        self.assertEquals(1,len(rt))

if __name__ == '__main__':
    suite = unittest.makeSuite(AdvancedTests)
    unittest.TextTestRunner(verbosity=3).run(suite)
