"""
SQLAlchemyDBAPI2.py
DBAPI2 implementation of rdflib.store.Store.
"""

__metaclass__ = type

import re
import logging
from rdflib.store import Store
from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
#from urllib import quote, unquote
#import inspect
#from rdflib.term import Literal, URIRef, BNode
#from rdflib.namespace import Namespace
#import sqlalchemy
#from sqlalchemy import sql

logging.basicConfig(level=logging.ERROR,format="%(message)s")
logger = logging.getLogger('rdfextras.store.SQLAlchemy_dbapi2')
logger.setLevel(logging.ERROR)

_literal = re.compile(
    r'''"(?P<value>[^@&]*)"(?:@(?P<lang>[^&]*))?(?:&<(?P<datatype>.*)>)?''')

global metadata
metadata = MetaData()
Base = declarative_base()
Session = sessionmaker()

LITERAL = 0
URI = 1
NO_URI = 'uri://dev/null/'
Any = None

class Literals(Base):
    pass
    # __tablename__ = 'literals'
    
    # hash = Column(Integer, index=True, primary_key=True)
    # value = Column(Text, nullable=False)
    
    # def __repr__(self):
    #     return "<Literal(%s)>" % (self.value)
    
_literals = Literals

class Namespaces(Base):
    pass
    # __tablename__ = 'namespaces'
    
    # hash = Column(Integer, index=True, primary_key=True)
    # value = Column(String(255), nullable=False)
    
    # def __repr__(self):
    #     return "<Namespace(%s)>" % (self.value)
    
_ns = Namespaces

class PrefixNamespace(Base):
    pass
    # __tablename__ = 'prefix_namespace'
    
    # prefix = Column(String(255), index=True, primary_key=True)
    # ns = Column(String(255), index=True)
    
    # def __repr__(self):
    #     return "<PrefixNamespace(%s: %s)>" % (self.prefix, self.value)
    
_prefix_namespace = PrefixNamespace

class Resources(Base):
    pass
    # __tablename__ = 'resources'
    
    # hash = Column(Integer, index=True, primary_key=True)
    # ns = Column(Integer, index=True)
    # name = Column(String(255), index=True)
    
    # def __repr__(self):
    #     return "<Resource(%s: %s)>" % (self.ns, self.name)
    
_resources = Resources

class Triples(Base):
    pass
    # __tablename__ = 'triples'
    
    # subject = Column(Integer, index=True, primary_key=True)
    # predicate = Column(Integer, index=True)
    # object = Column(Integer, index=True)
    # objtype = Column(Integer, index=True, default=LITERAL)

_triples = Triples

def add_indices():
    pass
    # Index('idx_ns_prefix', PrefixNamespace.ns, PrefixNamespace.prefix)
    # Index('idx_ns_name', Resources.ns, Resources.name)
    # Index('idx_hash_ns_name', Resources.hash, Resources.ns, Resources.name)
    # Index('idx_object_objtype', Triples.object, Triples.objtype)
    # Index('idx_subject_predicate', Triples.subject, Triples.predicate)
    # Index('idx_subject_object_objtype', Triples.subject, Triples.object, 
    #                                     Triples.objtype)
    # Index('idx_predicate_object_objtype', Triples.predicate, Triples.object, 
    #                                       Triples.objtype)


q1 = """\
SELECT relname
FROM pg_class c
WHERE relkind = 'r' 
    AND 
    'public' = 
        (SELECT nspname FROM pg_namespace n 
         WHERE n.oid = c.relnamespace);
"""

