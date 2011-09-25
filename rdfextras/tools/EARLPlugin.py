""" A Nose Plugin for EARL.

See Also:
  http://nose.python-hosting.com/
  http://www.w3.org/TR/EARL10-Schema/

"""

import logging

from nose.plugins import Plugin

from rdflib.graph import Graph
from rdflib import BNode
from rdflib import Literal
from rdflib.namespace import Namespace
from rdflib.namespace import RDF
from rdflib.namespace import RDFS
from rdflib.util import date_time

log = logging.getLogger(__name__)

EARL = Namespace("http://www.w3.org/ns/earl#")


class EARLPlugin(Plugin):
    """
    Activate the EARL plugin to generate a report of the test results
    using EARL.
    """
    name = 'EARL'
    
    def begin(self):
        self.graph = Graph()
        self.graph.bind("earl", EARL.uri)
        tool = BNode('rdflib')
        self.graph.add((tool, RDF.type, EARL.TestTool))
        self.graph.add((tool, RDFS.label, Literal('rdflib.net')))
        self.graph.add((tool, RDFS.comment, Literal('nosetests')))
    
    def finalize(self, result):
        # TODO: add plugin options for specifying where to send
        # output.
        self.graph.serialize("file:results-%s.rdf" % \
                            date_time().replace(':','-'), format="pretty-xml")
    

    def addDeprecated(self, test):
        print "Deprecated: %s" % test

    
    def addError(self, test, err, capt):
        print "Error: %s" % test

    
    def addFailure(self, test, err, capt, tb_info):
        print("FAILED")
        result = BNode() # TODO: coin URIRef
        self.graph.add((result, RDFS.label, Literal(test)))
        self.graph.add((result, RDFS.comment, Literal(type(test))))
        self.graph.add((result, RDF.type, EARL.TestResult))
        self.graph.add((result, EARL.outcome, EARL["fail"]))
    

    def addSkip(self, test):
        print("SKIPPED")
        result = BNode() # TODO: coin URIRef
        self.graph.add((result, RDFS.label, Literal(test)))
        self.graph.add((result, RDFS.comment, Literal(type(test))))
        self.graph.add((result, RDF.type, EARL.TestResult))
        self.graph.add((result, EARL.outcome, EARL["untested"]))
    

    def addSuccess(self, test, capt):
        print("PASSED")
        result = BNode() # TODO: coin URIRef
        self.graph.add((result, RDFS.label, Literal(test)))
        self.graph.add((result, RDFS.comment, Literal(type(test))))
        self.graph.add((result, RDF.type, EARL.TestResult))
        self.graph.add((result, EARL.outcome, EARL["pass"]))
        # etc

"""
<earl:TestResult rdf:about="#result">
  <earl:outcome rdf:resource="http://www.w3.org/ns/earl#fail"/>
  <dc:title xml:lang="en">Invalid Markup (code #353)</dc:title>
  <dc:description rdf:parseType="Literal" xml:lang="en">
    <div xmlns="http://www.w3.org/1999/xhtml">
      <p>The <code>table</code> element is not allowed to appear
        inside a <code>p</code> element</p>
    </div>
  </dc:description>
  <dc:date rdf:datatype="http://www.w3.org/2001/XMLSchema#date">2006-08-13</dc:date>
  <earl:pointer rdf:resource="#xpointer"/>
  <earl:info rdf:parseType="Literal" xml:lang="en">
    <div xmlns="http://www.w3.org/1999/xhtml">
      <p>It seems the <code>p</code> element has not been closed</p>
    </div>
  </earl:info>
</earl:TestResult>
"""

"""
<earl:TestResult rdf:about="#result">
  <earl:outcome rdf:resource="http://www.w3.org/ns/earl#failed"/>
  <dct:title xml:lang="en">Invalid Markup (code #353)</dct:title>
  <dct:description rdf:parseType="Literal" xml:lang="en">
    <div xmlns="http://www.w3.org/1999/xhtml">
      <p>The <code>table</code> element is not allowed to appear
        inside a <code>p</code> element</p>
    </div>
  </dct:description>
  <earl:pointer rdf:resource="#pointer"/>
  <earl:info rdf:parseType="Literal" xml:lang="en">
    <div xmlns="http://www.w3.org/1999/xhtml">
      <p>It seems the <code>p</code> element has not been closed</p>
    </div>
  </earl:info>
</earl:TestResult>

<earl:Software rdf:about="#tool">
  <dct:title xml:lang="en">Cool Tool</dct:title>
  <dct:description xml:lang="en">My favorite tool!</dct:description>
  <foaf:homepage rdf:resource="http://example.org/tools/cool/"/>
  <dct:hasVersion>1.0.3</dct:hasVersion>
  <dct:isPartOf rdf:resource="http://example.org/tools/cms/"/>
  <dct:hasPart rdf:resource="http://example.org/tools/cool/#module-1"/>
</earl:Software>

<foaf:Agent rdf:about="#assertor">
  <dct:title xml:lang="en">Bob using Cool Tool</dct:title>
  <dct:description xml:lang="en">Bob doing semi-automated testing</dct:description>
  <earl:mainAssertor rdf:resource="http://www.example.org/people/#bob"/>
  <foaf:member rdf:resource="http://www.example.org/tool/#cool"/>
</foaf:Agent>

"""

