.. _rdfmodelling: RDFExtras, store implementations.

=========================================================================
RDF Modelling: a Relational Model for FOL Persistence
=========================================================================

The :mod:`~rdfextras.store.FOPLRelationModel` module implements a relational model for Notation 3 
abstract syntax. Contributor: Chimezie Ogbuji.

In essence, this is an open-source, maximally efficient RDBM upon which large
volume RDF can be persisted, within named graphs, with the ability to persist
Notation 3 formulae in a seperate manner (consistent with Notation 3 semantics).
The module is  called the "FOPLRelationModel" because although it is specifically
a relational model for Notation 3 syntax, it covers much of the requirement for
the syntactic representation of First Order Logic in general.

Discussion and design rationale
===============================

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
The first method with the most impact was separating Assertional Box
statements (statements of class membership) from the rest of the Knowledge
Base. When I say Knowledge Base, I mean a 'named' aggregation of all the named
graphs in an RDF database. Partitioning the Table space has a universal effect
on shortening indices and reducing the average number of rows needed to be
scanned for even the worst-case scenario for a SQL optimizer. The nature of
RDF data (at the syntactic level) is a major factor. RDF is a Description
Logic-oriented representation and thus relies heavily on statements of class
membership.

The relational model is all about representing everything as specific
relations and the 'instantiation' relationship is a perfect candidate for a
database table.

Eventually, it made sense to create additional table partitions for:

* RDF statments between resources (where the object is not an RDF ``Literal``).
* RDF's equivalent to EAV statements (where the object is a value or RDF ``Literal``).
* Matching Triple Patterns against these partitions can be expressed using a decision tree which accomodates every combination of RDF terms. For example, a triple pattern:

.. sourcecode:: text

    ?entity foaf:name "Ikenna"

Would only require a scan through the indices for the EAV-type RDF statements
(or the whole table if necessary - but that decision is up to the underlying
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

For example, the ``Object`` term of an EAV-type RDF statment doesn't need an
associated column for the kind of term it is (the relation is explicitely
defined as those RDF statements where the Object is a Literal - ``L``)

Efficient Skolemization with Hashing
------------------------------------
Finally. thanks to Benjamin Nowack's related efforts with ARC - a PHP-based
implementation of an RDF / SPARQL storage system, Mark Nottinghams suggestion,
and an earlier paper by Stephen Harris and Nicholas Gibbins: `3store: Efficient
Bulk RDF Storage <http://citeseer.ist.psu.edu/harris03store.html>`_, a final method of using a half-hash (MD5 hash) of the RDF
identifiers in the 'statement' tables was employed instead. The statements
table each used an unsigned MySQL ``BIGint`` to encode the half hash in base 10
and use as foreign keys to two separate tables:

* A table for identifiers (with a column that enumerated the kind of identifier it was)
* A table for literal values

The key to both tables was the 16-byte unsigned integer which represented the half-hash

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

Contents:
=========

:mod:`~rdfextras.store.FOPLRelationalModel.BinaryRelationPartition`
-------------------------------------------------------------------

The set of classes used to model the 3 'partitions' for N3 assertions.

There is a top level class which implements operations common to all
partitions as well as a class for each partition. These classes are meant to
allow the underlying SQL schema to be completely configurable as well as to
automate the generation of SQL queries for adding, updating, removing and 
resolving triples to/from/in the partitions. 

These classes work in tandem with the RelationHashes to automate all (or most)
of the SQL processing associated with this FOPL Relational Model

.. note:: The use of foreign keys (which - unfortunately - bumps the `minimum MySQL version to 5.0 <http://dev.mysql.com/doc/refman/5.0/en/ansi-diff-foreign-keys.html>`_) allows for the efficient removal of all statements about a particular resource using cascade on delete (although this is currently not used).

This is the common ancestor of the three partitions for assertions. It implements 
behavior common to all 3.  Each subclass is expected to define the following:

*nameSuffix* - The suffix appended to the name of the table

*termEnumerations* - a 4-item list (for each quad 'slot') of lists (or None)
    which enumerate the allowable term types for each quad slot (one of 
    ``U`` - URIs, ``V`` - Variable, ``L`` - Literals, ``B`` - BNodes, ``F`` - Formulae)

*columnNames* - a list of column names for each quad slot (can be of 
    additional length where each item is a 3-item tuple of:
    column name, column type, index)

*columnIntersectionList* - a list of 2-item tuples (the quad index and a 
    boolean indicating whether or not the associated term is an identifier)
    this list (the order of which is very important) is used for 
    generating intersections between the partition and the identifier / 
    value hash

*hardCodedResultFields* - a dictionary mapping quad slot indices to their 
    hardcoded value (for partitions - such as ABOX - which have a 
    hardcoded value for a particular quad slot)

*hardCodedResultTermsTypes* - a dictionary mapping quad slot indices to 
    their hardcoded term type (for partitions - such as Literal 
    properties - which have hardcoded values for a particular quad slot's
    term type)

:mod:`~rdfextras.store.FOPLRelationalModel.QuadSlot`
-----------------------------------------------------

Utility functions associated with RDF terms:

* normalizing (to 64 bit integers via half-md5-hashes)
* escaping literals for SQL persistence


:mod:`~rdfextras.store.FOPLRelationalModel.RelationalHash`
----------------------------------------------------------

This module implements two hash tables for identifiers and values that
facilitate maximal index lookups and minimal redundancy (since identifiers and
values are stored once only and referred to by integer half-md5-hashes). 

The identifier hash uses the half-md5-hash (converted by base conversion to an
integer) to key on the identifier's full lexical form (for partial matching by
REGEX) and their term types.

