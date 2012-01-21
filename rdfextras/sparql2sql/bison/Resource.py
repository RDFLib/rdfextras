from rdflib import BNode
from rdflib import URIRef
from rdflib import Variable
from rdfextras.sparql2sql.bison.Util import ListRedirect

class RDFTerm(object):
    """
    Common class for RDF terms
    """

class Resource(RDFTerm):
    """
    Represents a sigle resource in a triple pattern.  It consists of an identifier
    (URIRef or BNode) and a list of :class:`rdfextras.sparql2sql.bison.Triples.PropertyValue` instances
    """
    def __init__(self, identifier=None, propertyValueList=None):
        self.identifier = identifier is not None and identifier or BNode()
        self.propVals = propertyValueList is not None and propertyValueList or []

    def __repr__(self):
        resId = isinstance(self.identifier,BNode) and '_:' + self.identifier or self.identifier
        #print type(self.identifier)
        return "%s%s" % (
            resId,self.propVals and ' %s' % self.propVals or '')

    def extractPatterns(self) :
        for prop, objs in self.propVals:
            for obj in objs:
                yield (self.identifier, prop,obj)

    def __eq__(self, other):
        return (self.identifier == other.identifier and
                self.propVals == other.propVals)

class TwiceReferencedBlankNode(RDFTerm):
    """
    Represents BNode in triple patterns in this form:

    [ :prop1 :val1 ] :prop2 :val2
    """
    def __init__(self, props1, props2):
        self.identifier = BNode()
        self.propVals = list(set(props1 + props2))
    

class ParsedCollection(ListRedirect,RDFTerm):
    """
    An RDF Collection
    """
    reducable = False
    def __init__(self, graphNodeList=None):
        self.propVals = []
        if graphNodeList:
            self._list = graphNodeList
            self.identifier = Variable(BNode())
        else:
            self._list = graphNodeList and graphNodeList or []
            self.identifier = URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#nil')
        
    def setPropertyValueList(self, propertyValueList):
        self.propVals = propertyValueList
        
    def __repr__(self):
        return "<RDF Collection: %s>" % self._list

# Convenience
# from rdfextras.sparql2sql.bison.Resource import ParsedCollection
# from rdfextras.sparql2sql.bison.Resource import TwiceReferencedBlankNode
# from rdfextras.sparql2sql.bison.Resource import RDFTerm
# from rdfextras.sparql2sql.bison.Resource import Resource
