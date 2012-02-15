"""
Utility functions associated with RDF terms:

- normalizing (to 64 bit integers via half-md5-hashes)
- escaping literals for SQL persistence

"""
try:
    from hashlib import md5
except ImportError:
    from md5 import md5
from rdflib.term import Literal
from rdfextras.store.REGEXMatching import REGEXTerm
from rdflib.graph import Graph
from rdflib.graph import QuotedGraph
from rdfextras.utils.termutils import SUBJECT
from rdfextras.utils.termutils import PREDICATE
from rdfextras.utils.termutils import OBJECT
from rdfextras.utils.termutils import CONTEXT
from rdfextras.utils.termutils import term2Letter
from rdfextras.utils.termutils import escape_quotes

Any = None

DATATYPE_INDEX = CONTEXT + 1
LANGUAGE_INDEX = CONTEXT + 2

SlotPrefixes = {
     SUBJECT   : 'subject',
     PREDICATE : 'predicate',
     OBJECT    : 'object',
     CONTEXT   : 'context',
     DATATYPE_INDEX : 'dataType',
     LANGUAGE_INDEX : 'language'
}

POSITION_LIST = [SUBJECT,PREDICATE,OBJECT,CONTEXT]

def EscapeQuotes(qstr):
    return escape_quotes(qstr)

def dereferenceQuad(index,quad):
    assert index <= LANGUAGE_INDEX, "Invalid Quad Index"
    if index == DATATYPE_INDEX:
        return isinstance(quad[OBJECT],Literal) and \
                                quad[OBJECT].datatype or None
    elif index == LANGUAGE_INDEX:
        return isinstance(quad[OBJECT],Literal) and \
                                quad[OBJECT].language or None
    else:
        return quad[index]

def genQuadSlots(quads, useSignedInts=False):
    return [QuadSlot(index, quads[index], useSignedInts)
            for index in POSITION_LIST]

def normalizeValue(value, termType, useSignedInts=False):
    if value is None:
        value = u'http://www.w3.org/2002/07/owl#NothingU'
    else:
        value = (isinstance(value, Graph) \
                        and value.identifier or str(value.encode('utf-8'))) + termType
    unsigned_hash = int(md5(
                      isinstance(value, unicode) and value.encode('utf-8')
                                                 or value)
                    .hexdigest()[:16], 16)
    if useSignedInts:
        return makeSigned(unsigned_hash)
    else:
        return unsigned_hash

bigint_signed_max = 2**63

def makeSigned(bigint):
    if bigint > bigint_signed_max:
        return bigint_signed_max - bigint
    else:
        return bigint

def normalizeNode(node, useSignedInts=False):
    return normalizeValue(node, term2Letter(node), useSignedInts)

class QuadSlot(object):
    def __repr__(self):
        #NOTE: http://docs.python.org/ref/customization.html
        return "QuadSlot(%s,%s,%s)" % \
                (SlotPrefixes[self.position],self.term,self.md5Int)
    
    def __init__(self, position, term, useSignedInts=False):
        assert position in POSITION_LIST, "Unknown quad position: %s" % \
            position
        self.position = position
        self.term = term
        self.termType = term2Letter(term)
        self.useSignedInts = useSignedInts
        self.md5Int = normalizeValue(term, term2Letter(term), useSignedInts)
    
    def EscapeQuotes(self,qstr):
        return escape_quotes(qstr)

    def normalizeTerm(self):
        if isinstance(self.term, (QuotedGraph, Graph)):
            return self.term.identifier.encode('utf-8')
        elif isinstance(self.term,Literal):
            return self.EscapeQuotes(self.term).encode('utf-8')
        elif self.term is None or isinstance(self.term,(list,REGEXTerm)):
            return self.term
        else:
            return self.term.encode('utf-8')
    
    def getDatatypeQuadSlot(self):
        if self.termType == 'L' and self.term.datatype:
            return self.__class__(SUBJECT, self.term.datatype,
                                  self.useSignedInts)
        return None
    
# # Convenience for expanding "from QuadSlot import *"
# from rdfextras.store.FOPLRelationalModel.QuadSlot import Any
# from rdfextras.store.FOPLRelationalModel.QuadSlot import DATATYPE_INDEX
# from rdfextras.store.FOPLRelationalModel.QuadSlot import LANGUAGE_INDEX
# from rdfextras.store.FOPLRelationalModel.QuadSlot import SlotPrefixes
# from rdfextras.store.FOPLRelationalModel.QuadSlot import POSITION_LIST
# from rdfextras.store.FOPLRelationalModel.QuadSlot import bigint_signed_max 
# from rdfextras.store.FOPLRelationalModel.QuadSlot import dereferenceQuad
# from rdfextras.store.FOPLRelationalModel.QuadSlot import genQuadSlots
# from rdfextras.store.FOPLRelationalModel.QuadSlot import normalizeValue
# from rdfextras.store.FOPLRelationalModel.QuadSlot import makeSigned
# from rdfextras.store.FOPLRelationalModel.QuadSlot import normalizeNode
