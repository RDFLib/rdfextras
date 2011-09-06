.. _foplrelmodel: RDFExtras storage

|today|

=================================================================================
:mod:`~rfdextras.store.FOPLRelationModel`, a Relational Model for FOL Persistence
=================================================================================

`Original post <http://copia-test.posterous.com/a-relational-model-for-fol-persistance>`_ by `Chimezie Ogbuji <http://posterous.com/people/10xO4b8IeU9>`_

A short while ago I was rather engaged in investigating the most efficient way
to persist RDF on Relational Database Management Systems. One of the outcomes
of this effort that I have yet to write about is a relational model for
Notation 3 abstract syntax and a fully funcitoning implementation - which is
now part of RDFLib's MySQL drivers.

It's written in with Soft4Science's SciWriter and seems to render natively in
Firefox alone (havne't tried any other browser)

Originally, I kept coming at it from a pure Computer Science approach
(programming and datastructures) but eventually had to roll my sleeves and get
down to the formal logic level (i.e., the Deconstructionist, Computer Engineer
approach).

Partitioning the KR Space
-------------------------
The first method with the most impact was seperating Assertional Box
statements (statements of class membership) from the rest of the Knowledge
Base. When I say Knowledge Base, I mean a 'named' aggregation of all the named
graphs in an RDF database. Partitioning the Table space has a universal effect
on shortening indices and reducing the average number of rows needed to be
scanned for even the worts case scenario for a SQL optimizer. The nature of
RDF data (at the syntactic level) is a major factor. RDF is Description
Logics-oriented representation and thus relies heavily on statements of class
membership.

The relational model is all about representing everything as specific
relations and the 'instanciation' relationship is a perfect candidate for a
database table.

Eventually, it made sense to create additional table partitions for:

* RDF statments between resources (where the object is not an RDF Literal).
* RDF's equivalent to EAV statements (where the object is a value or RDF Literal).
* Matching Triple Patterns against these partitions can be expressed using a decision tree which accomodates every combination of RDF terms. For example, a triple pattern:

.. sourcecode:: sparql

    ?entity foaf:name "Ikenna"

Would only require a scan through the indices for the EAV-type RDF statements
(or the whole table if neccessary - but that decision is up to the underlying
SQL optimizer).

Using Term Type Enumerations
----------------------------
The second method involves the use of the enumeration of all the term types as
an additional column whose indices are also available for a SQL query
optimizer. That is:

.. sourcecode:: text

    ANY_TERM = ['U','B','F','V','L']

The terms can be partitioned into the exact allowable set for certain kinds of
RDF terms:

.. sourcecode:: text

    ANY_TERM = ['U','B','F','V','L']
    CONTEXT_TERMS   = ['U','B','F']
    IDENTIFIER_TERMS   = ['U','B']
    GROUND_IDENTIFIERS = ['U']
    NON_LITERALS = ['U','B','F','V']
    CLASS_TERMS = ['U','B','V']
    PREDICATE_NAMES = ['U','V']

    NAMED_BINARY_RELATION_PREDICATES = GROUND_IDENTIFIERS
    NAMED_BINARY_RELATION_OBJECTS    = ['U','B','L']

    NAMED_LITERAL_PREDICATES = GROUND_IDENTIFIERS
    NAMED_LITERAL_OBJECTS    = ['L']

    ASSOCIATIVE_BOX_CLASSES    = GROUND_IDENTIFIERS

For example, the Object term of an EAV-type RDF statment doesn't need an
associated column for the kind of term it is (the relation is explicitely
defined as those RDF statements where the Object is a Literal - L)

Efficient Skolemization with Hashing
------------------------------------
Finally. thanks to Benjamin Nowack's related efforts with ARC - a PHP-based
implementation of an RDF / SPARQL storage system, Mark Nottinghams suggestion,
and an earlier paper by Stephen Harris and Nicholas Gibbins: 3store: Efficient
Bulk RDF Storage, a final method of using a half-hash (MD5 hash) of the RDF
identifiers in the 'statement' tables was employed instead. The statements
table each used an unsigned MySQL BIGint to encode the half hash in base 10
and use as foreign keys to two seperate tables:

* A table for identifiers (with a column that enumerated the kind of identifier it was)
* A table for literal values

The key to both tables was the 16 byte unsigned integer which represented the half-hash

This of course introduces a possibility of collision (due to the reduced hash
size), but by hashing the identifier along with the term type, this further
dilutes the lexical space and reduces this collision risk. This latter part is
still a theory I haven't formally proven (or disproven) but hope to. At the
maximum volume (around 20 million RDF assertions) I can resolve a single
triple pattern in 8 seconds on an SGI machine and there is no collision - the
implementation includes (disabled by default) a collision detection mechanism.

The implementation includes all the magic needed to generate SQL statements to
create, query, and manage indices for the tables in the relational model. It
does this from a Python model that encapsulates the relational model and
methods to carry out the various SQL-level actions needed by the underlying
DBMS.

For me, it has satisfied my needs for an open-source maximally efficient RDBM
upon which large volume RDF can be persisted, within named graphs, with the
ability to persist Notation 3 formulae in a seperate manner (consistent with
Notation 3 semantics).

I called the Python module ``FOPLRelationModel`` because although it is
specifically a relational model for Notation 3 syntax it covers much of the
requirements for the syntactic representation of First Order Logic in general.


Modules and contents
---------------------

.. currentmodule:: rdfextras.store.FOPLRelationalModel

:mod:`~rdfextras.store.FOPLRelationalModel.BinaryRelationPartition`
-------------------------------------------------------------------
.. automodule:: rdfextras.store.FOPLRelationalModel.BinaryRelationPartition
.. autoclass:: BinaryRelationPartition
   :members:
.. autoclass:: AssociativeBox
   :members:
.. autoclass:: NamedLiteralProperties
   :members:
.. autoclass:: NamedBinaryRelations
   :members:
.. autofunction:: BinaryRelationPartitionCoverage
.. autofunction:: PatternResolution


:mod:`~rdfextras.store.FOPLRelationalModel.QuadSlot`
-------------------------------------------------------------------
.. automodule:: rdfextras.store.FOPLRelationalModel.QuadSlot
.. autoclass:: QuadSlot
   :members:
.. autofunction:: EscapeQuotes
.. autofunction:: dereferenceQuad
.. autofunction:: genQuadSlots
.. autofunction:: normalizeValue
.. autofunction:: makeSigned
.. autofunction:: normalizeNode

:mod:`~rdfextras.store.FOPLRelationalModel.RelationalHash`
-------------------------------------------------------------------
.. automodule:: rdfextras.store.FOPLRelationalModel.RelationalHash
.. autoclass:: Table
   :members:
.. autoclass:: RelationalHash
   :members:
.. autoclass:: IdentifierHash
   :members:
.. autoclass:: LiteralHash
   :members:
.. autofunction:: GarbageCollectionQUERY

:mod:`~rdfextras.store.FOPLRelationalModel.MySQLMassLoader`
-------------------------------------------------------------------
.. automodule:: rdfextras.store.FOPLRelationalModel.MySQLMassLoader
.. autoclass:: Loader
   :members:
.. autoclass:: MySQLLoader
   :members:
.. autoclass:: PostgreSQLLoader
   :members:
