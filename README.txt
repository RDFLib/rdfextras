========================================================================
RDFExtras README
========================================================================

RDFExtras is a collection of packages providing extras based on RDFLib. These
include a tools package and several "non-core-rdflib" store implementations.

RDFExtras includes: 

 * Extra plugins for parsing/serialisation of RDF/JSON and JSON-LD
 * A pure-python SPARQL implementation for in-memory stores or other store
   that do not provide their own SPARQL implementation. 
 * A set of extra stores implementations: 
   * DB backed stores: KyotoCabinet, ZODB, SQLite, MySQL, PostgreSQL
   * A SPARQL Store for a graph on top of a remote SPARQL endpoint. Read-only
     access with SPARQL 1.0 or read-write with SPARQL 1.1 support.
 * A set of commandline utilities: rdfpipe, rdf2dot, rdfs2dot, csv2rdf

Dependencies: 

 * RDFLib>=3.2.1
 * For SPARQL: pyparsing
 * For SPARQL Store: SPARQLWrapper


For more information see: 
 * RDFExtras: http://code.google.com/p/rdfextras/
 * RDFExtras Docs: http://readthedocs.org/docs/rdfextras/
 
 * RDFLib: http://code.google.com/p/rdflib/
 * RDFLib Docs: http://readthedocs.org/docs/rdflib

 * Discussion group: http://groups.google.com/group/rdflib-dev
