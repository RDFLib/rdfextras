.. _queryapi: RDFExtras SPARQL implementations

|today|

===========================
Comprehensive RDF Query API
===========================

`Original post <http://copia.posterous.com/comprehensive-rdf-query-apis-for-rdflib>`_ 
by `Chimezie Ogbuji <http://posterous.com/people/10xO4b8IeU9>`_

RDFLib's support for SPARQL has come full circle and I wasn't planning on
blogging on the developments until they had settled some – and they have. In
particular, the last piece was finalizing a set of APIs for querying and
result processing that fit well within the framework of RDFLib's various Graph
API's. The other issue was for the query APIs to accomodate eventual support
for other querying languages (Versa for instance) that are capable of picking
up the slack where SPARQL is wanting (transitive closures, for instance – try
composing a concise SPARQL query for calculating the transitive closure of a
given node along the rdfs:subClassOf property and you'll immediately see what
I mean).

Querying
--------

Every Graph instance now has a query method through which RDF queries can be
dispatched:

.. sourcecode:: python

    def query(self, strOrQuery, initBindings={}, initNs={}, DEBUG=False, processor="sparql")
        """
        Executes a SPARQL query (eventually will support Versa queries with same method) against this Conjunctive Graph
        strOrQuery - Is either a string consisting of the SPARQL query or an instance of rdflib.sparql.bison.Query.Query
        initBindings - A mapping from variable name to an RDFLib term (used for initial bindings for SPARQL query)
        initNS - A mapping from a namespace prefix to an instance of rdflib.Namespace (used for SPARQL query)
        DEBUG - A boolean flag passed on to the SPARQL parser and evaluation engine
        processor - The kind of RDF query (must be 'sparql' until Versa is ported)
        """

The first argument is either a query string or a pre-compiled query object
(compiled using the appropriate BisonGen mechanism for the target query
language). Pre-compilation can be useful for avoiding redundant parsing
overhead for queries that need to be evaluated repeatedly:

.. sourcecode:: python

    from rdfextras.sparql2sql.bison import Parse
    queryObject = Parse(sparqlString)

The next argument (initBindings) is dictionary that maps variables to their
values. Though variables are common to both languages, SPARQL variables differ
from Versa queries in that they are string terms in the form “?varName”,
wherease in Versa variables are QNames (same as in Xpath). For SPARQL queries
the dictionary is expected to be a mapping from variables to RDFLib terms.
This is passed on to the SPARQL processor as initial variable bindings.

initNs is yet another top-level parameter for the query processor: a namespace
mapping from prefixes to namespace URIs.

The debug flag is pretty self explanatory. When True, it will cause additional
print statements to appear for the parsing of the query (triggered by
BisonGen) as well as the patterns and constraints passed on to the processor
(for SPARQL queries).

Finally, the processor specifies which kind of processor to use to evaluate
the query: 'versa' or 'sparql'. Currently (with emphasis on 'currently'), only
SPARQL is supported.

Result formats
--------------

SPARQL has two result formats (JSON and XML). Thanks to Ivan Herman's recent
contribution the SPARQL processor now supports both formats. The query method
(above) returns instances of QueryResult, a common class for RDF query results
which define the following method:

.. sourcecode:: python

    def serialize(self,format='xml')

The format argument determines which result format to use. For SPARQL queries,
the allowable values are: 'graph' – for CONSTRUCT / DESCRIBE queries (in which
case a resulting Graph object is returned), 'json',or 'xml'. The resulting
object also behaves as an iterator over the bindings for manipulation in the
host language (Python).

Versa has it's own set of result formats as well. Primarily there is an XML
result format (see: Versa by Example) as well as Python classes for the
various internal datatypes: strings,resources,lists,sets,and numbers. So, the
eventual idea is for using the same method signature for serializing Versa
queries as XML as you would for SPARQL queries.

SPARQL Limitations
-------------------

.. warning:: the limitations mentioned have been addressed. 

The known SPARQL query forms that aren't supported are:

* DESCRIBE/CONSTRUCT (very temporary)
* Nested Group Graph Patterns
* Graph Patterns can only be used (once) by themselves or with OPTIONAL patterns
* UNION patterns can only be combined with OPTIONAL patterns
* Outer FILTERs which refer to variables within an OPTIONAL

A lot of the above limitations can be addressed with formal equivalence 
axioms of SPARQL semantics, such as those mentioned in the recent paper 
on the complexity and semantics of SPARQL. Since there is very little guidance 
on the semantics of SPARQL I was left with the option of implementing only 
those equivalences that seemed obvious (in order to support the patterns in 
the DAWG test suite):

.. code-block:: text

    1) { patternA { patternB } } => { patternA. patternB }
    2) { basicGraphPatternA OPTIONAL { .. } basicGraphPatternB }
      =>
    { basicGraphPatternA+B OPTIONAL { .. }}
