"""
SQLAlchemy Store, declarative Base implementation of rdflib's Store
"""

__metaclass__ = type

import re
import logging
from rdflib.store import Store
from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

logging.basicConfig(level=logging.ERROR,format="%(message)s")
logger = logging.getLogger('rdfextras.store.SQLAlchemy')
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

class Literals(Base):
    pass
_literals = Literals

class Namespaces(Base):
    pass
_ns = Namespaces

class PrefixNamespace(Base):
    pass
_prefix_namespace = PrefixNamespace

class Resources(Base):
    pass
_resources = Resources

class Triples(Base):
    pass
_triples = Triples

def add_indices():
    pass

class SQLAlchemy(Store):

    def __init__(self, uri=None, **kwargs):
        pass
    
    def open(self, uri=None, create=True, **kwargs):
        pass
    
    def close(self, commit_pending_transaction=False):
        pass
    
    def destroy(self, uri=None):
        pass
    
    def tokey(self, obj):
        pass
    
    def insert(self, obj):
        pass
    
    def add(self, (subject, predicate, object), context=None, quoted=False):
        pass
    
    def remove(self, (subject, predicate, object), context=None):
        pass
    
    def triples(self, (subject, predicate, object), context=None):
        pass
    
    def namespace(self, prefix):
        pass
    
    def namespaces(self):
        pass
    
    def prefix(self, namespace):
        pass
    
    def bind(self, prefix, namespace):
        pass
    
    def __len__(self, context=None):
        pass

    def _fromkey(key):
        pass

    def _tokey(self, term):
        pass

    def _makeHash(self, value):
        pass
    
    def _insertLiteral(self, value):
        pass
    
    def _insertURI(self, value=None, namespace=None, local_name=None):
        pass
    
    def _insertTriple(self, s_hash, p_hash, o_hash, objtype=URI):
        pass
    
    def _makeURIHash(self, value=None, namespace=None, local_name=None):
        pass
    
    def splituri(uri):
        pass
