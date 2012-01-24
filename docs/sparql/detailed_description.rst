.. _rdfextras_sparql: RDFExtras SPARQL implementations

|today|

===============================
SPARQL in RDFLib (Version 2.1)
===============================

:author: Ivan Herman ivan@ivan-herman.net
:date: 2005/10/10 15:40:35

Introduction
============
This is a short overview of the query facilities added to `RDFLib <http://rdflib.net>`_. 
These are based on the July 2005 version of the `SPARQL draft <http://www.w3.org/TR/rdf-sparql-query/>`_
worked on at the W3C. For a lack of a better word, I refer to this implementation as ``sparql-p``.

Thanks to the work of Daniel Krech and mainly Michel Pelletier,
``sparql-p`` is now fully integrated with the newer versions of
RDFLib (version `2.2.2 <http://rdflib.net/2005/09/10/rdflib-2.2.2/README/>`_ or later), whereas earlier versions were distributed as separate
packages. This integration has led to some minor adjustments in class naming
and structure compared to earlier versions. If you are looking for the
documentation of the separate package, please refer to an `earlier version <http://dev.w3.org/cvsweb/~checkout~/2004/PythonLib-IH/Doc/sparqlDesc.html?rev=1.8>`_ of this document. Be warned, though, that the
earlier versions are now deprecated in favour of RDFLib 2.2.2 or later.

The SPARQL draft describes its facilities in terms of a query language. A
full SPARQL implementation should include a parser of that language mapping
on the underlying implementation. ``sparql-p`` does *not*
include such parser yet, only the underlying SPARQL engine and its API. The
description below shows how the mapping works. This also means that the API
is not the full implementation of SPARQL: some of the features should be left
to the parser that could use this API. This is the case, for example, of
named Graphs facilities that could be mapped using RDFLib ``Graph``
instances: *all* query is performed on such an instance in the first
place! In any case, the implementation of ``sparql-p`` covers (I
believe) the most frequently used cases of SPARQL.

The SPARQL facilities ar based on a wrapper class called
:class:`~rdfextras.sparql.sparqlGraph.SPARQLGraph` around the basic :class:`~rdflib.graph.Graph` object defined
by RDFLib. Ie, all programs using ``sparql-p`` should be of the
form:

.. sourcecode:: python

    from rdfextras.sparql import sparqlGraph
    sparqlGr = sparqlGraph.SPARQLGraph()

the ``sparqlGr`` object thus created has the same methods as a :class:`~rdflib.graph.Graph` type object would have, extended with the
``sparql-p`` facilities. An alternative way of creating the
``sparql-p`` graph is to use an existing :class:`~rdflib.graph.Graph`
instance:

.. sourcecode:: python

    sparqlGr = sparqlGraph.SPARQLGraph(graph=myExistingGraph)


Basic SPARQL
============

The basic SPARQL construct is as follows (using the query syntax of the
SPARQL document):

.. sourcecode:: sparql

    SELECT ?a ?b ?c
    WHERE { ?a P ?x .
            Q ?b ?a .
            ?x R ?c
         }


The meaning of this construction is simple: the '?a', '?b', etc, symbols
(referred to as 'unbound' symbols) are queried with the constraint that the
tuples listed in the ``WHERE`` clause are 'true', i.e., part of the
triple store. This functionality is translated into a Python method as:

.. sourcecode:: python

    from rdfextras.sparql import GraphPattern
    select = ("?a","?b","?c")
    where  = GraphPattern([("?a",P,"?x"),(Q,"?b","?a"),("?x",R,"?c")])
    result = sparqlGr.query(select,where)


where ``result`` is a list of tuples, each giving possible
binding combinations for "?a", "?b", and "?c", respectively. ``P``,
``Q``, ``R``, etc, must be the rdflib incarnations of RDF
resources, i.e., :class:`~rdflib.term.URIRef`, :class:`~rdflib.term.Literal`, etc. The
object of each pattern can also be one of the following Python types:

 * ``integer``
 * ``long``
 * ``float``
 * ``string``
 * ``unicode``
 * ``datetime.date``,
 * ``datetime.time``, 
 * ``datetime.datetime``

