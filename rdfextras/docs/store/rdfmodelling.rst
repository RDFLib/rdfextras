.. _rdfmodelling: RDFExtras, store implementations.

|today|

=============
RDF Modelling
=============

Contents:

.. toctree::
   :maxdepth: 2

:mod:`rdfextras.store.FOPLRelationalModel`
-------------------------------------------

A First Order Predicate Logic Relational Model. See also :mod:`foplrelmodel`

:mod:`rdfextras.store.FOPLRelationalModel.MySQLMassLoader`
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Bulk loading
^^^^^^^^^^^^^

If you need to load a large number of RDF statements into an empty database,
RDFLib provides a module that can be run as a script to help you with this
task. You can run this module with the command 

.. sourcecode:: bash

    $ python -m \
        rdflib.store.FOPLRelationalModel.MySQLMassLoader [options] <DB Type> 

Note that several of the options are very important. 

Let's start with an example. 

If you wanted to load the RDF/XML file :file:`profiles.rdf` and the N-Triples
file :file:`targets.nt` into an empty MySQL database named 'plan' located at 
host 'bubastis' accessible to user 'ozymandias' with password 'ramsesIII',
you could use the following command:

.. sourcecode:: bash

    $ python -m rdflib.store.FOPLRelationalModel.MySQLMassLoader \
      -c db=plan,host=bubastis,user=ozymandias,password=ramsesIII \
      -i plan \
      -x profiles.rdf --nt=targets.nt \
      MySQL

Here, we're connecting to a MySQL database, but this script can also utilize a
PostgreSQL database with the 'PostgreSQL' keyword. 

The -c option allows you to specify the connection details for the target
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

:mod:`~rdfextras.store.FOPLRelationalModel.BinaryRelationPartition`
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

The set of classes used to model the 3 'partitions' for N3 assertions.

There is a top level class which implements operations common to all
partitions as well as a class for each partition. These classes are meant to
allow the underlying SQL schema to be completely configurable as well as to
automate the generation of SQL queries for adding,updating,removing,resolving
triples from the partitions. 

These classes work in tandem with the RelationHashes to automate all (or most)
of the SQL processing associated with this FOPL Relational Model

NOTE: The use of foreign keys (which - unfortunately - bumps the minimum MySQL
version to 5.0) allows for the efficient removal of all statements about a
particular resource using cascade on delete (currently not used)

see: http://dev.mysql.com/doc/refman/5.0/en/ansi-diff-foreign-keys.html


BinaryRelationPartition
^^^^^^^^^^^^^^^^^^^^^^^
The common ancestor of the three partitions for assertions.

Implements behavior common to all 3.  Each subclass is expected to define
the following:

nameSuffix - The suffix appended to the name of the table

termEnumerations - a 4 item list (for each quad 'slot') of lists (or None)
    which enumerate the allowable term types for each quad slot (one of 
    'U' - URIs, 'V' - Variable, 'L' - Literals, 'B' - BNodes, 'F' - Formulae)

columnNames - a list of column names for each quad slot (can be of 
    additional length where each item is a 3-item tuple of:
    column name, column type, index)

columnIntersectionList - a list of 2 item tuples (the quad index and a 
    boolean indicating whether or not the associated term is an identifier)
    this list (the order of which is very important) is used for 
    generating intersections between the partition and the identifier / 
    value hash

hardCodedResultFields - a dictionary mapping quad slot indices to their 
    hardcoded value (for partitions - such as ABOX - which have a 
    hardcoded value for a particular quad slot)

hardCodedResultTermsTypes - a dictionary mapping quad slot indices to 
    their hardcoded term type (for partitions - such as Literal 
    properties - which have hardcoded values for a particular quad slot's
    term type)

:mod:`~rdfextras.store.FOPLRelationalModel.QuadSlot`
++++++++++++++++++++++++++++++++++++++++++++++++++++

Utility functions associated with RDF terms:

* normalizing (to 64 bit integers via half-md5-hashes)
* escaping literals for SQL persistence


:mod:`~rdfextras.store.FOPLRelationalModel.RelationalHash`
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

This module implements two hash tables for identifiers and values that
facilitate maximal index lookups and minimal redundancy (since identifiers and
values are stored once only and referred to by integer half-md5-hashes). 

The identifier hash uses the half-md5-hash (converted by base conversion to an
integer) to key on the identifier's full lexical form (for partial matching by
REGEX) and their term types.

The use of a half-hash introduces a collision risk that is currently not
accounted for.

The volume at which the risk becomes significant is calculable, though through
the 'birthday paradox'.

The value hash is keyed off the half-md5-hash (as an integer also) and stores
the identifier's full lexical representation (for partial matching by REGEX)

These classes are meant to automate the creation, management, linking,
insertion of these hashes (by SQL) automatically

see: http://en.wikipedia.org/wiki/Birthday_Paradox

