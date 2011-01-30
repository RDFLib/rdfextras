#!/d/Bin/Python/python.exe
# -*- coding: utf-8 -*-
#
"""
This is an RDFLib store around Ivan Herman et al.'s SPARQL service wrapper. 
This was first done in layer-cake, and then ported to rdflib 3 and rdfextras

This version works with vanilla SPARQLWrapper installed by easy_install or similar

Changes:
- Layercake adding support for namespace binding, I removed it again to work with vanilla SPARQLWrapper
- JSON object mapping support suppressed
- Replaced '4Suite-XML Domlette with Elementtree
- Incorporated as an rdflib store

"""

__version__ = "1.02"
__authors__  = u"Ivan Herman, Sergio Fernández, Carlos Tejo Alonso, Gunnar Aastrand Grimnes"
__license__ = u'W3C® SOFTWARE NOTICE AND LICENSE, http://www.w3.org/Consortium/Legal/2002/copyright-software-20021231'
__contact__ = 'Ivan Herman, ivan_herman@users.sourceforge.net'
__date__    = "2011-01-30"

import re
from SPARQLWrapper import SPARQLWrapper, XML
from SPARQLWrapper.Wrapper import QueryResult


import xml.etree.ElementTree

from rdfextras.store.REGEXMatching import NATIVE_REGEX

from rdflib.store import Store
from rdflib       import Variable, Namespace, BNode, URIRef, Literal


BNODE_IDENT_PATTERN = re.compile('(?P<label>_\:[^\s]+)')
SPARQL_NS        = Namespace('http://www.w3.org/2005/sparql-results#')
sparqlNsBindings = {u'sparql':SPARQL_NS}
xml.etree.ElementTree._namespace_map["sparql"]=SPARQL_NS

def TraverseSPARQLResultDOM(doc,asDictionary=False):
    """
    Returns a generator over tuples of results
    by (4Suite) XPath evaluation over the result XML
    """
    
    # namespace handling in elementtree xpath sub-set is not pretty :(
    vars = [Variable(v.attrib["name"]) for v in
             doc.findall('/{http://www.w3.org/2005/sparql-results#}head/{http://www.w3.org/2005/sparql-results#}variable')]
    for result in doc.findall('/{http://www.w3.org/2005/sparql-results#}results/{http://www.w3.org/2005/sparql-results#}result'):
        currBind = {}
        values = []
        for binding in result.findall('{http://www.w3.org/2005/sparql-results#}binding'):
            varVal = binding.attrib["name"]
            var = Variable(varVal)
            term = CastToTerm(binding.findall('*')[0])
            values.append(term)
            currBind[var]=term
        if asDictionary:
            yield currBind,vars
        else:
            yield values[0] if len(values)==1 else tuple(values),vars

def localName(qname): 
    # wtf - elementtree cant do this for me
    return qname[qname.index("}")+1:]

def CastToTerm(node):
    """
    Helper function that casts domlette node in SPARQL results
    to appropriate rdflib term
    """
    if node.tag == '{%s}bnode'%SPARQL_NS:
        return BNode(node.text)
    elif node.tag == '{%s}uri'%SPARQL_NS:
        return URIRef(node.text)
    elif node.tag == '{%s}literal'%SPARQL_NS:
        if 'datatype' in node.attrib:
            dT = URIRef(node.attrib['datatype'])
            if False:#not node.xpath('*'):
                return Literal('',datatype=dT)
            else:
                return Literal(node.text,
                               datatype=dT)
        else:
            if False:#not node.xpath('*'):
                return Literal('')
            else:
                return Literal(node.text)
    else:
        raise Exception('Unknown answer type')

class SPARQLResult(QueryResult):
    """
    Query result class for SPARQL

    xml   : as an XML string conforming to the SPARQL XML result format: http://www.w3.org/TR/rdf-sparql-XMLres/
    python: as Python objects
    json  : as JSON
    graph : as an RDFLib Graph - for CONSTRUCT and DESCRIBE queries
    """
    def __init__(self,result):
        self.result    = xml.etree.ElementTree.parse(result)
        self.noAnswers = 0
        self.askAnswer = None

    def _parseResults(self):
        self.askAnswer=self.result.findall('/{http://www.w3.org/2005/sparql-results#}boolean')

    def __len__(self):
        raise NotImplementedError("Results are an iterable!")

    def __iter__(self):
        """Iterates over the result entries"""
        self._parseResults()
        if not self.askAnswer:
            for rt,vars in TraverseSPARQLResultDOM(self.result):
                self.noAnswers += 1
                yield rt

    def serialize(self,format='xml'):
        if format == 'python':
            self._parseResults()
            if self.askAnswer:
                return bool(self.askAnswer=='true')
            else:
                return self
        elif format == 'xml':
            return self.result
        else:
           raise Exception("Result format not implemented: %s"%format)