The use of a half-hash introduces a collision risk that is currently not
accounted for.

The volume at which the risk becomes significant is calculable, though through
the `birthday paradox <http://en.wikipedia.org/wiki/Birthday_Paradox>`_.

The value hash is keyed off the half-md5-hash (as an integer also) and stores
the identifier's full lexical representation (for partial matching by REGEX)

These classes are meant to automate the creation, management, linking,
insertion of these hashes (by SQL) automatically.

:mod:`~rdfextras.store.FOPLRelationalModel.MySQLMassLoader` - Bulk loading
--------------------------------------------------------------------------

If you need to load a large number of RDF statements into an empty database,
RDFLib provides a module that can be run as a script to help you with this
task. You can run this module with the command 

.. sourcecode:: bash

    $ python -m \
        rdfextras.store.FOPLRelationalModel.MySQLMassLoader [options] <DB Type> 

Note that several of the options are very important. 

Let's start with an example. 

If you wanted to load the RDF/XML file :file:`profiles.rdf` and the N-Triples
file :file:`targets.nt` into an empty MySQL database named 'plan' located at 
host 'bubastis', accessible to user 'ozymandias' with password 'ramsesIII',
you could use the following command:

.. sourcecode:: bash

    $ python -m rdfextras.store.FOPLRelationalModel.MySQLMassLoader \
      -c db=plan,host=bubastis,user=ozymandias,password=ramsesIII \
      -i plan \
      -x profiles.rdf --nt=targets.nt \
      MySQL

Here, we're connecting to a MySQL database, but this script can also utilize a
PostgreSQL database with the 'PostgreSQL' keyword. 

The ``-c`` option allows you to specify the connection details for the target
database; it is a comma-separated string of variable assignments, as in the
example above. As in that example, it can specify the database with 'db', the
name of the target machine with 'host', the username with 'user', and the
password for that user with 'password'.

Also, you can specify the port on the target machine with 'port'. A single
database can support multiple RDF stores; each such store has an additional
store "identifier", which you must provide with the ``-i`` option.

