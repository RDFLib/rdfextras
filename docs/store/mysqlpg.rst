.. _rdfextras_storage_mysqlpg: RDFExtras storage MySQLPg

|today|

================================================================
Summary Overview of using MySQL or PostgreSQL as a triple store.
================================================================

Introduction
------------

The RDFLib 3 plugin interface supports using either a MySQL or PostgreSQL
database to store and query your RDF graphs. This document describes how to
use these backends, from loading large datasets into them to taking advantage
of their query capabilities.

Bulk loading
------------
If you need to load a large number of RDF statements into an empty database,
RDFLib provides a module that can be run as a script to help you with this
task. You can run this module with the command 

.. sourcecode:: bash

    $ python -m rdfextras.store.FOPLRelationalModel.MySQLMassLoader [options] <DB Type>; 

note that several of the options are very important. Let's start with an example.

If you wanted to load the RDF/XML file ``profiles.rdf`` and the N-Triples file
``targets.nt`` into an empty MySQL database named ``plan`` located at host
``bubastis`` accessible to user ``ozymandias`` with password ``ramsesIII``, you
could use the following command:

.. sourcecode:: bash

    $ python -m rdflib.store.FOPLRelationalModel.MySQLMassLoader \
      -c db=plan,host=bubastis,user=ozymandias,password=ramsesIII \
      -i plan \
      -x profiles.rdf --nt=targets.nt \
      MySQL

Here, we're connecting to a MySQL database, but this script can also utilize a
PostgreSQL database with the ``PostgreSQL`` keyword. The ``-c`` option allows you
to specify the connection details for the target database; it is a
comma-separated string of variable assignments, as in the example above. As in
that example, it can specify the database with ``db``, the name of the target
machine with ``host``, the username with ``user``, and the password for that user
with ``password``. Also, you can specify the port on the target machine with
``port``. 

A single database can support multiple RDF stores; each such store has
an additional store "identifier", which you must provide with the ``-i`` option.

Once we have connected, we can load data from files that can be in various
formats. This script supports identifying RDF/XML files to load with the `-x`
option, TriX files with the `-t` option, N3 files with the `-n` option,
N-Triples files with the `--nt` option, and RDFa files with the `-a` option.
In addition, you can load all the files in a directory, assuming that they all
have the same format. To do this, use the `--directory` option to identify the
directory containing the files, and the `--format` option to specify the
format of the files in that directory.

There are a few advanced options available for this script; you can use the
`-h` option to get a summary of all the available options. You may also want
to see the "Benchmarking" section, below, for specific examples that you can
generalize.

Query
-----

The RDFLib `SPARQL <http://www.w3.org/TR/rdf-sparql-query/>`_ implementation
allows you to use the SPARQL language to query your RDF stores. The default
implementation works entirely in memory; with a SQL backend, two different
RDFLib components offer separate approaches to utilizing that backend to
optimize the query. This section will eventually provide generic instructions
for how to use the different query options, but until I get around to writing
it see the "Benchmarking" section, below, for specific examples that you can
generalize.

Benchmarking
------------

When working on the various SQL backends, I found it useful to compare the
results of the RDFLib store with the results obtained in Christian Becker's
`RDF Store Benchmarks with DBpedia <http://www4.wiwiss.fu-berlin.de/benchmarks-200801/>`_. 

Walking through this process serves both as a good example to how
to load and query large RDF datasets with an SQL backend, but also helps to
judge the RDFLib backend against other options. Indeed, the DBpedia data set
is interesting in its own right; loading and querying DBpedia may be a
reasonably common use case on its own. For our benchmarking, we will compare
both the MySQL and the PostgreSQL backends.

I obtained a set of results for this benchmark dataset on a dual core 1.86 GHz
machine with 3.5 GB of RAM, running Ubuntu GNU/Linux 8.10. These specs do not
completely align with Becker's configuration, so the results are only roughly
comparable. Also, note that I used MySQL version 5.0.67, and, importantly,
*PostgreSQL 8.4beta1*.