class SPARQLStore(SPARQLWrapper,Store):
    """
    An RDFLib store around a SPARQL endpoint
    """
    context_aware = True
    formula_aware = False
    transaction_aware = False
    regex_matching = NATIVE_REGEX
    batch_unification = False
    def __init__(self,identifier=None,bNodeAsURI = False):
        super(SPARQLStore, self).__init__(identifier,returnFormat=XML)
        self.bNodeAsURI = bNodeAsURI

    #Database Management Methods
    def create(self, configuration):
        raise TypeError('The SPARQL store is read only')

    def open(self, configuration, create=False):
        """
        Opens the store specified by the configuration string. If
        create is True a store will be created if it does not already
        exist. If create is False and a store does not already exist
        an exception is raised. An exception is also raised if a store
        exists, but there is insufficient permissions to open the
        store.
        """
        if create: raise Exception("Cannot create a SPARQL Endpoint")


    def destroy(self, configuration):
        """
        FIXME: Add documentation
        """
        raise TypeError('The SPARQL store is read only')

    #Transactional interfaces
    def commit(self):
        """ """
        raise TypeError('The SPARQL store is read only')

    def rollback(self):
        """ """
        raise TypeError('The SPARQL store is read only')


    def add(self, (subject, predicate, obj), context=None, quoted=False):
        """ Add a triple to the store of triples. """
        raise TypeError('The SPARQL store is read only')

    def addN(self, quads):
        """
        Adds each item in the list of statements to a specific context. The quoted argument
        is interpreted by formula-aware stores to indicate this statement is quoted/hypothetical.
        Note that the default implementation is a redirect to add
        """
        raise TypeError('The SPARQL store is read only')

    def remove(self, (subject, predicate, obj), context):
        """ Remove a triple from the store """
        raise TypeError('The SPARQL store is read only')

    def query(self,  graph,
                     queryStringOrObj,
                     initNs={},
                     initBindings={},
                     DEBUG=False):
        self.debug = DEBUG
        assert isinstance(queryStringOrObj,basestring)
        #self.setNamespaceBindings(initNs)
        if len(initNs)>0: 
            raise Exception("initNs not supported.")
        if len(initBindings)>0: 
            raise Exception("initBindings not supported.")
            
        self.setQuery(queryStringOrObj)
        return SPARQLResult(SPARQLWrapper.query(self).response)

    def triples(self, (subject, predicate, obj), context=None):
        """
        SELECT ?subj ?pred ?obj WHERE { ?subj ?pred ?obj }
        """

        subjVar = Variable('subj')
        predVar = Variable('pred')
        objVar  = Variable('obj')

        termsSlots = {}
        selectVars = []
        if subject is not None:
            termsSlots[subjVar] = subject
        else:
            selectVars.append(subjVar)
        if predicate is not None:
            termsSlots[predVar] = predicate
        else:
            selectVars.append(predVar)
        if obj is not None:
            termsSlots[objVar] = obj
        else:
            selectVars.append(objVar)

        query ="SELECT %s WHERE { %s %s %s }"%(
            ' '.join([term.n3() for term in selectVars]),
            termsSlots.get(subjVar, subjVar).n3(),
            termsSlots.get(predVar, predVar).n3(),
            termsSlots.get(objVar , objVar ).n3()
        )

        self.setQuery(query)
        
        doc = xml.etree.ElementTree.parse(SPARQLWrapper.query(self).response)
        #xml.etree.ElementTree.dump(doc)
        for rt,vars in TraverseSPARQLResultDOM(doc,asDictionary=True):
            
            yield (rt.get(subjVar,subject),
                   rt.get(predVar,predicate),
                   rt.get(objVar,obj)),None

    def triples_choices(self, (subject, predicate, object_),context=None):
        """
        A variant of triples that can take a list of terms instead of a single
        term in any slot.  Stores can implement this to optimize the response time
        from the import default 'fallback' implementation, which will iterate
        over each term in the list and dispatch to tripless
        """
        raise NotImplementedError('Triples choices currently not supported')

    def __len__(self, context=None):
        raise NotImplementedError("For performance reasons, this is not supported")

    def contexts(self, triple=None):
        """
        iterates over results to SELECT ?NAME { GRAPH ?NAME { ?s ?p ?o } }
        returning instances of this store with the SPARQL wrapper
        object updated via addNamedGraph(?NAME)
        This causes a named-graph-uri key / value  pair to be sent over the protocol
        """
        raise NotImplementedError(".contexts(..) not supported")
        # self.setQuery("SELECT ?NAME { GRAPH ?NAME { ?s ?p ?o } }")
        # doc = self.query().convert()
        # for result in doc.xpath('/{http://www.w3.org/2005/sparql-results#}sparql/{http://www.w3.org/2005/sparql-results#}results/{http://www.w3.org/2005/sparql-results#}result',
        #                         explicitNss=sparqlNsBindings):
        #     statmentTerms = {}
        #     for binding in result.xpath('{http://www.w3.org/2005/sparql-results#}binding',
        #                                 explicitNss=sparqlNsBindings):
        #         term = CastToTerm(binding.xpath('*')[0])
        #         newStore = SPARQLStore(self.baseURI)
        #         newStore.addNamedGraph(term)
        #         yield Graph(self,term)

    #Namespace persistence interface implementation
    def bind(self, prefix, namespace):
        self.nsBindings[prefix]=namespace

    def prefix(self, namespace):
        """ """
        return dict([(v,k) for k,v in self.nsBindings.items()]).get(namespace)

    def namespace(self, prefix):
        return self.nsBindings.get(prefix)

    def namespaces(self):
        for prefix,ns in self.nsBindings.items():
            yield prefix,ns
