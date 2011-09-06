.. _rdfextras.store.Redland: RDFExtras, stores, Redland.

|today|

====================================
Redland
====================================

From the Redland docs...

Create a new RDF Storage using any of these forms

.. sourcecode:: python

    s1=RDF.Storage(storage_name="name",options_string="")

Create a Storage of the given type. Currently the built in storage names that
are always present are ``memory``, ``hashes``, ``file`` and ``uri``. 

``bdb`` is available when Sleepycat / BerkeleyDB is compiled in; ``mysql`` 
when MySQL is compiled in (similary ``postgres`` and ``sqlite``) when those
libraries are compiled in. If storage_name is omitted, it defaults to 
``memory``.
 
The argument 'name' can be used when the storage needs a name
to operate, such as used for a filename or URI:

.. sourcecode:: python

    s1=RDF.Storage(storage_name="file", 
                   name='/filename',options_string="")
    
    s2=RDF.Storage(storage_name="uri", 
                   name='http://rdf.example.org/',options_string="")

The required argument options_string allows additional store-specific options
to be given, some of which are required by certain stores.

This uses the following form:

.. sourcecode:: python

    s3=RDF.Storage(storage_name="name", name='abc',
                   options_string="key1='value1', key2='value2', ...")

for multiple key/value option pairs, option values are always surrounded by 
single quotes.
 
The common options are:
    new - optional and takes a boolean value (default false)
        If true, it deletes any existing store and creates a new one
        otherwise if false (default) open an existing store.

    write - optional and takes a boolean value (default true)
        If true (default) the Storage is opened read-write otherwise
        if false the storage is opened read-only and for file-based
        Storages or those with locks, may be opened with shared-readers.
 
Some storage types have additional options:
 
storage_name 'hashes' has options
  :param hash-type: -  the name of any hash type supported.
  
    * 'memory' (default), 
    * 'file' hash types are always present. 
    * 'bdb' is available when BerkeleyDB is compiled in,
  :param dir: - the directory name to create the files in (default '.')
  :param mode: - the file creation mode (default 0644 octal)
 
storage_name 'mysql' has options:
  :param host: - required MySQL database hostname
  :param port: - optional MySQL database port (defaults to 3306)
  :param database: - required MySQL database name
  :param user: - required MySQL database user
  :param password: - required MySQL database password
 
storage name 'sqlite' has options:
  :param synchronous: - optional value off, normal or full
      
For copying from an existing Storage, s1, the form is:

.. sourcecode:: python

  s4 = RDF.Storage(storage = s1)

Note: there are convience classes to create a Memory storage:

.. sourcecode:: python

    s5=RDF.MemoryStorage()

and for creating Hash storage:

.. sourcecode:: python

    # memory hash
    s6 = RDF.HashStorage('abc')
    
    # specified bdb hash stored in files named 'def'*
    s7 = RDF.HashStorage('def', options = "hash-type='bdb'")

rdflib usage examples
+++++++++++++++++++++

.. sourcecode:: python

    from rdflib.store import Store
    from rdfextras.store import Redland
    # Redland libs...
    import RDF as RedlandRDF
    # Use one of...
    options_string = '''"new='true',write='true'"'''
    options_string2 = '''"new='false',write='false'"'''
    
    my_identifier = "http://example.org"
    
    sqlite3store = RedlandRDF.Storage(storage_name = "sqlite",
                                       name = 'some_name',
                                       options_string=options_string)
    
    model = RedlandRDF.Model(sqlite3store)
    graph = Graph(store = Redland.Redland(model), identifier = my_identifier)
    graph.store.open(options_string, create = True)

Module contents
---------------

.. currentmodule:: rdfextras.store.Redland

:mod:`~rdfextras.store.Redland`
----------------------------------------
.. automodule:: rdfextras.store.Redland
.. autoclass:: Redland
  :members:
