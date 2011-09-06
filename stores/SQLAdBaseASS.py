"""
SQLAdBaseASS.py
SQLAlchemy declarativeBase implementation based on AbstractSQLStore.
"""

__metaclass__ = type

import logging
import re
import uuid
from urllib import quote, unquote
from rdflib.store import Store
from rdflib.term import Literal, URIRef, BNode
from rdflib.namespace import Namespace
import sqlalchemy
from sqlalchemy import *
from sqlalchemy import sql
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

logging.basicConfig(level=logging.ERROR,format="%(message)s")
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.ERROR)


_literal = re.compile(
    r'''"(?P<value>[^@&]*)"(?:@(?P<lang>[^&]*))?(?:&<(?P<datatype>.*)>)?''')

global metadata
global Session
metadata = MetaData()
Base = declarative_base()
Session = sessionmaker()

LITERAL = 0
URI = 1
NO_URI = 'uri://oops/'
Any = None

class Literals(Base):
    __tablename__ = 'literals'
    
    hashno = Column(Integer, index=True, primary_key=True)
    value = Column(Text, nullable=False)
    
    def __repr__(self):
        return "<Literal(%s)>" % (self.value)
    

_literals = Literals

class Namespaces(Base):
    __tablename__ = 'namespaces'
    
    hashno = Column(Integer, index=True, primary_key=True)
    value = Column(String(1000), nullable=False)
    
    def __repr__(self):
        return "<Namespace(%s)>" % (self.value)
    

_ns = Namespaces

class PrefixNamespace(Base):
    __tablename__ = 'prefix_namespace'
    
    prefix = Column(String(1000), index=True, primary_key=True)
    ns = Column(String(1000), index=True)
    
    def __repr__(self):
        return "<PrefixNamespace(%s: %s)>" % (self.prefix, self.ns)
    

_prefix_namespace = PrefixNamespace

class Resources(Base):
    __tablename__ = 'resources'
    
    hashno = Column(Integer, index=True, primary_key=True)
    ns = Column(Integer, index=True)
    name = Column(String(1000), index=True)
    
    def __repr__(self):
        return "<Resource(%s: %s)>" % (self.ns, self.name)
    

_resources = Resources

class Triples(Base):
    __tablename__ = 'triples'
    
    subject = Column(Integer, index=True, primary_key=True)
    predicate = Column(Integer, index=True)
    object = Column(Integer, index=True)
    objtype = Column(Integer, index=True, default=LITERAL)


_triples = Triples

Index('idx_ns_prefix', PrefixNamespace.ns, PrefixNamespace.prefix)
Index('idx_ns_name', Resources.ns, Resources.name)
Index('idx_hash_ns_name', Resources.hashno, Resources.ns, Resources.name)
Index('idx_object_objtype', Triples.object, Triples.objtype)
Index('idx_subject_predicate', Triples.subject, Triples.predicate)
Index('idx_subject_object_objtype', Triples.subject, Triples.object,
                                    Triples.objtype)
Index('idx_predicate_object_objtype', Triples.predicate, Triples.object,
                                        Triples.objtype)

def splituri(uri):
    if uri.startswith('<') and uri.endswith('>'):
        uri = uri[1:-1]
    if uri.startswith('_'):
        uid = ''.join(uri.split('_'))
        return '_', uid
    if '#' in uri:
        ns, local = uri.rsplit('#', 1)
        return ns + '#', local
    if '/' in uri:
        ns, local = uri.rsplit('/', 1)
        return ns + '/', local
    return NO_URI, uri

def _fromkey(key):
    if key is None:
        return BNode(URIRef(
            Namespace("http://purl.org/net/")+"#%s" % \
                                            uuid.uuid4()))
    if key.startswith("<") and key.endswith(">"):
        key = key[1:-1].decode("UTF-8")
        if key.startswith("_"):
            key = ''.join(splituri(key))
            return BNode(key)
        return URIRef(key)
    elif key.startswith("_"):
        return BNode(key)
    else:
        m = _literal.match(key)
        if m:
            d = m.groupdict()
            value = d["value"]
            value = unquote(value)
            value = value.decode("UTF-8")
            lang = d["lang"] or ''
            datatype = d["datatype"]
            return Literal(value, lang, datatype)
        else:
            msg = "Unknown Key Syntax: '%s'" % key
            raise Exception(msg)
    