Version 8.4 of PostgreSQL contains a large performance enhancement over
previous versions, so if you want the best performance (and if you want to
reproduce the results in this report), you will need to install your own
PostgreSQL server until the next stable version makes it out into the wild.

Loading
-------

To begin, we first need to load our data. To do this, we need to first create
both a MySQL and a PostgreSQL database which will receive the data; these
examples assume that this database is named 'Becker_dbpedia'. This load
process also assumes that we have downloaded and extracted the benchmark
datasets to a `data` directory relative to the current directory. Once we have
created a database, we can load that database (and time the load) with the
following command:


.. sourcecode:: bash

    $ time python -m rdfextras.store.FOPLRelationalModel.MySQLMassLoader \
      -c db=Becker_dbpedia,host=localhost,user=username,password=password \
      -i Becker_dbpedia \
      --nt=data/infoboxes-fixed.nt --nt=data/geocoordinates-fixed.nt \
      --nt=data/homepages-fixed.nt \
      MySQL

Note that the name ``MySQLMassLoader`` is a misnomer; it started life
targeting MySQL, but now supports both MySQL and PostgreSQL through its first
positional parameter. As such, we can load the data into PostgreSQL by
changing the argument from ``MySQL`` to ``PostgreSQL`` (in addition to changing
any relevant connection details in the connection string).

The results for the bulk load times are listed below. Note that in addition to
the hardware differences listed above, we are also doing a bulk load of all
the pieces at once, instead of loading the three pieces in stages.

+-----------------------+-----------------------+
|       *Backend*       | *Load time (seconds)* |
+=======================+=======================+
|        MySQL          |         28,612        |
+-----------------------+-----------------------+
| PostgreSQL (8.4beta1) |         7,812         |
+-----------------------+-----------------------+


.. note:: the PostgreSQL and MySQL load strategies are *very different*, which may account for the dramatic difference. Interestingly, it was a missing feature (the `IGNORE` keyword on the delimited load statement) that led to the construction of a different load mechanism in PostgreSQL, but it may turn out that the alternate load mechanism may work better on MySQL as well. I will continue to experiment with that.

Queries
-------

Becker's benchmark set includes five amusing queries; we can currently run the
first three of these queries, but the last two use SPARQL features that are
not currently supported by the RDFLib SPARQL processor. To run these queries,
we will use the :mod:`rdfextras.tools.sparqler` script.

For both backends, we will run each query in up to four different ways. The
RDFLib SPARQL processor has a new component that can completely translate
SPARQL queries to equivalent SQL queries directly against the backend, so we
will run each query using that component, and again without it. Also, for each
component run, we may also provide range metadata to the processor as an
optimization.

All available information about a specific subject
--------------------------------------------------

We run this query using the SPARQL to SQL translator using the `sparqler.py`
command line below.

.. sourcecode:: bash

    $ time python /home/john/development/rdfextras/tools/sparqler.py -s MySQL \
    db=Becker_dbpedia,host=localhost,user=username,password=password Becker_dbpedia \
    'SELECT ?p ?o WHERE {
      <http://dbpedia.org/resource/Metropolitan_Museum_of_Art> ?p ?o
    }' > results


We run this query using the original SPARQL implementation using the command line below.


.. sourcecode:: bash

    $ time python /home/john/development/rdfextras/tools/sparqler.py \
    --originalSPARQL -s MySQL \
    db=Becker_dbpedia,host=localhost,user=username,password=password Becker_dbpedia \
    'SELECT ?p ?o WHERE {                                                               
      <http://dbpedia.org/resource/Metropolitan_Museum_of_Art> ?p ?o
    }' > results


We must simply change 'MySQL' to 'PostgreSQL' in the above commands (and
change connection parameters as necessary) to run the same queries against the
PostgreSQL backend.

The results for this query are listed below. All times are in seconds. For
this query, we do not add any range information, because we don't know
anything about the properties that may be involved.

