import unittest
import gc
import itertools
from time import time
from random import random
from tempfile import mkdtemp
from tempfile import mkstemp
from rdflib import Graph
from rdflib import URIRef

def random_uri():
    return URIRef("%s" % random())

class StoreTestCase(unittest.TestCase):
    """
    Test case for testing store performance... probably should be
    something other than a unit test... but for now we'll add it as a
    unit test.
    """
    store = 'default'
    path = None
    storetest = True
    
    def setUp(self):
        self.gcold = gc.isenabled()
        gc.collect()
        gc.disable()
        
        # self.graph = Graph(store=self.store_name)
        # if not self.path:
        #     a_tmp_dir = mkdtemp(prefix='rdfextras_test',dir='/tmp')
        #     print("Persisting in %s" % a_tmp_dir)
        #     self.path = self.path or a_tmp_dir
        # self.graph.open(self.path)
        
        self.graph = Graph(store=self.store)
        if self.store == "MySQL":
            from test_mysql import configString
            from rdfextras.store.MySQL import MySQL
            path=configString
            MySQL().destroy(path)
        elif self.store == "PostgreSQL":
            from test_postgresql import configString
            from rdflib.store.PostgreSQL import PostgreSQL
            path=configString
            PostgreSQL().destroy(path)
        elif not self.path and self.store == "SQLite":
            path = mkstemp(dir="/var/tmp", prefix="test", suffix='.sqlite')[1]
        elif not self.path and self.store in ["sqlobject", "SQLAlchemy", "Elixir"]:
            path = mkstemp(dir="/var/tmp", prefix="test", suffix='.sqlite')[1]
            path = 'sqlite://'+path
        elif not self.path:
            path = mkdtemp()
        else:
            path = self.path
        # print("Opening %s" % path)
        self.path = path
        self.graph.open(self.path, create=True)
        self.input = input = Graph()
        input.parse(location="http://rdflib.googlecode.com/svn/trunk/test/n3/example-just_a_class.n3", format="n3")
        # print("Opened %s" % path)
    
    def tearDown(self):
        # print(self.graph.serialize(format="n3"))
        self.graph.close()
        if self.gcold:
            gc.enable()
        # TODO: delete a_tmp_dir
        self.graph.close()
        del self.graph
        import os
        if hasattr(self,'path') and self.path is not None:
            if os.path.exists(self.path):
                if os.path.isdir(self.path):
                    for f in os.listdir(self.path): os.unlink(self.path+'/'+f)
                    os.rmdir(self.path)
                elif len(self.path.split(':')) == 1:
                    os.unlink(self.path)
                else:
                    os.remove(self.path)
    
    def testTime(self):
        number = 1
        print("")
        print(self.store)
        res = ""
        for i in itertools.repeat(None, number):
            res += self._testInput()
        print("std input file: %s" % res)
        res = ""
        for i in itertools.repeat(None, number):
            res += self._testRandom()
        print("random # of triples: %s" % res)
    
    def _testRandom(self):
        number = len(self.input)
        store = self.graph
        
        def add_random():
            s = random_uri()
            p = random_uri()
            o = random_uri()
            store.add((s, p, o))
        
        it = itertools.repeat(None, number)
        t0 = time()
        for _i in it:
            add_random()
        t1 = time()
        return "%.3g " % (t1 - t0)
    
    def _testInput(self):
        number = 1
        store = self.graph
        
        def add_from_input():
            for t in self.input:
                store.add(t)
        
        it = itertools.repeat(None, number)
        t0 = time()
        for _i in it:
            add_from_input()
        t1 = time()
        return "%.3g " % (t1 - t0)
    


class MemoryStoreTestCase(StoreTestCase):
    store = "IOMemory"

try:
    class SleepycatStoreTestCase(StoreTestCase):
        def setUp(self):
            self.store = "Sleepycat"
            self.path = '/var/tmp/test'
            StoreTestCase.setUp(self)
except ImportError, e:
    print("Can not test Sleepycat store:", e)

try:
    class BDBOptimizedStoreTestCase(StoreTestCase):
        def setUp(self):
            self.store = "BDBOptimized"
            self.path = '/var/tmp/test'
            StoreTestCase.setUp(self)
except ImportError, e:
    print("Can not test BDBOptimized store:", e)

try:
    class BerkeleyDBStoreTestCase(StoreTestCase):
        def setUp(self):
            self.store = "BerkeleyDB"
            self.path = '/var/tmp/test'
            StoreTestCase.setUp(self)
except ImportError, e:
    print("Can not test BerkeleyDB store:", e)
# 
# try:
#     from rdfextras.store.PostgreSQL import PostgreSQL
#     class PostgreSQLStoreTestCase(StoreTestCase):
#         store = "PostgreSQL"
# except ImportError, e:
#     print("Can not test PostgreSQL store:", e)
# 

# try:
#     from rdfextras.store.SQLAlchemy_dbapi2 import SQLAlchemy
#     from configstrings import mysqluri, postgresqluri, psycopguri
#     class SQLAlchemyStoreTestCase(StoreTestCase):
#         store = "SQLAlchemy"
#         def testSQLite(self):
#             path = "sqlite:///var/tmp/rdflibsql.sqlite"
#         def testMySQL(self):
#             path = mysqluri
#         def testPostgres(self):
#             path = postgresqluri
#         def testPsycopg(self):
#             path = psycopguri
# except ImportError, e:
#     print("Can not test SQLAlchemy store:", e)
# 
try:
    class SQLiteStoreTestCase(StoreTestCase):
        def setUp(self):
            self.store = "SQLite"
            self.path = "/var/tmp/test"
            StoreTestCase.setUp(self)
except ImportError, e:
    print("Can not test SQLite store:", e)

try:
    # If we can import persistent then test ZODB store
    class ZODBStoreTestCase(StoreTestCase):
        non_standard_dep = True
        def setUp(self):
            self.store = "ZODB"
            self.path = '/var/tmp/test'
            StoreTestCase.setUp(self)
except ImportError, e:
    print("Can not test ZODB store:", e)
# 
# try:
#     import RDF
#     # If we can import RDF then test Redland store
#     class RedLandTestCase(StoreTestCase):
#         non_standard_dep = True
#         store = "Redland"
# except ImportError, e:
#     print("Can not test Redland store:", e)



#
# # TODO: add test case for 4Suite backends?  from Ft import Rdf
#
# try:
# #     import todo # what kind of configuration string does open need?
# 
#     import MySQLdb,sys
#     # If we can import RDF then test Redland store
#     class MySQLTestCase(StoreTestCase):
#         non_standard_dep = True
#         store = "MySQL"
# except ImportError, e:
#     print("Can not test MySQL store:", e)

if __name__ == '__main__':
    unittest.main()
