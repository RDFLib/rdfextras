.. _queryapi: RDFExtras SPARQL implementations

|today|

===========================
Comprehensive RDF Query API
===========================

`Original post <http://copia.posterous.com/comprehensive-rdf-query-apis-for-rdflib>`_ 
by `Chimezie Ogbuji <http://posterous.com/people/10xO4b8IeU9>`_ (edited for
contemporary use by Graham Higgins <gjh@bel-epa.com>)

RDFLib's support for SPARQL has come full circle and I wasn't planning on
blogging on the developments until they had settled some – and they have. In
particular, the last piece was finalizing a set of APIs for querying and
result processing that fit well within the framework of RDFLib's various Graph
API's. The other issue was for the query APIs to accomodate eventual support
for other querying languages that are capable of picking up the slack where SPARQL
is wanting (transitive closures, for instance – try composing a concise SPARQL query 
for calculating the transitive closure of a given node along the ``rdfs:subClassOf`` 
property and you'll immediately see what I mean).

Querying
--------

Every Graph instance has a ``query`` method through which RDF queries can be
dispatched:

.. sourcecode:: python

    def query(self, 
                strOrQuery, initBindings={}, initNs={}, 
                DEBUG=False, processor="sparql")
        """
        Executes a SPARQL query (eventually will support Versa queries with
        same method) against this Conjunctive Graph
        
        :Params:

        :strOrQuery: - Is either a string consisting of the SPARQL query 
            or an instance of rdflib.sparql.bison.Query.Query
        
        :initBindings: - A mapping from variable name to an RDFLib term 
            (used for initial bindings for SPARQL query)
        
        :initNS: - A mapping from a namespace prefix to an instance of 
            rdflib.Namespace (used for SPARQL query)
        
        :DEBUG: - A boolean flag passed on to the SPARQL parser and 
            evaluation engine
        
        :processor: - The kind of RDF query. Choose 'sparql' to use the 
            pure-Python "nOSQL" SPARQL processor, choose 'sparql2sql' to
            use the pure-Python "SPARQL2SQL" SPARQL processor.
        
        """

The first positional argument ``strOrQuery`` is either a query string or
a pre-compiled query object (compiled using the appropriate BisonGen 
mechanism for the target query language). Pre-compilation can be useful
for avoiding redundant parsing overhead for queries that need to be
evaluated repeatedly:

.. sourcecode:: python

    from rdfextras.sparql2sql.bison import Parse
    queryObject = Parse(sparqlString)

The ``initBindings`` keyword argument is a dictionary that maps variables
to their values. The dictionary is expected to be a mapping from variables
to RDFLib terms. This is passed on to the SPARQL processor as initial variable bindings.

``initNs`` is yet another top-level parameter for the query processor: 
a namespace mapping from prefixes to namespace URIs.

The ``DEBUG`` flag is pretty self-explanatory. When set to ``True``, it
will cause additional print statements to appear for the parsing of the
query (when the ``sparql2sql`` processor is selected) as well as the
patterns and constraints passed on to the processor (for SPARQL queries).

Finally, the ``processor`` keyword specifies which kind of processor to use to 
evaluate the query: ``sparql`` or ``sparql2sql``.

Result formats
--------------

SPARQL has two result formats (JSON and XML). Thanks to Ivan Herman's recent
contribution the SPARQL processor now supports both formats. The query method
(above) returns instances of ``QueryResult``, a common class for RDF query results
which define the following method:

.. sourcecode:: python

    def serialize(self,format='xml'):
        # real code required ...
        pass

The format argument determines which result format to use. For SPARQL queries,
the allowable values are: ``graph`` – for CONSTRUCT / DESCRIBE queries (in which
case a resulting ``Graph`` object is returned), ``json``,or ``xml``. The resulting
object also acts as an iterator over the bindings to allow for manipulation in the
host language (Python).