+------------------------+----------------------------+---------------------------+
|        *Backend*       | *SPARQL to SQL translator* | *Original implementation* |
+========================+============================+===========================+
|           MySQL        |            2.063           |         2.013             |
+------------------------+----------------------------+---------------------------+
| PostgreSQL (8.4beta1)  |            1.993           |         2.002             |
+------------------------+----------------------------+---------------------------+

Two degrees of separation from Kevin Bacon
------------------------------------------

To run this query, we can replace the query in the above commands with the new
query:

.. sourcecode:: sparql

    PREFIX p: <http://dbpedia.org/property/>

    SELECT ?film1 ?actor1 ?film2 ?actor2
    WHERE {
      ?film1 p:starring <http://dbpedia.org/resource/Kevin_Bacon> .
      ?film1 p:starring ?actor1 .
      ?film2 p:starring ?actor1 .
      ?film2 p:starring ?actor2 .
    }


The results for this query are listed below. All times are in seconds. This
time, we will also run the query with the range optimization; we know the
`http://dbpedia.org/property/starring` property only ranges over resources, so
we can add `-r http://dbpedia.org/property/starring` to the query command line
to provide this hint to the query processor.

+-----------------------+--------------+------------+------------------------+----------------------+
|     *Backend*         | *Translator* | *Original* | *Translator with hint* | *Original with hint* |
+=======================+==============+============+========================+======================+
|        MySQL          |      843     |     645    |         23.58          |        25.216        |
+-----------------------+--------------+------------+------------------------+----------------------+
| PostgreSQL (8.4beta1) |      68.36   |    82.64   |         23.38          |         80.45        |
+-----------------------+--------------+------------+------------------------+----------------------+

Unconstrained query for artworks, artists, museums and their directors
----------------------------------------------------------------------

To run this query, we can replace the query in the above commands with the new query:

.. sourcecode:: python

    PREFIX p: <http://dbpedia.org/property/>

    SELECT ?artist ?artwork ?museum ?director
    WHERE {
      ?artwork p:artist ?artist .
      ?artwork p:museum ?museum .
      ?museum p:director ?director
    }

The results for this query are listed below. All times are in seconds. We will
not use any range optimizations for this query.

+-----------------------+----------------------------+----------------------------+
|       *Backend*       | *SPARQL to SQL translator* | *Original implementation*  |
+=======================+============================+============================+
|         MySQL         |             1026           |               336          |
+-----------------------+----------------------------+----------------------------+
| PostgreSQL (8.4beta1) |              98            |             5.074          |
+-----------------------+----------------------------+----------------------------+

API
===

This section describes how to use the RDFLib API to use either a MySQL or
PostgreSQL backend as a `ConjunctiveGraph`. This section assumes that you have
MySQL or PostgreSQL installed and configured correctly (particularly
permissions), as well as either the ``MySQLdb``, the ``pgdb``, the ``postgresql``
or the ``psycopg`` Python modules installed.

Setting up the database server is outside the scope of this document and so is 
installing the modules.

Here's an example:

.. sourcecode :: python

    import rdflib
    from rdflib import plugin, term, graph, namespace

    db_type = 'PostgreSQL' # Use 'MySQL' instead, if that's what you have
    store = plugin.get(db_type, rdflib.store.Store)(
                          identifier = 'some_ident',
                          configuration = 'user=u,password=p,host=h,db=d')
    store.open(create=True) # only True when opening a store for the first time

    g = graph.ConjunctiveGraph(store)
    sg = graph.Graph(store, identifier=term.URIRef(
                                'tag:jlc6@po.cwru.edu,2009-08-20:bookmarks'))
    sg.add((term.URIRef('http://www.google.com/'), 
            namespace.RDFS.label,
            term.Literal('Google home page')))
    sg.add((term.URIRef('http://wikipedia.org/'), 
            namespace.RDFS.label,
            term.Literal('Wikipedia home page')))

Other general Graph/ConjunctiveGraph API uses here

