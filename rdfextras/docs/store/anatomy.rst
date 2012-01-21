================================================================
Anatomy of the RDFLib Sleepycat key-value non-nested btree Store
================================================================

BerkeleyDB/Sleepycat underpinning
=================================

At base, we have ``get(key)`` and ``put(key, data)`` as provided by the 
Sleepycat/BerkeleyDB core API:

.. code-block:: text

    get(key, default=None, txn=None, flags=0, ...)
    Returns the data object associated with key.

    put(key, data, txn=None, flags=0, ...)
    Stores the key/data pair in the database.

Python's ``bsddb`` module
==========================

From the documentation for Python's (now deprecated) 
`bsddb <http://docs.python.org/library/bsddb.html>`_ module:

    The bsddb module provides an interface to the Berkeley DB library. Users can
    create hash, btree or record based library files using the appropriate ``open()``
    call. Bsddb objects behave generally like dictionaries. Keys and values must be
    strings, however, so to use other objects as keys or to store other kinds of
    objects the user must serialize them somehow, typically using ``marshal.dumps()`` or
    ``pickle.dumps()``.

The two main points of interest here are i) the choice of hash, btree or 
record-based storage techniques typically provided by key-data stores and ii) the 
requirement for serialization of Python objects - which, for the case in 
point, are RDFLib objects: ``BNode``, ``Literal``, ``URIRef``, ``Namespace``,
``Graph``, ``QuotedGraph``, etc.

Modelling an RDF store using serialized key-data pairs
=======================================================
To illustrate (sketchily) how this basic principle of serialized key-data pairs
is used to model an RDF store, here is a sort-of-pseudocode distillation of RDFLib's 
``Sleepycat`` Store implementation (which uses non-nested btrees, specified via
a relevant db flag) and shows the creation of the indices and the main key-data
tables: ``context``, ``namespace``, ``prefix``, ``k2i`` and ``i2k`` (the 
latter being "key-to-index" and "index-to-key" respectively) and then, broadly, 
how a ``{subject, predicate, object}`` triple is serialized into keys and indices 
which are then ``put`` into the underlying key-data store:

.. code-block:: python

    def open(self, config):

        # creating and opening the DBs

        # Create the indices ...

        self.__indices = [None,] * 3
        self.__indices_info = [None,] * 3
        for i in xrange(0, 3):
            index_name = to_key_func(i)(("s", "p", "o"), "c")
            index = db.DB(db_env)
            index.open(index_name, dbopenflags)
            self.__indices[i] = index
            self.__indices_info[i] = \
                    (index, to_key_func(i), from_key_func(i))

        # [ ... ]

        # Create the required key-data stores

        self.__contexts = db.DB(db_env)
        self.__contexts.open("contexts", dbopenflags)

        self.__namespace = db.DB(db_env)
        self.__namespace.open("namespace", dbopenflags)

        self.__prefix = db.DB(db_env)
        self.__prefix.open("prefix", dbopenflags)

        self.__k2i = db.DB(db_env)
        self.__k2i.open("k2i", dbopenflags)

        self.__i2k = db.DB(db_env)
        self.__i2k.open("i2k", dbopenflags)

    # [ ... ]

    def add(self, (subject, predicate, object), context=None, txn=None):

        # Serializing the subject, predicate, object and context

        s = _to_string(subject, txn=txn)
        p = _to_string(predicate, txn=txn)
        o = _to_string(object, txn=txn)
        c = _to_string(context, txn=txn)
        
        # Storing the serialized data (protected by a transaction 
        # object, if provided)

        cspo, cpos, cosp = self.__indices

        value = cspo.get("%s^%s^%s^%s^" % (c, s, p, o), txn=txn)
        if value is None:
            self.__contexts.put(c, "", txn=txn)

            contexts_value = cspo.get("%s^%s^%s^%s^" % ("", s, p, o), txn=txn) or ""
            contexts = set(contexts_value.split("^"))
            contexts.add(c)
            contexts_value = "^".join(contexts)
            assert contexts_value!=None

            cspo.put("%s^%s^%s^%s^" % (c, s, p, o), "", txn=txn)
            cpos.put("%s^%s^%s^%s^" % (c, p, o, s), "", txn=txn)
            cosp.put("%s^%s^%s^%s^" % (c, o, s, p), "", txn=txn)

            if not quoted:
                cspo.put("%s^%s^%s^%s^" % ("", s, p, o), contexts_value, txn=txn)
                cpos.put("%s^%s^%s^%s^" % ("", p, o, s), contexts_value, txn=txn)
                cosp.put("%s^%s^%s^%s^" % ("", o, s, p), contexts_value, txn=txn)

