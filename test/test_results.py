import sys
from nose.exc import SkipTest
import unittest
import rdflib
from StringIO import StringIO

class TestSparqlResultsFormats(unittest.TestCase): 

    def _test(self,s,format):
        r = rdflib.query.Result.parse(StringIO(s), format=format)
        print r.type
        s = r.serialize(format=format)
        #print s
        r2 = rdflib.query.Result.parse(StringIO(s.decode('utf-8')), format=format)
        self.assertEqual(r, r2)

    def testXML(self):
        if sys.version_info[:2] < (2, 6):
            raise SkipTest("Skipped, known issue with XML namespaces under Python < 2.6")
        xmlres="""<?xml version="1.0"?>
<sparql xmlns="http://www.w3.org/2005/sparql-results#"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://www.w3.org/2001/sw/DataAccess/rf1/result2.xsd">

  <head>
    <variable name="x"/>
    <variable name="hpage"/>
    <variable name="name"/>
    <variable name="mbox"/>
    <variable name="age"/>
    <variable name="blurb"/>
    <variable name="friend"/>

    <link href="example.rq" />
  </head>

  <results>

    <result>
      <binding name="x"><bnode>r1</bnode></binding>
      <binding name="hpage"><uri>http://work.example.org/alice/</uri></binding>
      <binding name="name"><literal>Alice</literal></binding>
      <binding name="mbox"><literal></literal></binding>
      <binding name="friend"><bnode>r2</bnode></binding>
      <binding name="blurb"><literal datatype="http://www.w3.org/1999/02/22-rdf-syntax-ns#XMLLiteral">&lt;p xmlns="http://www.w3.org/1999/xhtml"&gt;My name is &lt;b&gt;alice&lt;/b&gt;&lt;/p&gt;</literal></binding>
    </result>

    <result> 
      <binding name="x"><bnode>r2</bnode></binding>
      <binding name="hpage"><uri>http://work.example.org/bob/</uri></binding>
      <binding name="name"><literal xml:lang="en">Bob</literal></binding>
      <binding name="mbox"><uri>mailto:bob@work.example.org</uri></binding>
      <binding name="age"><literal datatype="http://www.w3.org/2001/XMLSchema#integer">30</literal></binding>
      <binding name="friend"><bnode>r1</bnode></binding>
    </result>

  </results>

</sparql>
"""
        
        self._test(xmlres,"xml")

    def testjson(self):
        jsonres=u"""{
   "head": {
       "link": [
           "http://www.w3.org/TR/rdf-sparql-XMLres/example.rq"
           ],
       "vars": [
           "x",
           "hpage",
           "name",
           "mbox",
           "age",
           "blurb",
           "friend"
           ]
       },
   "results": {
       "bindings": [
               {
                   "x" : {
                     "type": "bnode",
                     "value": "r1"
                   },

                   "hpage" : {
                     "type": "uri",
                     "value": "http://work.example.org/alice/"
                   },

                   "name" : {
                     "type": "literal",
                     "value": "Alice"
                   },
                   
                   "mbox" : {
                     "type": "literal",
                     "value": ""
                   },

                   "blurb" : {
                     "datatype": "http://www.w3.org/1999/02/22-rdf-syntax-ns#XMLLiteral",
                     "type": "typed-literal",
                     "value": "<p xmlns=\\"http://www.w3.org/1999/xhtml\\">My name is <b>alice</b></p>"
                   },

                   "friend" : {
                     "type": "bnode",
                     "value": "r2"
                   }
               },{
                   "x" : {
                     "type": "bnode",
                     "value": "r2"
                   },
                   
                   "hpage" : {
                     "type": "uri",
                     "value": "http://work.example.org/bob/"
                   },
                   
                   "name" : {
                     "type": "literal",
                     "value": "Bob",
                     "xml:lang": "en"
                   },

                   "mbox" : {
                     "type": "uri",
                     "value": "mailto:bob@work.example.org"
                   },

                   "friend" : {
                     "type": "bnode",
                     "value": "r1"
                   }
               }
           ]
       }
   }
"""
        self._test(jsonres,"json")


if __name__ == '__main__':
    unittest.main()
