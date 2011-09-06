from rdflib import Namespace
from rdflib import URIRef

EMPTY_STRING=""

class PrefixDeclaration(object):
    """
    PrefixDecl ::= 'PREFIX' QNAME_NS Q_IRI_REF
    
    See: http://www.w3.org/TR/rdf-sparql-query/#rPrefixDecl
    """
    def __init__(self,qName,iriRef):
        self.namespaceMapping = Namespace(iriRef)
        self.qName = qName[:-1]
        self.base = iriRef
        # print(self.base,self.qName,self.namespaceMapping.knows)

    def __repr__(self):
        return "%s -> %s" % (self.base, self.qName)

    def __eq__(self, other):
        return (self.namespaceMapping == other.namespaceMapping and
                self.qName == other.qName)

class BaseDeclaration(URIRef):
    """
    BaseDecl ::= 'BASE' Q_IRI_REF
    
    """
    pass

# Convenience
# from rdfextras.sparql2sql.bison.Bindings import EMPTY_STRING
# from rdfextras.sparql2sql.bison.Bindings import PrefixDeclaration
# from rdfextras.sparql2sql.bison.Bindings import BaseDeclaration
