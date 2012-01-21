"""
An adaptation of the BerkeleyDB Store's key-value approach to use Kyoto Cabinet 
as a back-end. 

Based on an original contribution by Drew Perttula: `TokyoCabinet Store <http://bigasterisk.com/darcs/?r=tokyo;a=tree>`_.

adaptor: Graham Higgins <gjh@bel-epa.com>
"""
import random
import logging
from os import mkdir
from os.path import exists, abspath
from urllib import pathname2url
from rdflib import URIRef
from rdflib.store import Store
from rdflib.store import VALID_STORE

from kyotocabinet import DB

logging.basicConfig(level=logging.ERROR,format="%(message)s")
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.ERROR)


class NoopMethods(object):
    def __getattr__(self, methodName):
        return lambda *args: None
    
class KyotoCabinet(Store):
    context_aware = True
    formula_aware = True
    transaction_aware = False

    def __init__(self, configuration=None, identifier=None):
        self.__open = False
        self.__identifier = identifier
        super(KyotoCabinet, self).__init__(configuration)
        self.configuration = configuration
        self._loads = self.node_pickler.loads
        self._dumps = self.node_pickler.dumps
        self.db_env = None
    
    def __get_identifier(self):
        return self.__identifier
    identifier = property(__get_identifier)
    
    def is_open(self):
        return self.__open

    def open(self, path, create=True):
        self.db_env = NoopMethods()
        self.create = create
        self.path = homeDir = path
        if not exists(homeDir):
            if create:
                mkdir(homeDir)
            else:
                raise ValueError("graph path %r does not exist" % homeDir)
        if self.identifier is None:
            self.__identifier = URIRef(pathname2url(abspath(homeDir)))
        
        def dbOpen(name):
            db = DB()
            if self.create:
                # if not db.open(abspath(self.path) + '/' + name + ".kch", 
                #         DB.OWRITER | DB.OCREATE | DB.OAUTOSYNC | DB.OAUTOTRAN):
                if not db.open(abspath(self.path) + '/' + name + ".kch", 
                        DB.OWRITER | DB.OCREATE):
                    raise IOError("open error: " + str(db.error()))
                return db
            else:
                # if not db.open(abspath(self.path) + '/' + name + ".kch", 
                #         DB.OWRITER | DB.OAUTOSYNC | DB.OAUTOTRAN):
                if not db.open(abspath(self.path) + '/' + name + ".kch", 
                        DB.OWRITER):
                    raise IOError("open error: " + str(db.error()))
                return db
                
        # create and open the DBs
        self.__indices = [None,] * 3
        self.__indices_info = [None,] * 3
        for i in xrange(0, 3):
            index_name = to_key_func(i)(("s", "p", "o"), "c")
            index = dbOpen(index_name)
            self.__indices[i] = index
            self.__indices_info[i] = (index, to_key_func(i), from_key_func(i))
        
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
            
            lookup[i] = (self.__indices[start], 
                            get_prefix_func(start, start + len), 
                            from_key_func(start), 
                            results_from_key_func(start, self._from_string))

        self.__lookup_dict = lookup

        # these 3 were btree mode in sleepycat, but currently i'm using tc hash
        self.__contexts = dbOpen("contexts")
        self.__namespace = dbOpen("namespace")
        self.__prefix = dbOpen("prefix")
        self.__k2i = dbOpen("k2i")
        self.__i2k = dbOpen("i2k") # was DB_RECNO mode
        self.__journal = NoopMethods() # was DB_RECNO mode
 
        self.__needs_sync = False
        # t = Thread(target=self.__sync_run)
        # t.setDaemon(True)
        # t.start()
        # self.__sync_thread = t
        self.__sync_thread = NoopMethods()
        # self.synchronize()
        self.__open = True

        return VALID_STORE
    
    def __sync_run(self):
        from time import sleep, time
        try:
            min_seconds, max_seconds = 10, 300
            while self.__open:
                if self.__needs_sync:
                    t0 = t1 = time()
                    self.__needs_sync = False
                    while self.__open:
                        sleep(.1)
                        if self.__needs_sync:
                            t1 = time()
                            self.__needs_sync = False
                        if time()-t1 > min_seconds or time()-t0 > max_seconds:
                            self.__needs_sync = False
                            _logger.debug("sync")
                            self.synchronize()
                            break
                else:
                    sleep(1)
        except Exception, e:
            _logger.exception(e)
    
    def sync(self):
        if self.__open:
            for i in self.__indices:
                i.synchronize()
            self.__contexts.synchronize()
            self.__namespace.synchronize()
            self.__prefix.synchronize()
            self.__i2k.synchronize()
            self.__k2i.synchronize()
    
    def close(self, commit_pending_transaction=False):
        _logger.debug("Closing store")
        # self.__sync_thread.join()
        for i in self.__indices:
            i.close()
        self.__contexts.close()
        self.__namespace.close()
        self.__prefix.close()
        self.__i2k.close()
        self.__k2i.close()
        # self.db_env.close()
        self.__open = False


    def destroy(self, configuration=''):
        import os
        path = configuration or self.homeDir
        if os.path.exists(path):
            for f in os.listdir(path): 
                os.unlink(path+'/'+f)
            os.rmdir(path)

    def __len__(self, context=None):
        assert self.__open, "The Store must be open."
        if context is not None:
            if context == self:
                context = None
        
        if context is None:
            prefix = "^"
        else:
            prefix = "%s^" % self._to_string(context)
        
        return len([key for key in self.__indices[0] 
                            if key.startswith(prefix)])

    def add(self, (subject, predicate, object), context, quoted=False):
        """\
        Add a triple to the store of triples.
        """
        assert self.__open, "The Store must be open."
        assert context != self, "Can not add triple directly to store"
        # Add the triple to the Store, triggering TripleAdded events
        Store.add(self, (subject, predicate, object), context, quoted)
        
        _to_string = self._to_string
        
        s = _to_string(subject)
        p = _to_string(predicate)
        o = _to_string(object)
        c = _to_string(context)
        
        cspo, cpos, cosp = self.__indices
        
        value = cspo.get("%s^%s^%s^%s^" % (c, s, p, o))
        if value is None:
            self.__contexts.set(c, "")
            
            contexts_value = cspo.get("%s^%s^%s^%s^" % ("", s, p, o)) or ""
            contexts = set(contexts_value.split("^"))
            contexts.add(c)
            contexts_value = "^".join(contexts)
            assert contexts_value!=None
            
            cspo.set("%s^%s^%s^%s^" % (c, s, p, o), "")
            cpos.set("%s^%s^%s^%s^" % (c, p, o, s), "")
            cosp.set("%s^%s^%s^%s^" % (c, o, s, p), "")
            if not quoted:
                cspo.set("%s^%s^%s^%s^" % ("", s, p, o), contexts_value)
                cpos.set("%s^%s^%s^%s^" % ("", p, o, s), contexts_value)
                cosp.set("%s^%s^%s^%s^" % ("", o, s, p), contexts_value)
            
            self.__needs_sync = True
            self.__contexts.synchronize()
            for dbindex in self.__indices:
                dbindex.synchronize()
            # self.synchronize()

    def __remove(self, (s, p, o), c, quoted=False):
        cspo, cpos, cosp = self.__indices
        contexts_value = cspo.get("^".join(("", s, p, o, ""))) or ""
        contexts = set(contexts_value.split("^"))
        contexts.discard(c)
        contexts_value = "^".join(contexts)
        for i, _to_key, _from_key in self.__indices_info:
            i.remove(_to_key((s, p, o), c))
        if not quoted:
            if contexts_value:
                for i, _to_key, _from_key in self.__indices_info:
                    i.set(_to_key((s, p, o), ""), contexts_value)
            else:
                for i, _to_key, _from_key in self.__indices_info:
                    try:
                        i.remove(_to_key((s, p, o), ""))
                    except self.db.DBNotFoundError, e:
                        _logger.debug("__remove failed with %s" % e)
                        pass # TODO: is it okay to ignore these?

    def remove(self, (subject, predicate, object), context):
        assert self.__open, "The Store must be open."
        Store.remove(self, (subject, predicate, object), context)
        _to_string = self._to_string
        
        if context is not None:
            if context == self:
                context = None
        
        if subject is not None \
                and predicate is not None \
                and object is not None \
                and context is not None:
            s = _to_string(subject)
            p = _to_string(predicate)
            o = _to_string(object)
            c = _to_string(context)
            value = self.__indices[0].get("%s^%s^%s^%s^" % (c, s, p, o))
            if value is not None:
                self.__remove((s, p, o), c)
                self.__needs_sync = True
        else:
            cspo, cpos, cosp = self.__indices
            index, prefix, from_key, results_from_key = self.__lookup(
                                    (subject, predicate, object), context)
            
            needs_sync = False
            for key in index.match_prefix(prefix):
                c, s, p, o = from_key(key)
                if context is None:
                    contexts_value = index.get(key) or ""
                    # remove triple from all non quoted contexts
                    contexts = set(contexts_value.split("^"))
                    contexts.add("") # and from the conjunctive index
                    for c in contexts:
                        for i, _to_key, _ in self.__indices_info:
                            i.remove(_to_key((s, p, o), c))
                else:
                    self.__remove((s, p, o), c)
                needs_sync = True
            if context is not None:
                if subject is None and predicate is None and object is None:
                    # TODO: also if context becomes empty and not just on 
                    # remove((None, None, None), c)
                    try:
                        self.__contexts.remove(_to_string(context))
                    # except db.DBNotFoundError, e:
                    #     pass
                    except Exception, e:
                        print("%s, Failed to delete %s" % (e, context))
                        pass
            
            self.__needs_sync = needs_sync
            # self.synchronize()

    def _from_string(self, i):
        """rdflib term from index number (as a string)"""
        k = self.__i2k.get(i)
        return self._loads(k)
    
    def _to_string(self, term, txn=None):
        """index number (as a string) from rdflib term"""
        k = self._dumps(term)
        i = self.__k2i.get(k)
        if i is None: # (from BdbApi)
            i = "%s" % random.random() # sleepycat used a serial number
            self.__k2i.set(k, i)
            self.__i2k.set(i, k)
            self.__k2i.synchronize()
            self.__i2k.synchronize()
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
        # _from_string = self._from_string

        index, prefix, from_key, results_from_key = self.__lookup(
                                    (subject, predicate, object), context)

        for key in index.match_prefix(prefix):
            yield results_from_key(
                key, subject, predicate, object, index[key])

    def bind(self, prefix, namespace):
        prefix = prefix.encode("utf-8")
        namespace = namespace.encode("utf-8")
        bound_prefix = self.__prefix.get(namespace)
        if bound_prefix:
            self.__namespace.remove(bound_prefix)
        self.__prefix[namespace] = prefix
        self.__namespace[prefix] = namespace
    
    def namespace(self, prefix):
        prefix = prefix.encode("utf-8")
        p = self.__namespace.get(prefix)
        return p if p else None
    
    def prefix(self, namespace):
        namespace = namespace.encode("utf-8")
        p = self.__prefix.get(namespace)
        return p if p else None

    def namespaces(self):
        for prefix in self.__namespace:
            yield prefix, URIRef(self.__namespace[prefix])

    def contexts(self, triple=None):
        _from_string = self._from_string
        _to_string = self._to_string
        
        if triple:
            s, p, o = triple
            s = _to_string(s)
            p = _to_string(p)
            o = _to_string(o)
            contexts = self.__indices[0].get("%s^%s^%s^%s^" % ("", s, p, o))
            if contexts:
                for c in contexts.split("^"):
                    if c:
                        yield _from_string(c)
        else:
            for key in self.__contexts:
                yield _from_string(key)