these are transformed into a :class:`~rdflib.term.Literal` with the corresponding XML Schema
datatype on the fly. This allows coding in the form:

.. sourcecode:: python

    select = ("?a","?b","?c")
    where  = GraphPattern([("?a",P,"?x"),(Q,"?b","?a"),("?x",R,"?c"),
                          ("?x",S,"Some Literal Here"),("?x",R,43)])
    result = sparqlGr.query(select,where)


Note that the SPARQL draft mandates datetime only, not
separate date and time, but it was obvious to add this into the Python
implementation (and useful in practice). See also the note above on literals, 
as well as the additional section on datatypes.

As a further convenience to the user, if ``select`` consists of a
single entry, it is not necessary to use a tuple and just giving the string
value will do. Similarly, if the ``where`` consists of one single
tuple, the array construction may be skipped, and the single tuple is
accepted as an argument. Finally, if ``select`` consists of one
entry, ``result`` is a list of the values rather than tuples of
(single) values.

The :class:`~rdfextras.sparql.graphPattern.GraphPattern` class instance can be built up gradually via
the :meth:`~rdfextras.sparql.graphPattern.GraphPattern.addPattern` and 
:meth:`~rdfextras.sparql.graphPattern.GraphPattern.addPatterns` methods (the former
takes one tuple, the latter a list of tuples).

The draft describes nested patterns, too, but it also draws
the attention to the fact that nested patterns can be turned into regular
patterns by possibly repeating some patterns. In other words, nested
patterns  can be handled by a parser and is therefore not implemented on
this API level.

The :class:`~rdfextras.sparql.SPARQLError` exception is raised (beyond the
possible exceptions raised by rdflib) if there are inconsistencies in the
``select`` or ``where`` clauses (e.g., the tuples do not
have the correct length or there are incorrect data in the tuples
themselves).

Constraining Values
-------------------

SPARQL makes it possible to constrain values through operators, like:

.. sourcecode:: sparql

    SELECT ?a,?b,?c
    WHERE { ?a P ?x .
            Q ?b ?a .
            ?x R ?c .
            FILTER ?x &lt; 10
           }
     ...


The draft also refers to the fact that application specific functions can
also be used in the 'FILTER' part. There are two ways to translate this
feature into ``sparql-p`` (see below for a further discussion).

Global Constraint
-----------------

This version is based on constraints that refer to the whole binding of
the pattern and is therefore executed against the full binding once
available. Here is how it looks in ``sparql-p``:

.. sourcecode:: python

    select = ("?a","?b","?c")
    where  = GraphPattern([("?a",P,"?x"),(Q,"?b","?a"),
                           ("?x",R,"?c"),("?x",S,"Some Literal Here")])
    where.addConstraint(func1)
    where.addConstraints([func2,func3,...])
    result = sparqlGr.query(select,where)


Each function in the constraints is of the form:

.. sourcecode:: python

    def func1(bindingDir) :
        # ....
        return True # or False 


where ``bindingDir`` is a dictionary of the possible binding, ie, of the form 

.. sourcecode:: sparql

    {"?a" : Resource1, "?b" : Resource2, ...}

Adding several constraints (in a list or via a series of :meth:`~rdfextras.sparql.graphPattern.GraphPattern.addConstraint`
methods) is equivalent to a logical conjunction of the individual
constraints.

As an extra help to operator writers, the ``bindingDir`` also
includes a special entry referring to the :class:`~rdfextras.sparql.sparqlGraph.SPARQLGraph` instance
in use via a special key:

.. sourcecode:: python

    from rdfextras.sparql import graphKey
    graph = bindingDir[graphKey]


This construction, ie, the global constraint, is the faithful
representation of the SPARQL spec. Note that a number of operator methods are
available to make the construction of the global constraints easier, see the
separate section on that.

Per Pattern constraint
----------------------

This version is based on a constraint that can be imposed on one specific
(bound) pattern only. This is achieved by adding a fourth element to the
tuple representing the pattern, e.g.:

.. sourcecode:: python

    select = ("?a","?b","?c")
    where  = GraphPattern([("?a",P,"?x",func),(Q,"?b","?a"),
                           ("?x",R,"?c"),("?x",S,"Some Literal Here")])
    result = sparqlGr.query(select,where)


where ``func`` is a function with three arguments (the bound
version of the ``?a``, ``P``, ``?x`` in the
example).

Why Two Constraints?
--------------------

Functionally, the global constraint is  a 'superset' of the per pattern
constraint; in other words, anything that can be expressed by per pattern
constraints can be achieved by global constraints. E.g., a method above can
be expressed in two different ways:

.. sourcecode:: python

    select = ("?a","?b","?c")
    where  = GraphPattern([("?a",P,"?x"),(Q,"?b","?a"),
                           ("?x",R,"?c"),("?x",S,"Some Literal Here")])
    where.addConstraint(lambda binding: int(binding["?x"]) &lt; 10)
    result = sparqlGr.query(select,where)

or:

.. sourcecode:: python

    select = ("?a","?b","?c")
    where  = GraphPattern([("?a",P,"?x",lambda a,P,x: int(x) &lt; 10),
            (Q,"?b","?a"),("?x",R,"?c"),("?x",S,"Some Literal Here")])
    result = sparqlGr.query(select,where)


However, the second version may be much more efficient. The search is
'cut' in the by the constraint, ie the binding tree is not (unnecessarily)
expanded further, whereas a full binding tree must be generated for a global
constraint (see the notes on the implementation below).

For large triple stores and/or large patterns this may be a significant
difference. A parser may optimize by generating per-pattern constraints in
some cases to make use of this optimization, hence this alternative.

'Or'-d Patterns
===============
A slight variation of the basic scheme could be described as:

.. sourcecode:: sparql

    SELECT ?a,?b,?c
    WHERE { { ?a P ?x . Q ?b ?a } UNION { S ?b ?a. ?x R ?c } }
     ...


(I hope my understanding is correct that...) the meaning a logical 'or' on
one of the clauses.  This is expressed in ``sparql-p`` by allowing
the query method to accept a list of graph patterns, too, instead of single
patterns only:

.. sourcecode:: python

    select = ("?a","?b","?c")
    where1 = GraphPattern([("?a",P,"?x"),(Q,"?b","?a")])
    where1 = GraphPattern([(S,"?b","?a"),("?x",R,"?c")])
    result = sparqlGr.query(select,[where1,where2])


The two queries are evaluated separately, and the concatenation of the
results is returned.

Optional Matching
=================
Another variation on the basic query is the usage of 'optional' clauses:

.. sourcecode:: sparql

    SELECT ?a,?b,?c,?d
    WHERE { ?a P ?x . 
            Q ?b ?a . 
            ?x R ?c .
            OPTIONAL { ?x S ?d. ... }
          }


What this means is that if the fourth tuple (with ``?x`` already bound) is not
in the triple store, that should not invalidate the possible bindings of
``?a``, ``?b``, and ``?c``; instead, the ``?d`` unbound variable should be set to a
null value, but the remaining bindings should be returned. In other words
first the following query is performed:

.. sourcecode:: sparql

    SELECT ?a,?b,?c
    WHERE { ?a P ?x . 
            Q ?b ?a . 
            ?x R ?c
          }


then, for *each possible bindings*, a second query is done:

.. sourcecode:: sparql

    SELECT ?d
    WHERE { X S ?d }


where ``X`` stands for a possible binding of ``?x``.

The ``sparql-p`` expression of this facility is based on the
creation of a separate graph pattern for the optional clause:

