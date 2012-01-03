#!/usr/bin/env python

import rdflib
import rdfextras.store.SPARQL

"""
This prints all the labels of 'Berlin' in DBpedia. 

Note that rdflib.Graph methods like triples, subjects, etc. 
do not use limits, and when unconstrained, may return huge amounts of 
data (or simply timeout for sensibly configured public endpoints).

Note also that DBpedia labels include non-ascii characters, 
on Unix-like systems you can force python stdout to be utf-8 compatible
with:

export LC_TYPE=en_GB.utf-8

"""

if __name__=='__main__':

    store=rdfextras.store.SPARQL.SPARQLStore("http://dbpedia.org/sparql")
    graph=rdflib.Graph(store)
    berlin=rdflib.URIRef("http://dbpedia.org/resource/Berlin")

    for label in graph.objects(berlin, rdflib.RDFS.label): 
        print label

       
