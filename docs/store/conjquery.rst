.. _conjquery: RDFExtras, store conjunctive_query.

|today|

======================================================================
Patterns and Optimizations for RDF Queries over Named Graph Aggregates
======================================================================

`Original post <http://copia.posterous.com/patterns-and-optimizations-for-rdf-queries-ov>`_ 
by `Chimezie Ogbuji <http://posterous.com/people/10xO4b8IeU9>`_


In a `previous post <http://copia.posterous.com/closed-world-assumptions-conjunctive-querying>`_ 
I used the term 'Conjunctive Query' to refer to a kind of
RDF query pattern over an aggregation of named graphs. However, the term
(apparently) has already-established roots in database querying and has a
different meaning that what I intended. It's a pattern I have come across
often and is for me a major requirement for an RDF query language, so I'll try
to explain by example.

Consider two characters, King (Wen) and his heir / son (Wu) of the Zhou
Dynasty. Let's say they each have a FOAF graph about themselves and the people
they know within a larger database which holds the FOAF graphs of every
historical character in literature.

The FOAF graphs for both Wen and Wu are (preceded by the name of each graph):

.. sourcecode:: xml

    <urn:literature:characters:KingWen>

.. code-block:: n3

    @prefix : <http://xmlns.com/foaf/0.1/> .
    @prefix rel: <http://purl.org/vocab/relationship/> .

    <http://en.wikipedia.org/wiki/King_Wen_of_Zhou> a :Person ;
        :name "King Wen" ;
        :mbox <mailto:kingWen@historicalcharacter.com> ;
        rel:parentOf [ a :Person; :mbox <mailto:kingWu@historicalcharacter.com> ] .
    

.. sourcecode:: xml

    <urn:literature:characters:KingWu>

.. code-block:: n3

    @prefix : <http://xmlns.com/foaf/0.1/>.
    @prefix rel: <http://purl.org/vocab/relationship/>.

    <http://en.wikipedia.org/wiki/King_Wu_of_Zhou> a :Person;
        :name "King Wu";
        :mbox <mailto:kingWu@historicalcharacter.com>;
        rel:childOf [ a :Person; :mbox <mailto:kingWen@historicalcharacter.com> ].
    

In each case, Wikipedia URLs are used as identifiers for each historical
character. There are better ways for using Wikipedia URLs within RDF, but
we'll table that for another conversation.

Now lets say a third party read a few stories about “King Wen” and finds out
he has a son, however, he/she doesn't know the son's name or the URL of either
King Wen or his son. If this person wants to use the database to find out
about King Wen's son by querying it with a reasonable response time, he/she
has a few thing going for him/her:

.. sourcecode:: n3

    foaf:mbox is an owl:InverseFunctionalProperty 
    
and so can be used for uniquely identifying people in the database.

The database is organized such that all the out-going relationships (between
``foaf:Persons`` – ``foaf:knows``, ``rel:childOf``, ``rel:parentOf``, etc..) 
of the same person are asserted in the FOAF graph associated with that person
and nowhere else.

So, the relationship between King Wen and his son, expressed with the term
``ref:parentOf``, will only be asserted in

.. sourcecode:: text

    urn:literature:characters:KingWen.

Yes, the idea of a character from an ancient civilization with an email
address is a bit cheeky, but foaf:mbox is the only inverse functional property
in FOAF to use to with this example, so bear with me.

Now, both Versa and SPARQL support restricting queries with the explicit name
of a graph, but there are no constructs for determining all the contexts of an
RDF triple or:

The names of all the graphs in which a particular statement (or statements
matching a specific pattern) are asserted.

This is necessary for a query plan that wishes to take advantage of [2]. Once
we know the name of the graph in which all statements about King Wen are
asserted, we can limit all subsequent queries about King Wen to that same
graph without having to query across the entire database.

Similarly, once we know the email of King Wen's son we can locate the other
graphs with assertions about this same email address (knowing they refer to
the same person [1]) and query within them for the URL and name of King Wen's
son. This is a significant optimization opportunity and key to this query
pattern.

I can't speak for other RDF implementations, but RDFLib has a mechanism for
this at the API level: a method called :meth:`~rdflib.graph.ConjunctiveGraph.quads`
which takes a tuple of three terms ``((subject, predicate, object))`` and 
returns a tuple of size 4 which correspond to the all triples (across the 
database) that match the pattern along with the graph that the triples are 
asserted in:

.. sourcecode:: python

    for s,p,o,containingGraph in aConjunctiveGraph.quads(s,p,o):
        do_something_with(containingGraph)

It's likely that most other QuadStores have similar mechanisms and given the
great value in optimizing queries across large aggregations of named RDF
graphs, it's a strong indication that RDF query languages should provide the
means to express such a mechanism.

Most of what is needed is already there (in both Versa and SPARQL). Consider a
SPARQL extension function which returns a boolean indicating whether the given
triple pattern is asserted in a graph with the given name:

.. sourcecode:: text

    rdfg:AssertedIn(?subj,?pred,?obj,?graphIdentifier)

We can then get the email of King Wen's son efficiently with:

.. code-block:: sparql

    BASE  <http://xmlns.com/foaf/0.1/>
    PREFIX rel: <http://purl.org/vocab/relationship/>
    PREFIX rdfg: <http://www.w3.org/2004/03/trix/rdfg-1/>

    SELECT ?mbox
    WHERE {
        GRAPH ?foafGraph {
          ?kingWen :name "King Wen";
                           rel:parentOf [ a :Person; :mbox ?mbox ] .
        }  
         FILTER (rdfg:AssertedIn(?kingWen,:name,”King Wen”,?foafGraph) ) .
    }

Now, it is worth noting that this mechanism can be supported explicitly by
asserting provenance statements associating the people the graphs are about
with the graph identifiers themselves, such as:

.. sourcecode:: n3

    <urn:literature:characters:KingWen> 
      :primaryTopic <http://en.wikipedia.org/wiki/King_Wen_of_Zhou> .

However, I think that the relationship between an RDF triple and the graph in
which it is asserted, although currently outside the scope of the RDF model,
should have its semantics outlined in the RDF abstract syntax instead of
using terms in an RDF vocabulary. The demonstrated value in RDF query
optimization makes for a strong argument:

.. code-block:: sparql

    BASE  <http://xmlns.com/foaf/0.1/>
    PREFIX rel: <http://purl.org/vocab/relationship/>
    PREFIX rdfg: <http://www.w3.org/2004/03/trix/rdfg-1/>

    SELECT ?kingWu,  ?sonName
    WHERE {
        GRAPH ?wenGraph {
          ?kingWen :name "King Wen";
                           :mbox ?wenMbox;
                           rel:parentOf [ a :Person; :mbox ?wuMbox ].
        }  
        FILTER (rdfg:AssertedIn(?kingWen,:name,"King Wen",?wenGraph) ).
        GRAPH ?wuGraph {
          ?kingWu :name ?sonName;
                         :mbox ?wuMbox;
                         rel:childOf [ a :Person; :mbox ?wenMbox  ].
        }  
         FILTER (rdfg:AssertedIn(?kingWu,:name,?sonName,?wuGraph) ).
    }

Generally, this pattern is any two-part RDF query across a database (a
collection of multiple named graphs) where the scope of the first part of the
query is the entire database, identifies terms that are local to a specific
named graph, and the scope of the second part of the query is this named
graph.