def results_from_key_func(i, from_string):
    def from_key(key, subject, predicate, object, contexts_value):
        "Takes a key and subject, predicate, object; returns tuple for yield"
        parts = key.split("^")
        if subject is None:
            # TODO: i & 1: # dis assemble and/or measure to see which is 
            # faster
            # subject is None or i & 1
            s = from_string(parts[(3-i+0)%3+1])
        else:
            s = subject
        if predicate is None:#i & 2:
            p = from_string(parts[(3-i+1)%3+1])
        else:
            p = predicate
        if object is None:#i & 4:
            o = from_string(parts[(3-i+2)%3+1])
        else:
            o = object
        return (s, p, o), (from_string(c) 
                                for c in contexts_value.split("^") if c)
    
    return from_key

def to_key_func(i):
    def to_key(triple, context):
        "Takes a string; returns key"
        return "^".join((context, triple[i%3], 
                         triple[(i+1)%3], triple[(i+2)%3], "")
                         ) # "" to tac on the trailing ^
    
    return to_key

def from_key_func(i):
    def from_key(key):
        "Takes a key; returns string"
        parts = key.split("^")
        return parts[0], parts[(3-i+0)%3+1], \
                    parts[(3-i+1)%3+1], parts[(3-i+2)%3+1]
    
    return from_key

def readable_index(i):
    s, p, o = "?" * 3
    if i & 1: s = "s"
    if i & 2: p = "p"
    if i & 4: o = "o"
    return "%s,%s,%s" % (s, p, o)
