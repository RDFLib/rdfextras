.. _rdfextras.store.KyotoCabinet: RDFExtras, stores, KyotoCabinet.

|today|

.. currentmodule:: rdfextras.store.KyotoCabinet

=======================================================
KyotoCabinet :: an adaptation of BerkeleyDB Store
=======================================================

An adaptation of the BerkeleyDB Store's key-value approach to use Kyoto Cabinet 
as a back-end. 

Based on an original contribution by Drew Perttula: `TokyoCabinet Store <http://bigasterisk.com/darcs/?r=tokyo;a=tree>`_.

(Kyoto Cabinet is the successor to Tokyo Cabinet.)

Module API
++++++++++

:mod:`rdfextras.store.KyotoCabinet`
-----------------------------------
.. automodule:: rdfextras.store.KyotoCabinet
.. autoclass:: KyotoCabinet
.. automethod:: KyotoCabinet.open
.. automethod:: KyotoCabinet.triples

About Kyoto Cabinet database
----------------------------

Lifted directly from `Fall Labs <http://fallabs.com/kyotocabinet/>`_

    Kyoto Cabinet is a library of routines for managing a database. The database is a simple data file containing records, each is a pair of a key and a value. Every key and value is serial bytes with variable length. Both binary data and character string can be used as a key and a value. Each key must be unique within a database. There is neither concept of data tables nor data types. Records are organized in hash table or B+ tree.

    Kyoto Cabinet runs very fast. For example, elapsed time to store one million records is 0.9 seconds for hash database, and 1.1 seconds for B+ tree database. Moreover, the size of database is very small. For example, overhead for a record is 16 bytes for hash database, and 4 bytes for B+ tree database. Furthermore, scalability of Kyoto Cabinet is great. The database size can be up to 8EB (9.22e18 bytes).

    Kyoto Cabinet is a free software licensed under the GNU General Public License. On the other hand, a commercial license is also provided. If you use Kyoto Cabinet within a proprietary software, the commercial license is required.