A corresponding ``get`` method reconstructs (de-serializes) the triple from the 
indices and keys.

Indexing and storage issues
===========================

Returning to the issue of the choice of hash, btree or record-based storage,
some of the issues that might usefully be taken into consideration are 
outlined in the Sleepycat DB manual:

    Choosing between BTree and Hash
    -------------------------------
    
    For small working datasets that fit entirely in memory, there is no
    difference between BTree and Hash. Both will perform just as well as the
    other. In this situation, you might just as well use BTree, if for no other
    reason than the majority of DB applications use BTree.

    Note that the main concern here is your working dataset, not your entire
    dataset. Many applications maintain large amounts of information but only
    need to access some small portion of that data with any frequency. So what
    you want to consider is the data that you will routinely use, not the sum
    total of all the data managed by your application.

    However, as your working dataset grows to the point where you cannot fit it
    all into memory, then you need to take more care when choosing your access
    method. Specifically, choose:

    BTree if your keys have some locality of reference. That is, if they sort
    well and you can expect that a query for a given key will likely be followed
    by a query for one of its neighbors.

    Hash if your dataset is extremely large. For any given access method, DB
    must maintain a certain amount of internal information. However, the amount
    of information that DB must maintain for BTree is much greater than for
    Hash. The result is that as your dataset grows, this internal information
    can dominate the cache to the point where there is relatively little space
    left for application data. As a result, BTree can be forced to perform disk
    I/O much more frequently than would Hash given the same amount of data.

    Moreover, if your dataset becomes so large that DB will almost certainly
    have to perform disk I/O to satisfy a random request, then Hash will
    definitely out perform BTree because it has fewer internal records to search
    through than does BTree.

And, in addition, there is the usual raft of cryptic XXXTHISNTHAT flags for 
tweaking the inevitable variety of database speed/space/structure knobs.

Adapting the key-data approach to different back-ends
========================================================

The design of the RDFLib ``Store`` facilitates the exploration of the 
above-mentioned tradeoffs as shown in Drew Pertulla's experiment 
with replacing the BerkeleyDB key-data database with the 
`Tokyo Cabinet <http://fallabs.com/tokyocabinet/>`_ key-data database, 
using the `pytc <http://pypi.python.org/pypi/pytc>`_ Python bindings.

Firstly, the Sleepycat Store is adapted by swapping out bsddb's ``BDB`` 
(btree) API in favour of pytc's ``HDB`` (hash) API ...

.. code-block:: python

    class BdbApi(pytc.HDB):
        """
        Make HDB's API look more like BerkeleyDB so we can share 
        the Sleepycat code.
        """

        def get(self, key, txn=None):
            try:
                return pytc.HDB.get(self, key)
            except KeyError:
                return None
                
        def put(self, key, data, txn=None):
            try:
                return pytc.HDB.set(self, key, data)
            except KeyError:
                return None
                
        def delete(self, key, txn=None):
            try:
                return pytc.HDB.out(self, key)
            except KeyError:
                return None

The next step is to create a wrapper to substitute for the standard bsddb
``open()`` call, returning a BdbApi object instead of a bsddb object ...

.. code-block:: python

    def dbOpen(name):
        return BdbApi(name, pytc.HDBOWRITER | pytc.HDBOCREAT)

This can be slotted into place with minimal disturbance to the re-use of 
the (substantial amount of) remaining Sleepycat-based code ...

.. code-block:: python

    # Create the required key-data stores

    # These 3 were BTree mode in Sleepycat, but currently I'm using TC hash
    self.__contexts = dbOpen("contexts")
    self.__namespace = dbOpen("namespace")
    self.__prefix = dbOpen("prefix")

    self.__k2i = dbOpen("k2i")
    self.__i2k = dbOpen("i2k")

The pytc HashDB API unfortunately does not provide a ``cursor()`` object, whereas
Sleepycat/BerkeleyDB does and key parts of the functionality of the RDFLib 
Sleepycat Store implementation rely on the availability of that cursor. The 
consequent necessity of mimicking a cursor in Python rather than being able to 
use the library's fast, C-coded version rendered the exploration much less 
promising.

However, Tokyo Cabinet has subsequently given way to its anagrammatic successor
`Kyoto Cabinet <http://fallabs.com/kyotocabinet/>`_ which offers a much richer 
`API <http://fallabs.com/kyotocabinet/api/>`_, including (crucially) a cursor 
object for the HashDB and so the exploration recovers its promise and an RDFLib
KyotoCabinet key-value Store is now undergoing performance trials.