class SQLAlchemy(Store):
    # context_aware = True
    # formula_aware = True
    # __open = False
    # _triples = Triples
    # _literals = Literals
    # _ns = Namespaces
    # _prefix_namespace = PrefixNamespace
    # _resources = Resources
    # # __node_pickler = None
    # _connection = None
    # conn = None
    # tables = ('_triples', '_literals', '_ns',
    #           '_prefix_namespace', '_resources')

    def __init__(self, uri='sqlite:///:memory:', **kwargs):
        pass
        # logger.debug("init: Initialising with |%s|" % uri)
        # if self.__open:
        #     logger.debug("init: Already open, returning")
        #     return
        # logger.debug("init: |%s| not yet open." % uri)
        # self.open(uri=uri, **kwargs)
    
    def open(self, uri='sqlite:///:memory:', create=True, **kwargs):
        pass
        # logger.debug("%s %s" % ('open: Creating' if create else 'Opening', uri))
        # if self.__open:
        #     logger.debug("init: Already open, returning")
        #     return
        # logger.debug("open: setting self.__open = True")
        # self.__open = True
        # from sqlalchemy import create_engine
        # engine = create_engine(uri, echo=False)
        # Base.metadata.bind = engine
        # if create:
        #     try:
        #         logger.debug("open: Need to create all")
        #         Base.metadata.create_all(checkfirst=True)
        #         logger.debug("open: create_all succeeded")
        #     except Exception, e: # TODO: should catch more specific exception
        #         logger.debug(e)
        #         logger.warning(e)
        #         return False
        # logger.debug("open: session.configure, binding engine")
        # Session.configure(bind=engine)
        # logger.debug("open: self.session set")
        # self.session = Session()
        # logger.debug("open: connecting engine")
        # engine.connect()
        # self.conn = self._connection = engine
        # # useful for debugging
        # self._connection.debug = False
        # return True
    
    def close(self, commit_pending_transaction=False):
        pass
        # logger.debug("close: Closing store")
        # if not self.__open:
        #     pass
        #     # raise ValueError, 'Not open'
        # self.__open = False
        # if commit_pending_transaction:
        #     self.transaction.commit()
    
    def destroy(self, uri='sqlite://:memory:'):
        pass
        # logger.debug("destroy: Destroying |%s|" % uri)
        # if self.__open:
        #     return
        # from sqlalchemy import create_engine
        # Base.metadata.bind = create_engine(uri)
        # try:
        #     Base.metadata.drop_all(checkfirst=True)
        # except Exception, e: # TODO: should catch more specific exception
        #     logger.debug(e)
        #     logger.warning(e)
        #     return 0
        # return 1
    
    def _makeHash(self, value):
        pass
        # try:
        #     logger.debug("_makeHash: Hashing |%s|" % value)
        # except:
        #     logger.debug("_makeHash: Hashing MULTIPLE VALUED |%s| called by |%s|" % (str(value), inspect.stack()[1][3]))
        # # print("Hashing", value)
        # # XXX We will be using python's hash, but it should be a database
        # # hash eventually.
        # v = hash(value)
        # logger.debug("hash: returning hash=|%s|" % v)
        # return v 
    
    def _insertLiteral(self, value):
        pass
        # logger.debug("_insertLiteral: Inserting literal |%s|" % value)
        # v_hash = self._makeHash(value)
        # lit = self._literals.__table__
        # res = lit.select(lit.c.hash == v_hash).execute().fetchall()
        # if res == []:
        #     nv_hash = self._literals(hash=v_hash, value=value)
        #     self.session.add(nv_hash)
        #     self.session.commit()
        # return v_hash
    
    def _makeURIHash(self, value=None, namespace=None, local_name=None):
        pass
        # logger.debug(
        #     "_makeURIHash: Making URI hash for value=|%s|, namespace=|%s|, localname=|%s|" % \
        #         (value, namespace, local_name))
        # if namespace is None and local_name is None:
        #     namespace, local_name = splituri(value)
        # ns_hash = self._makeHash(namespace)
        # rsrc_hash = self._makeHash((ns_hash, local_name))
        # return ns_hash, rsrc_hash
    
    def _insertURI(self, value=None, namespace=None, local_name=None):
        pass
        # logger.debug(
        #     "_insertURI: Inserting URI for value=|%s|, namespace=|%s|, localname=|%s|" % \
        #         (value, namespace, local_name))
        # if namespace is None and local_name is None:
        #     namespace, local_name = splituri(value)
        # ns_hash, rsrc_hash = self._makeURIHash(value, namespace, local_name)
        # ns = self._ns
        # s = ns.__table__.select(ns.hash == sql.bindparam('ns_hash'))
        # if not self.conn.execute(s, ns_hash=ns_hash).fetchall():
        #     s = ns.__table__.insert(
        #             values={'hash':ns_hash, 'value':namespace})
        #     self.conn.execute(s)
        #     self.session.commit()
        # rsrc = self._resources
        # s = rsrc.__table__.select(rsrc.hash == sql.bindparam('rsrc_hash'))
        # if not self.conn.execute(s, rsrc_hash=rsrc_hash).fetchall():
        #     s = rsrc.__table__.insert(
        #             values={'hash':rsrc_hash,'ns':ns_hash, 'name':local_name})
        #     self.conn.execute(s)
        #     self.session.commit()
        # return rsrc_hash
    
    def _insertTriple(self, s_hash, p_hash, o_hash, objtype=URI):
        pass
        # logger.debug(
        #     "_insertTriple: Inserting triple s_hash=|%s|, p_hash=|%s|, o_hash=|%s|, objtype=|%s|" % \
        #         (s_hash, p_hash, o_hash, objtype))
        # trip = self._triples
        # s = trip.__table__.select(and_(
        #                         trip.subject == sql.bindparam('s_hash'),
        #                         trip.predicate == sql.bindparam('p_hash'),
        #                         trip.object == sql.bindparam('o_hash')))
        # ctext = dict(s_hash=s_hash,p_hash=p_hash,o_hash=o_hash)
        # # res = self.conn.execute(s, **ctext).rowcount
        # # logger.debug("_insertTriple: res %s" % dir(res))
        # # if not res.fetchall():
        # if not self.conn.execute(s, **ctext).rowcount:
        #     s = trip.__table__.insert(
        #             values={'subject':s_hash, 'predicate':p_hash,
        #                     'object':o_hash, 'objtype':objtype})
        #     self.conn.execute(s)
        #     self.session.commit()
    
    def tokey(self, obj):
        pass
        # logger.debug("tokey: Tokey obj=|%s|" % (obj))
        # if isinstance(obj, (URIRef, BNode)):
        #     logger.debug("tokey: URIRef/BNode - returning makeURIHash obj=|%s|" % (obj))
        #     return URI, self._makeURIHash(_tokey(obj))[1]
        # elif isinstance(obj, Literal):
        #     logger.debug("tokey: Literal - returning makeHash obj=|%s|" % (obj))
        #     return LITERAL, self._makeHash(_tokey(obj))
        # elif obj is Any:
        #     logger.debug("tokey: Any returning None, Any" % (obj))
        #     return None, Any
        # raise ValueError, obj
    
    def insert(self, obj):
        pass
        # logger.debug("insert: Insert obj=|%s|" % (str(obj)))
        # if isinstance(obj, (URIRef, BNode)):
        #     logger.debug("insert: URIRef/BNode - returning insertURI obj=|%s|" % (obj))
        #     return URI, self._insertURI(_tokey(obj))
        # elif isinstance(obj, Literal):
        #     logger.debug("insert: Literal - returning insertLiteral obj=|%s|" % (obj))
        #     return LITERAL, self._insertLiteral(_tokey(obj))
        # raise ValueError, obj
    
    def add(self, (subject, predicate, object), context=None, quoted=False):
        pass
        # """add: Add a triple to the store of triples."""
        # logger.debug(
        #     "Adding triple subject=|%s|, predicate=|%s|, object=|%s|, context=|%s|, quoted=|%s|" % \
        #         (subject, predicate, object, context, quoted))
        # tokey = self.insert
        # ts, s = tokey(subject)
        # tp, p = tokey(predicate)
        # to, o = tokey(object)
        # self._insertTriple(s, p, o, to)
    
    def remove(self, (subject, predicate, object), context=None):
        pass
        # logger.debug(
        #     "remove: Removing triple: subject=|%s|, predicate=|%s|, object=|%s|, context=|%s|" % \
        #         (subject, predicate, object, context))
        # tokey = self.tokey
        # where_clause = ''
        
        # if subject is not Any:
        #     ts, s = tokey(subject)
        #     where_clause += 'subject = %s' % s
        # if predicate is not Any:
        #     if where_clause:
        #         where_clause += ' AND '
        #     tp, p = tokey(predicate)
        #     where_clause += 'predicate = %s' % p
        # if object is not Any:
        #     if where_clause:
        #         where_clause += ' AND '
        #     to, o = tokey(object)
        #     where_clause += 'object = %s AND objtype = %s' % (o, to)
        
        # trip = self._triples
        # # conn = trip._connection
        # query = 'DELETE from %s' % trip.__table__.name
        # if where_clause:
        #     query += ' WHERE %s' % where_clause
        # logger.debug("REMOVE |%s|" % dir(self.conn))
        # logger.debug("REMOVE |%s|" % dir(trip.__table__))
        # self.conn.execute(query)
        # self.session.commit()
    
    def triples(self, (subject, predicate, object), context=None):
        pass
        # logger.debug(
        #     "triples: Triples for subject=|%s|, predicate=|%s|, object=|%s|, context=|%s|" % \
        #                 (subject, predicate, object, context))
        # tokey = self.tokey
        # where_clause = ''
        # if subject is not Any:
        #     ts, s = tokey(subject)
        #     where_clause += 'r1.hash = %s' % s
        # if predicate is not Any:
        #     if where_clause:
        #         where_clause += ' AND '
        #     tp, p = tokey(predicate)
        #     where_clause += 'r2.hash = %s' % p
        # if object is not Any:
        #     if where_clause:
        #         where_clause += ' AND '
        #     to, o = tokey(object)
        #     if to == URI:
        #         where_clause += 'r3.hash = %s' % o
        #     else:
        #         where_clause += 'l.hash = %s' % o
        
        # query = ("SELECT '<'||n1.value||r1.name||'>' AS subj, "
        #          "'<'||n2.value||r2.name||'>' AS pred, "
        #          "CASE WHEN t.objtype = %d "
        #          "THEN '<'||n3.value||r3.name||'>' "
        #          "ELSE l.value END AS obj, "
        #          "l.hash, r3.hash "
        #          "FROM resources r1, resources r2, "
        #          "namespaces n1, namespaces n2, triples t "
        #          "LEFT JOIN literals l ON t.object = l.hash "
        #          "LEFT JOIN resources r3 ON t.object = r3.hash "
        #          "LEFT JOIN namespaces n3 ON r3.ns = n3.hash "
        #          "WHERE t.subject = r1.hash AND "
        #          "r1.ns = n1.hash AND "
        #          "t.predicate = r2.hash AND "
        #          "r2.ns = n2.hash" % URI)
        # if where_clause:
        #     query += ' AND %s' % where_clause
        # query += ' ORDER BY subj, pred'
        # res = self.conn.execute(query).fetchall()
        # logger.debug("triples: %s triples retrieved" % len(res))
        # for t in res:
        #     triple = (_fromkey(t[0]), _fromkey(t[1]), _fromkey(t[2]))
        #     yield triple, None
    
    def namespace(self, prefix):
        pass
        # logger.debug("namespace: Namespace prefix=|%s|" % (prefix))
        # prefix = prefix.encode("utf-8")
        # prefix_ns = self._prefix_namespace.__table__
        # s = prefix_ns.select(prefix_ns.c.prefix == sql.bindparam('prefix'))
        # res = self.conn.execute(s, prefix=prefix).fetchall()
        # logger.debug("namespace: rowcount=|%s|" %len(res))
        # if not res:
        #     logger.debug("namespace: returning explicit None")
        #     return None
        # v = iter(res).next().ns
        # logger.debug("namespace: returning ns |%s|" % v)
        # return v
    
    def prefix(self, namespace):
        pass
        # logger.debug("prefix: Prefix namespace=|%s|" % (namespace))
        # namespace = namespace.encode("utf-8")
        # pns = self._prefix_namespace.__table__
        # s = pns.select(pns.c.ns == sql.bindparam('namespace'))
        # res = self.conn.execute(s, namespace=namespace).fetchall()
        # logger.debug("prefix: count=|%s|" % len(res))
        # if not res:
        #     logger.debug("prefix: returning explicit None")
        #     return None
        # p = iter(res).next().prefix
        # logger.debug("prefix: returning prefix |%s|" % p)
        # return p
    
    def bind(self, prefix, namespace):
        pass
        # logger.debug("bind: Bind prefix=|%s|, namespace=|%s|" % (prefix, namespace))
        # if namespace[-1] == "-":
        #     raise Exception("??")
        # pns = self._prefix_namespace.__table__
        # prefix = prefix.encode("utf-8")
        # namespace = namespace.encode("utf-8")
        # s = pns.select(and_(pns.c.ns == sql.bindparam('ns'),
        #                      pns.c.prefix == sql.bindparam('prefix')))
        # if not self.conn.execute(s, ns=namespace,prefix=prefix).fetchall():
        #     logger.debug("bind: Binding prefix=|%s"" namespace=|%s|" % (prefix, namespace))
        #     s = pns.insert(values={'prefix':prefix, 'ns':namespace})
        #     self.conn.execute(s)
        # else:
        #     logger.debug("bind: already bound prefix=|%s| namespace|%s|" % (prefix, namespace))
        # self.session.commit()
    
    def namespaces(self):
        pass
        # logger.debug("namespaces: Retrieving namespaces")
        # pns = self._prefix_namespace.__table__
        # s = pns.select()
        # res = self.conn.execute(s).fetchall()
        # for p in res:
        #     logger.debug("namespaces: yielding |%s| |%s|" % (p.prefix, URIRef(p.ns)))
        #     yield p.prefix, URIRef(p.ns)
    
    def __len__(self, context=None):
        pass
        # logger.debug("len: Getting length context=|%s|" % (context))
        # res = self._triples.__table__.select().execute().fetchall()
        # return len(res)

    def _fromkey(key):
        pass
        # logger.debug("_fromkey: %s" % key if key else 'None Key')
        # if key is None:
        #     return BNode(
        #         URIRef(Namespace("http://example.com/data")+"#%s" % \
        #             'later'))
        # if key.startswith("<") and key.endswith(">"):
        #     key = key[1:-1].decode("UTF-8")
        #     if key.startswith("_"):
        #         key = ''.join(splituri(key))
        #         return BNode(key)
        #     return URIRef(key)
        # elif key.startswith("_"):
        #     return BNode(key)
        # else:
        #     m = _literal.match(key)
        #     if m:
        #         d = m.groupdict()
        #         value = d["value"]
        #         value = unquote(value)
        #         value = value.decode("UTF-8")
        #         lang = d["lang"] or ''
        #         datatype = d["datatype"]
        #         return Literal(value, lang, datatype)
        #     else:
        #         msg = "Unknown Key Syntax: '%s'" % key
        #         raise Exception(msg)

    def _tokey(self, term):
        pass
        # logger.debug("_tokey: |%s|" % term)
        # if isinstance(term, URIRef):
        #     term = term.encode("UTF-8")
        #     if not '#' in term and not '/' in term:
        #         term = '%s%s' % (NO_URI, term)
        #     logger.debug("tokey |%s| is URIRef" % term)
        #     k =  '<%s>' % term
        # elif isinstance(term, BNode):
        #     logger.debug("tokey |%s| is BNode" % term)
        #     k =  '<%s>' % ''.join(splituri(term.encode("UTF-8")))
        # elif isinstance(term, Literal):
        #     language = term.language
        #     datatype = term.datatype
        #     value = quote(term.encode("UTF-8"))
        #     if language:
        #         language = language.encode("UTF-8")
        #         if datatype:
        #             datatype = datatype.encode("UTF-8")
        #             n3 = '"%s"@%s&<%s>' % (value, language, datatype)
        #         else:
        #             n3 = '"%s"@%s' % (value, language)
        #     else:
        #         if datatype:
        #             datatype = datatype.encode("UTF-8")
        #             n3 = '"%s"&<%s>' % (value, datatype)
        #         else:
        #             n3 = '"%s"' % value
        #     logger.debug("tokey |%s| is Literal" % term)
        #     k = n3
        # else:
        #     msg = "Unknown term Type for: %s" % term
        #     raise Exception(msg)
        # logger.debug("%s returning |%s|" % (inspect.stack()[0][3], k))
        # return k

    def splituri(uri):
        pass
        # logger.debug("splituri: Splitting URI |%s|" % uri)
        # if uri.startswith('<') and uri.endswith('>'):
        #     uri = uri[1:-1]
        # if uri.startswith('_'):
        #     uid = ''.join(uri.split('_'))
        #     return '_', uid
        # if '#' in uri:
        #     ns, local = uri.rsplit('#', 1)
        #     return ns + '#', local
        # if '/' in uri:
        #     ns, local = uri.rsplit('/', 1)
        #     return ns + '/', local
        # return NO_URI, uri