.. sourcecode:: python

    select = ("?a","?b","?c","?d")
    where  = GraphPattern([("?a",P,"?x"),[(Q,"?b","?a"),("?x",R,"?c")])
    opt    = GraphPattern([("?x",S,"?d")])
    result = sparqlGr.query(select,where,opt)


and the (possible) unbound ``?d`` is set to ``None``
in the return value. Just as for the 'main' pattern, the third argument of
the call can be a list of graph patterns (for several OPTIONAL clauses) 
evaluated separately. Each of the OPTIONAL clauses can have their global
constraints.

Query Forms
===========
The SPARQL draft includes several `Query forms <http://www.w3.org/TR/rdf-sparql-query/#QueryForms>`_, which is a term to
control how the query results are returned to the caller. In the case of
``sparql-p`` this is implemented via a separate Python class, called
:class:`~rdfextras.sparql.Query.Query`. All query results yield, in fact, an instance of that
class, and various methods on that class are defined corresponding to the
SPARQL Query Forms. The :meth:`~rdfextras.sparql.Query.queryObject` method can be
invoked instead of :meth:`~rdfextras.sparql.Query.query` to return an instance of
such object. (In fact, the ``SPARQLGraph.query`` method, used in all
previous examples, is simply a convenient shorthand, see below.)

SELECT Forms
------------

The ``SELECT`` SPARQL query forms are used to retrieve the query results.
Corresponding to the draft, the :class:`~rdfextras.sparql.Query.Query` class has a
:meth:`~rdfextras.sparql.Query.Query.select` method, with two (keyword) arguments:
``distinct`` (with possible values ``True`` and
``False``) and ``limit`` (which is either a positive
integer or ``None``). For example:

.. sourcecode:: python

    select       = ("?a","?b","?c","?d")
    where        = GraphPattern([("?a",P,"?x"),[(Q,"?b","?a"),("?x",R,"?c")])
    opt          = GraphPattern([("?x",S,"?d")])
    resultObject = sparqlGr.queryObject(where,opt)
    result       = resultObject.select(select,distinct=True,limit=5)


returns the first 5 query results, all distinct from one another. The
default for ``distinct`` is set ``True`` and the
``limit`` is ``None``. Ie, the
:meth:`~rdfextras.sparql.Query.query` is, in fact, a shorthand for
**queryObject(where,...).select(select)** (it is
probably the most widespread use of ``select`` hence this shorthand
method).

Note that it is possible to use the same class instance returned by
:meth:`~rdfextras.sparql.Query.queryObject` to run different selections (though the SPARQL draft
does not make this distinction); in other words, running the
:meth:`~rdfextras.sparql.Query.Query.select` method does not change any internal variable of the
class.

CONSTRUCT Forms
----------------

The construct method can be invoked either with an explicit Graph Pattern
or without (the latter corresponds to the ``CONSTRUCT *`` of the
draft, the former to the case when a separate ``CONSTRUCT`` pattern
is defined). In both cases, a separate :class:`~rdfextras.sparql.sparqlGraph.SPARQLGraph` instance is
returned containing the constructed triples. For example, the construction in
the draft:

.. sourcecode:: sparql

    CONSTRUCT { &lt;http://example.org/person#Alice&gt; FN ?name }
    WHERE     { ?x nm ?name }


corresponds to the ``sparql-p`` construction:

.. sourcecode:: python

    where            = GraphPattern([("?x",nm,"?name"])
    constructPattern = GraphPattern([(URIRef(
                            "http://example.org/person#Alice"),FN,"?name")])
    resultObject     = sparqlGr.queryObject(where)
    result           = resultObject.construct(constructPattern)


whereas the example:

.. sourcecode:: python

    CONSTRUCT * WHERE (?x N ?name)


corresponds to:

.. sourcecode:: python

    where        = GraphPattern([("?x",N,"?name"])
    resultObject = sparqlGr.queryObject(where)
    result       = resultObject.construct() # or resultObject.construct(None)


DESCRIPTION Forms
-----------------

The current draft is pretty vague as to what this facility is (and leaves
is to the implementor). What ``SPARQLGraph`` implements is a form of
clustering. The :meth:`~rdfextras.sparql.Query.Query.describe` method has a ``seed``
argument (to serve as a seed for clustering) and two keyword arguments,
``forward`` and ``backward``, each a boolean. What it
means:

* ``forward=True`` and ``backward=False`` generates a triple store
    with a transitive closure for each result of the query and the seed:
    take, recursively, all the properties and objects that start by a
    specific resource.
* ``forward=False`` and ``backward=True`` the same as ``forward`` but in the 'other direction'.
* ``forward=True`` and ``backward=True`` combines the two into one triple store.
* ``forward=False`` and ``backward=False`` returns and empty triple store.

ASK Forms
---------

The SPARQL draft refers to an ``ASK`` query form., which simply
says whether the set of patterns represent a non-empty subgraph. This is done
by:

.. sourcecode:: python

    resultObject = sparqlGr.queryObject(where)
    result       = resultObject.ask() 


The :meth:`~rdfextras.sparql.Query.Query.ask` method returns False or True (whether the resulting
subgraph is empty or not, respectively).

Datatype lexical representations
================================
The current implementation does not (yet) do a full implementation of all
the datatypes with the precise lexical representation as defined in the XML
Schema Datatype document (and referred to in the SPARQL document). In theory,
these should be taken care of by the underlying RDFLib layer when parsing
strings into datatypes, but it does not happen yet. ``sparql-p``
does a partial conversion to have the vast majority of queries running
properly, but there are some restrictions:

* ``string``: Implemented and coded in UTF-8
* ``integer, float, long``: Implemented as required
* ``double``: As Python does not know doubles, it is mapped to floats
* ``decimal``: As Python does not know general decimals, mapped to integers
* ``date``: The format is YYYY-MM-DD. The optional timezone character (allowed by the XML Schema document) is not implemented when interpreting ``Literal``-s as date.
* ``time``: The format is  HH:MM:SS. The optional microsecond and timezone characters (allowed by the XML Schema document) are not implemented when interpreting ``Literal``-s as time.
* ``dateTime``: The format is YYYY-MM-DDTHH:MM:SS (ie, the combination of date and time with a separator 'T'). No microseconds or timezone characters are implemented when interpreting a ``Literal`` as a ``dateTime``.

These mappings are used when a typed literal value is specified in a Graph
pattern, and a :class:`~rdflib.term.Literal` instance is generated on-the-fly: the
:class:`~rdflib.term.Literal` instance uses these lexical representations and the
corresponding XML Schema datatype are stored. When comparing values coming
from an RDF data and parsed by RDFLib, these lexical representations are
pre-supposed when comparing :class:`~rdflib.term.Literal` instances.

Operators
=========
SPARQL defines a number of possible operators for the AND clause. It is
not obvious at this point which of those should be left to a parser and which
of those should be implemented by the engine. ``sparql-p`` provides
a number of methods that can be used to create an elementary operator and
that can also be used in the AND clause. More complex constructions can be
done using Python’s ``lambda`` function, for example.

The available binary operator functions are: :func:`~rdfextras.sparql.sparqlOperators.lt` (for less
than), :func:`~rdfextras.sparql.sparqlOperators.le` (for less or equal), :func:`~rdfextras.sparql.sparqlOperators.gt` (for greater
than), :func:`~rdfextras.sparql.sparqlOperators.ge` (for greater or equal), and :func:`~rdfextras.sparql.sparqlOperators.eq` (for
equal). Each of these operator methods take two parameters, which are both
either a query string or a typed value, and each of these operators return a
*function* that can be plugged into a global constraint. (All these
methods should be imported from the
:mod:`~rdfextras.sparql.sparqlOperators` module.) For example, to add the
constraint:

.. sourcecode:: python

    FILTER ?m &lt; 42 


one can use:

.. sourcecode:: python

    constraints = [ lt("?m",42) ]


For the more complex case of the form:

.. sourcecode:: python

    FILTER ?m &lt; 42 || ?n &gt; 56


the ``lambda`` construction can be used:

.. sourcecode:: python

    constraints = [ lambda binding: lt("?m",42)(binding) or gt("?n",56)(binding) ]


The complicated case of how values of different types compare is left
completely to Python for the time being. If a comparison does not make sense,
the return value is ``False``. When the Working Group gets to an
equilibrium point on this issue,  this should be compared to what Python
does but this is currently a matter of debate in the group, too.

The module also offers a special operator called
:func:`~rdfextras.sparql.isOnCollection` that can be used as a global constraint to check
whether a resource is on a collection or not.

The SPARQL document  also `defines <http://www.w3.org/TR/rdf-sparql-query/#operandDataTypes>`_ a
number of special operators. The following of those operators are
implemented: :func:`~rdfextras.sparql.sparqlOperators.bound`, :func:`~rdfextras.sparql.sparqlOperators.isURI`, 
:func:`~rdfextras.sparql.sparqlOperators.isBlank`, :func:`~rdfextras.sparql.sparqlOperators.isLiteral`, 
:func:`~rdfextras.sparql.sparqlOperators.str`, :func:`~rdfextras.sparql.sparqlOperators.lang`,
:func:`~rdfextras.sparql.sparqlOperators.datatype`. For example:

.. sourcecode:: python

    pattern.addConstraint(isURI("?mbox"))


adds a constraint that the value bound to ``?mbox`` *must*
be a real URI (as opposed to a literal), or

.. sourcecode:: python

    pattern.addConstraint( lambda binding: datatype("?d")(binding) == \\
    	"http://www.myexampledatatype.org" )


checks whether the datatype of a bound resource is of a specific URI.

Whether this set of elementary operators is enough or not for
the complete implementation of SPARQL is not yet clear. I presume the final
answer will come when somebody writes a parser to the query language...

The :mod:`~rdfextras.sparql.sparqlOperators` module in the
package includes some methods that might be useful in creating more complex
constraint methods, such as :func:`~rdfextras.sparql.sparqlOperators.getLiteralValue` (to return the value
of a :class:`~rdflib.term.Literal`, possibly making on-the-fly conversion for the known datatypes),
or :func:`~rdfextras.sparql.sparqlOperators.getValue` (to create a 'retrieval' method to return either the
original Resource or a bound resource in case of a query string parameter).
Look at the detailed method description for details.

Implementation
==============
The implementation of SPARQL is based on an expansion tree. Each layer in
the tree takes care of a statement in the ``WHERE`` clause, starting
by the first for the first layer, then the second statement for the second
layer, etc. Once the full expansion is done, the results for
``SELECT`` are collected by visiting the leaves. In more details:

The root of the tree is created by handing over the full list of
statements, and a dictionary with the variable bindings. Initially, this
dictionary looks like 

.. sourcecode:: sparql

    {"?x": None, "?a" : None, ...}

The node picks the first tuple in the ``where``, replaces all unbound
variables by ``None`` and makes a RDFLib query to the triple store.
The result are all tuples in the triple store that conform to the pattern
expressed by the first ``where`` pattern tuple. *For each of
those* a child node is created, by handing over the rest of the triples
in the ``where`` clause, and a binding where some of the
``None`` values are replaced by 'real' RDF resources. The children
follow the same process recursively. There are several ways for the recursion
to stop:

* though there is still a ``where`` pattern to handle, no tuples
  are found in the triple store in the process. This means that the
  corresponding branch does not produce valid results. (In the
  implementation, such a node is marked as 'clashed'). The same happens if,
  though a tuple is found, that tuple is rejected by the constraint
  function assigned to this tuple (the "per-tuple" constraint).
* though there are no statements to process any more in the
  ``where`` clause, there are still unbound variables
* all variables are bound and there are no more patterns to process.
  Unless one of the global constraints reject this binding this yields
  'successful' leaves.

The third type of leaf contains a valid, possible query result for the
unbound variables. Once the expansion is complete, the collection of the
results becomes obvious: successful leaves are visited to return their
results as the binding for the variables appearing in the ``select``
clause; the non-leaf nodes simply collect and combine the results of their
children.

The implementation of the 'optional' feature
follows the semantic description. A pre-processing step separates the
'regular' and 'optional' ``select`` and ``where`` clauses.
First a regular expansion is done; then, separate optional expansions (for
each optional clauses) are attached to each *successful* leaf node
(obviously, by binding all variables that can be bound on that level). The
collection of the result follows the same mechanism except that if the
optional expansion tree yields no results, the real result tuples are padded
by the necessary number of ``None``-s.

:author: Ivan Herman ivan@ivan-herman.net
:date: 2005/10/10 15:40:35

This software is available for use under the `W3C Software License <http://www.w3.org/Consortium/Legal/2002/copyright-software-20021231>`_.
