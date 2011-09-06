"""
http://groups.google.com/group/rdflib-dev/msg/a5d7905f2b7808b3?
drewp's TokyoCabinet store implementation.
http://bigasterisk.com/darcs/?r=tokyo;a=tree
"""
import random
from os import mkdir
from os.path import exists, abspath, join
from urllib import pathname2url
from threading import Thread
from time import sleep, time
from rdflib import URIRef
from rdflib.plugins.sleepycat import Sleepycat, to_key_func, from_key_func, \
        results_from_key_func
from bsddb3 import db
import pytc

class BdbApi(pytc.HDB):
    """make HDB's api look more like berkeley db so I can share the
    sleepycat code"""
    def get(self, key, txn=None):
        try:
            return pytc.HDB.get(self, key)
        except KeyError:
            return None
    
    def append(self, value):
        return
    
    def delete(self, key, txn=None):
        try:
            return pytc.HDB.out(self, key)
        except KeyError:
            return None
    
    # def cursor(self):
    #     return pytc.BDB.curnew(self)

class NoopMethods(object):
    def __getattr__(self, methodName):
        return lambda *args: None
    

class TokyoCabinet(Sleepycat):
    def open(self, path, create=True):
        self.db_env = NoopMethods()
        homeDir = path
        if not exists(homeDir):
            if create:
                mkdir(homeDir)
            else:
                raise ValueError("graph path %r does not exist" % homeDir)
        if self.identifier is None:
            self._Sleepycat__identifier = URIRef(pathname2url(abspath(homeDir)))
        def dbOpen(name):
            return BdbApi(join(homeDir, name),
                          pytc.HDBOWRITER | pytc.HDBOCREAT) # should obey 'create' arg
        self._Sleepycat__open = self._TokyoCabinet__open = True
        
        # create and open the DBs
        self.__indicies = [None,] * 3
        self.__indicies_info = [None,] * 3
        for i in xrange(0, 3):
            index_name = to_key_func(i)(("s", "p", "o"), "c")
            index = dbOpen(index_name)
            self.__indicies[i] = index
            self.__indicies_info[i] = (index, to_key_func(i), from_key_func(i))
        
        lookup = {}
        for i in xrange(0, 8):
            results = []
            for start in xrange(0, 3):
                score = 1
                len = 0
                for j in xrange(start, start+3):
                    if i & (1<<(j%3)):
                        score = score << 1
                        len += 1
                    else:
                        break
                tie_break = 2-start
                results.append(((score, tie_break), start, len))
            
            results.sort()
            score, start, len = results[-1]
            
            def get_prefix_func(start, end):
                def get_prefix(triple, context):
                    if context is None:
                        yield ""
                    else:
                        yield context
                    i = start
                    while i<end:
                        yield triple[i%3]
                        i += 1
                    yield ""
                return get_prefix
            
            lookup[i] = (self.__indicies[start], get_prefix_func(start, start + len), from_key_func(start), results_from_key_func(start, self._from_string))

        
        self.__lookup_dict = lookup
        
        # these 3 were btree mode in sleepycat, but currently i'm using tc hash
        self.__contexts = dbOpen("contexts")
        self.__namespace = dbOpen("namespace")
        self.__prefix = dbOpen("prefix")
        
        self.__k2i = dbOpen("k2i")
        self.__i2k = dbOpen("i2k") # was DB_RECNO mode
        self.__journal = NoopMethods() # was DB_RECNO mode
        
        self._Sleepycat__indicies = self.__indicies
        self._Sleepycat__indicies_info = self.__indicies_info
        self._Sleepycat__lookup_dict = self.__lookup_dict
        self._Sleepycat__contexts = self.__contexts
        self._Sleepycat__namespace = self.__namespace
        self._Sleepycat__prefix = self.__prefix
        self._Sleepycat__k2i = self.__k2i
        self._Sleepycat__i2k = self.__i2k
        self._Sleepycat__journal = self.__journal

        self._TokyoCabinet__lookup = self.__lookup
        
        self._Sleepycat__sync_thread = NoopMethods()
        
        return 1
    
    def _from_string(self, i):
        """rdflib term from index number (as a string)"""
        print "getting", repr(i)
        k = self.__i2k.get(i)
        return self._loads(k)
    
    def _to_string(self, term, txn=None):
        """index number (as a string) from rdflib term"""
        k = self._dumps(term)
        # print "k2i(%r)" % k
        i = self.__k2i.get(k)
        if i is None: # (from BdbApi)
            i = "%s" % random.random() # sleepycat used a serial number
            # print "store", repr((k, i))
            self.__k2i.put(k, i)
        assert i is not None
        return i
    
    def __lookup(self, (subject, predicate, object), context):
        _to_string = self._to_string
        if context is not None:
            context = _to_string(context)
        i = 0
        if subject is not None:
            i += 1
            subject = _to_string(subject)
        if predicate is not None:
            i += 2
            predicate = _to_string(predicate)
        if object is not None:
            i += 4
            object = _to_string(object)
        index, prefix_func, from_key, results_from_key = self.__lookup_dict[i]
        prefix = "^".join(prefix_func((subject, predicate, object), context))
        return index, prefix, from_key, results_from_key
    
    def play_journal(self, graph=None):
        raise NotImplementedError
    
    def triples(self, (subject, predicate, object), context=None):
        """A generator over all the triples matching """
        assert self.__open, "The Store must be open."
        
        if context is not None:
            if context == self:
                context = None
        
        _from_string = self._from_string
        index, prefix, from_key, results_from_key = self.__lookup((subject, predicate, object), context)
        
        current = index.cursor()

        try:
            current = cursor.set_range(prefix)
        except db.DBNotFoundError:
            current = None
        cursor.close()
        while current:
            key, value = current
            cursor = index.cursor()
            try:
                cursor.set_range(key)
                current = cursor.next()
            except db.DBNotFoundError:
                current = None
            cursor.close()
            if key and key.startswith(prefix):
                contexts_value = index.get(key)
                yield results_from_key(key, subject, predicate, object, contexts_value)
            else:
                break
    