Once we have connected, we can load data from files that can be in various
formats. This script supports identifying RDF/XML files to load with the ``-x``
option, TriX files with the ``-t`` option, N3 files with the ``-n`` option, 
N-Triples files with the ``--nt`` option, and RDFa files with the ``-a`` 
option. 

In addition, you can load all the files in a directory, assuming that they all
have the same format. To do this, use the ``--directory`` option to identify
the directory containing the files, and the ``--format`` option to specify the
format of the files in that directory.

There are a few advanced options available for this script; you can use the 
``-h`` option to get a summary of all the available options.


Typical Usage
=============

Typical usage is via module import in order to support the development of
an implementation of an RDFLib Store, such as in the MySQL Store, from which
the following illustration is drawn:

.. sourcecode:: python

    from FOPLRelationalModel.BinaryRelationPartition import AssociativeBox
    from FOPLRelationalModel.BinaryRelationPartition import NamedLiteralProperties
    from FOPLRelationalModel.BinaryRelationPartition import NamedBinaryRelations
    from FOPLRelationalModel.BinaryRelationPartition import BinaryRelationPartitionCoverage
    from FOPLRelationalModel.BinaryRelationPartition import PatternResolution
    from FOPLRelationalModel.QuadSlot import genQuadSlots
    from FOPLRelationalModel.QuadSlot import normalizeNode
    from FOPLRelationalModel.RelationalHash import IdentifierHash
    from FOPLRelationalModel.RelationalHash import LiteralHash
    from FOPLRelationalModel.RelationalHash import GarbageCollectionQUERY

    class SQL(Store):
        """
        Abstract SQL implementation of the FOPL Relational Model as an RDFLib
        Store.
        """
        context_aware = True
        formula_aware = True
        transaction_aware = True
        regex_matching = NATIVE_REGEX
        batch_unification = True
        def __init__(
                     self, identifier=None, configuration=None,
                     debug=False, engine="ENGINE=InnoDB",
                     useSignedInts=False, hashFieldType='BIGINT unsigned',
                     declareEnums=False, perfLog=False,
                     optimizations=None,
                     scanForDatatypes=False):
            self.dataTypes={}
            self.scanForDatatypes=scanForDatatypes
            self.optimizations=optimizations
            self.debug = debug
            if debug:
                self.timestamp = TimeStamp()
            
            #BE: performance logging
            self.perfLog = perfLog
            if self.perfLog:
                self.resetPerfLog()
            
            self.identifier = identifier and identifier or 'hardcoded'
            
            #Use only the first 10 bytes of the digest
            self._internedId = INTERNED_PREFIX + sha1(self.identifier).hexdigest()[:10]
            
            self.engine = engine
            self.showDBsCommand = 'SHOW DATABASES'
            self.findTablesCommand = "SHOW TABLES LIKE '%s'"
            self.findViewsCommand = "SHOW TABLES LIKE '%s'"
            # TODO: Note, the following three members are MySQL-specific, and
            # must be overridden for other databases.
            self.defaultDB = 'mysql'
            self.default_port = 3306
            self.select_modifier = 'straight_join'
            self.can_cast_bigint = False
            
            self.INDEX_NS_BINDS_TABLE = \
                'CREATE INDEX uri_index on %s_namespace_binds (uri(100))'
            
            #Setup FOPL RelationalModel objects
            self.useSignedInts = useSignedInts
            # TODO: derive this from `self.useSignedInts`?
            self.hashFieldType = hashFieldType
            self.idHash = IdentifierHash(self._internedId,
                self.useSignedInts, self.hashFieldType, self.engine, declareEnums)
            self.valueHash = LiteralHash(self._internedId,
                self.useSignedInts, self.hashFieldType, self.engine, declareEnums)
            self.binaryRelations = NamedBinaryRelations(
                self._internedId, self.idHash, self.valueHash, self,
                self.useSignedInts, self.hashFieldType, self.engine, declareEnums)
            self.literalProperties = NamedLiteralProperties(
                self._internedId, self.idHash, self.valueHash, self,
                self.useSignedInts, self.hashFieldType, self.engine, declareEnums)
            self.aboxAssertions = AssociativeBox(
                self._internedId, self.idHash, self.valueHash, self,
                self.useSignedInts, self.hashFieldType, self.engine, declareEnums)
            
            self.tables = [
                           self.binaryRelations,
                           self.literalProperties,
                           self.aboxAssertions,
                           self.idHash,
                           self.valueHash
                           ]
            self.createTables = [
                           self.idHash,
                           self.valueHash,
                           self.binaryRelations,
                           self.literalProperties,
                           self.aboxAssertions
                           ]
            self.hashes = [self.idHash,self.valueHash]
            self.partitions = [self.literalProperties,self.binaryRelations,self.aboxAssertions,]
            
            #This is a dictionary which caputures the relationships between
            #the each view, it's prefix, the arguments to viewUnionSelectExpression
            #and the tables involved
            self.viewCreationDict={
                '_all'                       : (False,self.partitions),
                '_URI_or_literal_object'     : (False,[self.literalProperties,
                                                       self.binaryRelations]),
                '_relation_or_associativeBox': (True,[self.binaryRelations,
                                                      self.aboxAssertions]),
                '_all_objects'               : (False,self.hashes)
            }
            
            #This parameter controls how exlusively the literal table is searched
            #If true, the Literal partition is searched *exclusively* if the object term
            #in a triple pattern is a Literal or a REGEXTerm.  Note, the latter case
            #prevents the matching of URIRef nodes as the objects of a triple in the store.
            #If the object term is a wildcard (None)
            #Then the Literal paritition is searched in addition to the others
            #If this parameter is false, the literal partition is searched regardless of what the object
            #of the triple pattern is
            self.STRONGLY_TYPED_TERMS = False
            self._db = None
            if configuration is not None:
                #self.open(configuration)
                self._set_connection_parameters(configuration=configuration)
            
            
            self.cacheHits = 0
            self.cacheMisses = 0
            
            self.literalCache = {}
            self.uriCache = {}
            self.bnodeCache = {}
            self.otherCache = {}
            
            self.literal_properties = set()
            '''set of URIRefs of those RDF properties which are known to range
            over literals.'''
            self.resource_properties = set()
            '''set of URIRefs of those RDF properties which are known to range
            over resources.'''
            
            #update the two sets above with defaults
            if False: # TODO: Update this to reflect the new namespace layout
                self.literal_properties.update(OWL.literalProperties)
                self.literal_properties.update(RDF.literalProperties)
                self.literal_properties.update(RDFS.literalProperties)
                self.resource_properties.update(OWL.resourceProperties)
                self.resource_properties.update(RDF.resourceProperties)
                self.resource_properties.update(RDFS.resourceProperties)
            
            self.length = None
    # [ ... ]

    class MySQL(SQL):
        """
        MySQL implementation of FOPL Relational Model as an rdflib Store
        """
        # node_pickler = None
        # __node_pickler = None
        _Store__node_pickler = None
        try:
            import MySQLdb
            def _connect(self, db=None):
                if db is None:
                    db = self.config['db']
                return MySQL.MySQLdb.connect(
                         user=self.config['user'],
                         passwd=self.config['password'], db=db,
                         port=self.config['port'], host=self.config['host'])
            
        except ImportError:
            def _connect(self, db=None):
                raise NotImplementedError(
                    'We need the MySQLdb module to connect to MySQL databases.')
            
        
        def _createViews(self,cursor):
            for suffix, (relations_only, tables) in self.viewCreationDict.items():
                query = ('CREATE SQL SECURITY INVOKER VIEW %s%s AS %s' %
                        (self._internedId, suffix, ' UNION ALL '.join(
                            [t.viewUnionSelectExpression(relations_only)
                            for t in tables])))
                if self.debug:
                    print >> sys.stderr, "## Creating View ##\n",query
                self.executeSQL(cursor, query)



|today|