def _tokey(term):
    if isinstance(term, URIRef):
        term = term.encode("UTF-8")
        if not '#' in term and not '/' in term:
            term = '%s%s' % (NO_URI, term)
        return '<%s>' % term
    elif isinstance(term, BNode):
        return '<%s>' % ''.join(splituri(term.encode("UTF-8")))
    elif isinstance(term, Literal):
        language = term.language
        datatype = term.datatype
        value = quote(term.encode("UTF-8"))
        if language:
            language = language.encode("UTF-8")
            if datatype:
                datatype = datatype.encode("UTF-8")
                n3 = '"%s"@%s&<%s>' % (value, language, datatype)
            else:
                n3 = '"%s"@%s' % (value, language)
        else:
            if datatype:
                datatype = datatype.encode("UTF-8")
                n3 = '"%s"&<%s>' % (value, datatype)
            else:
                n3 = '"%s"' % value
        return n3
    else:
        msg = "Unknown term Type for: %s" % term
        raise Exception(msg)
    


class SQLAlchemyStore(Store):
    
    context_aware = True
    formula_aware = True
    __open = False
    _triples = Triples
    _literals = Literals
    _ns = Namespaces
    _prefix_namespace = PrefixNamespace
    _resources = Resources
    __node_pickler = None
    _connection = None
    echo = False
    
    tables = ('_triples', '_literals', '_ns',
              '_prefix_namespace', '_resources')

    def __init__(self, uri=None):
        self.uri = uri
        super(SQLAlchemyStore, self).__init__(uri)
    
    def open(self, uri='sqlite://:memory:', create=True):
        if self.__open:
            return
        self.__open = True
        
        from sqlalchemy import create_engine
        engine = create_engine(uri, echo=False)
        Base.metadata.bind = engine
        if create:
            try:
                Base.metadata.create_all(checkfirst=True)
            except Exception, e: # TODO: should catch more specific exception
                print(e)
                _logger.warning(e)
                return 0
        Session.configure(bind=engine)
        self.session = Session()
        self._connection = engine.connect()
        # useful for debugging
        self._connection.debug = False
        self.conn = self._connection
        _logger.debug("Graph opened, %s engine bound." % (engine.name))
        return True
    
    def close(self,commit_pending_transaction=False):
        if not self.__open:
            raise ValueError, 'Not open'
        self.__open = False
        if commit_pending_transaction:
            self.transaction.commit()
        self.session.close()
    
    def destroy(self, uri='sqlite://:memory:'):
        if self.__open:
            return
        from sqlalchemy import create_engine
        Base.metadata.bind = create_engine(uri)
        try:
            Base.metadata.drop_all(checkfirst=True)
        except Exception, e: # TODO: should catch more specific exception
            print(e)
            _logger.warning(e)
            return 0
        return 1
    
    def _makeHash(self, value):
        # XXX We will be using python's hash, but it should be a database
        # hash eventually.
        return hash(value)
    
    def _insertLiteral(self, value):
        v_hash = self._makeHash(value)
        lit = self._literals
        if not self.session.query(lit).filter(hashno == v_hash).count():
            new_lit = lit()
            new_lit.hashno = v_hash
            new_lit.value = value
            self.session.add(new_lit)
            self.session.commit()
        return v_hash
    
    def _makeURIHash(self, value=None, namespace=None, local_name=None):
        if namespace is None and local_name is None:
            namespace, local_name = splituri(value)
        ns_hash = self._makeHash(namespace)
        rsrc_hash = self._makeHash((ns_hash, local_name))
        return ns_hash, rsrc_hash
    
    def _insertURI(self, value=None, namespace=None, local_name=None):
        if namespace is None and local_name is None:
            namespace, local_name = splituri(value)
        ns_hash, rsrc_hash = self._makeURIHash(value, namespace, local_name)
        ns = self._ns
        res = self.session.query(ns).filter_by(hashno = sql.bindparam('ns_hash')).count()
        _logger.debug("Hash %s", ns_hash)
        _logger.debug("Res %s", res)
        if not res:
            new_ns = ns()
            new_ns.hashno = ns_hash
            new_ns.value = namespace
            _logger.debug("New ns %s" % new_ns)
            self.session.add(new_ns)
        rsrc = self._resources
        if not self.session.query(rsrc).filter_by(hashno = sql.bindparam('rsrc_hash')).count():
            new_resource = rsrc()
            new_resource.hashno = rsrc_hash
            new_resource.ns = ns_hash
            new_resource.name = local_name
            _logger.debug("New resource %s" % new_resource)
            self.session.add(new_resource)
        self.session.commit()
        return rsrc_hash
    
    def _insertTriple(self, s_hash, p_hash, o_hash, objtype=URI):
        trip = self._triples
        if not self.session.query(trip).filter(
                            and_(trip.subject == s_hash,
                                 trip.predicate == p_hash,
                                 trip.object == o_hash)).count():
            new_triple = trip()
            new_triple.subject = s_hash
            new_triple.predicate = p_hash
            new_triple.object = o_hash
            new_triple.objtype = objtype
            self.session.add(new_triple)
            self.session.commit()
    
    def tokey(self, obj):
        if isinstance(obj, (URIRef, BNode)):
            return URI, self._makeURIHash(_tokey(obj))[1]
        elif isinstance(obj, Literal):
            return LITERAL, self._makeHash(_tokey(obj))
        elif obj is Any:
            return None, Any
        raise ValueError, obj
    
    def insert(self, obj):
        if isinstance(obj, (URIRef, BNode)):
            return URI, self._insertURI(_tokey(obj))
        elif isinstance(obj, Literal):
            return LITERAL, self._insertLiteral(_tokey(obj))
        raise ValueError, obj
    
    def add(self, (subject, predicate, object), context=None, quoted=False):
        """
        Add a triple to the store of triples.
        """
        tokey = self.insert
        ts, s = tokey(subject)
        tp, p = tokey(predicate)
        to, o = tokey(object)
        self._insertTriple(s, p, o, to)
    
    def remove(self, (subject, predicate, object), context=None):
        tokey = self.tokey
        where_clause = ''
        if subject is not Any:
            ts, s = tokey(subject)
            where_clause += 'subject = %s' % s
        if predicate is not Any:
            if where_clause:
                where_clause += ' AND '
            tp, p = tokey(predicate)
            where_clause += 'predicate = %s' % p
        if object is not Any:
            if where_clause:
                where_clause += ' AND '
            to, o = tokey(object)
            where_clause += 'object = %s AND objtype = %s' % (o, to)
        
        trip = self._triples
        conn = self._connection
        query = 'DELETE from %s' % trip.__tablename__
        if where_clause:
            query += ' WHERE %s' % where_clause
        conn.execute(query)
    
    def triples(self, (subject, predicate, object), context=None):
        conn = self._connection
        
        tokey = self.tokey
        where_clause = ''
        if subject is not Any:
            ts, s = tokey(subject)
            where_clause += 'r1.hashno = %s' % s
        if predicate is not Any:
            if where_clause:
                where_clause += ' AND '
            tp, p = tokey(predicate)
            where_clause += 'r2.hashno = %s' % p
        if object is not Any:
            if where_clause:
                where_clause += ' AND '
            to, o = tokey(object)
            if to == URI:
                where_clause += 'r3.hashno = %s' % o
            else:
                where_clause += 'l.hashno = %s' % o
                
        query = ("SELECT '<'||n1.value||r1.name||'>' AS subj, "
                 "'<'||n2.value||r2.name||'>' AS pred, "
                 "CASE WHEN t.objtype = %d "
                 "THEN '<'||n3.value||r3.name||'>' "
                 "ELSE l.value END AS obj, "
                 "l.hashno, r3.hashno "
                 "FROM resources r1, resources r2, "
                 "namespaces n1, namespaces n2, triples t "
                 "LEFT JOIN literals l ON t.object = l.hashno "
                 "LEFT JOIN resources r3 ON t.object = r3.hashno "
                 "LEFT JOIN namespaces n3 ON r3.ns = n3.hashno "
                 "WHERE t.subject = r1.hashno AND "
                 "r1.ns = n1.hashno AND "
                 "t.predicate = r2.hashno AND "
                 "r2.ns = n2.hashno" % URI)
        if where_clause:
            query += ' AND %s' % where_clause
        query += ' ORDER BY subj, pred'
        res = conn.execute(query)
        for t in res:
            triple = (_fromkey(t[0]), _fromkey(t[1]), _fromkey(t[2]))
            yield triple, None
    
    def namespace(self, prefix):
        _logger.debug("Creating namespace %s" % (prefix))
        prefix = prefix.encode("utf-8")
        prefix_ns = self._prefix_namespace
        if not self.session.query(prefix_ns).filter(prefix_ns.prefix == prefix).count():
            return None
        res = iter(res).next().ns
        _logger.debug("Returning namespace %s" % res)
        return res
    
    def prefix(self, namespace):
        namespace = namespace.encode("utf-8")
        pns = self._prefix_namespace
        res = self.session.query(pns).filter(pns.ns == namespace)
        if not res.count():
            return None
        return iter(res.all()).next().prefix
    
    def bind(self, prefix, namespace):
        if namespace[-1] == "-":
            raise Exception("??")
        pns = self._prefix_namespace
        prefix = prefix.encode("utf-8")
        namespace = namespace.encode("utf-8")
        if not self.session.query(pns).filter(and_((pns.ns == namespace), (pns.prefix == prefix))).count():
            new_pns = pns()
            new_pns.prefix = prefix
            new_pns.ns = namespace
            self.session.add(new_pns)
            self.session.flush()
    
    def namespaces(self):
        pns = self._prefix_namespace
        for p in self.session.query(pns).all():
            yield p.prefix, URIRef(p.ns)
    
    def __len__(self):
        return self._triples.select().count()
    

    