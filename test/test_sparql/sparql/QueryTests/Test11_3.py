#!/d/Bin/Python/python.exe
# -*- coding: utf-8 -*-
#
#
# $Date: 2005/04/02 07:29:46 $, by $Author: ivan $, $Revision: 1.1 $
#
"""
   Datatype test. Note that this is not 100% kosher. The problem is that the Literal of rdflib does not check the
   datatypes. In theory, if the data contains:

           x ns:p 42.

   instead of:

       x ns:p 42^^http://www.w3.org/2001/XMLSchema#integer

    the query should return no results, because the first object is of datatype string. However, Literal does not
        implement this...

"""

rdfData ="""<?xml version="1.0" encoding="UTF-8"?>
<rdf:RDF
   xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
   xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
   xmlns:dc="http://purl.org/dc/elements/1.1/"
   xmlns:foaf="http://xmlns.com/foaf/0.1/"
   xmlns:ns = "http://example.org/ns#"
>
        <rdf:Description>
                <foaf:name>Alice</foaf:name>
                <foaf:mbox rdf:resource="mailto:alice@work.example"/>
        </rdf:Description>
        <rdf:Description>
                <foaf:name>Bob</foaf:name>
                <foaf:mbox>bob@work.example</foaf:mbox>
        </rdf:Description>
</rdf:RDF>
"""



from testSPARQL import ns_rdf
from testSPARQL import ns_rdfs
from testSPARQL import ns_dc
from testSPARQL import ns_foaf
from testSPARQL import ns_ns
from testSPARQL import ns_book

from rdflib import Literal
from rdfextras.sparql.graph import GraphPattern

from rdfextras.sparql.operators import isURI


select      = ["?name", "?mbox"]
pattern     = GraphPattern([("?x", ns_foaf["name"],"?name"),("?x",ns_foaf["mbox"],"?mbox")])
pattern.addConstraint(isURI("?mbox"))
optional    = []
tripleStore = None
expected = '''
  ?name: Alice
  ?mbox: mailto:alice@work.example
'''



