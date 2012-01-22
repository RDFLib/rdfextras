#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
RDFLib Python binding for OWL Abstract Syntax

see: http://www.w3.org/TR/owl-semantics/syntax.html
     http://owl-workshop.man.ac.uk/acceptedLong/submission_9.pdf

3.2.3 Axioms for complete classes without using owl:equivalentClass

  Named class description of type 2 (with owl:oneOf) or type 4-6 
  (with owl:intersectionOf, owl:unionOf or owl:complementOf
  
Uses Manchester Syntax for __repr__  

>>> exNs = Namespace('http://example.com/')        
>>> namespace_manager = NamespaceManager(Graph())
>>> namespace_manager.bind('ex', exNs, override=False)
>>> namespace_manager.bind('owl', OWL_NS, override=False)
>>> g = Graph()    
>>> g.namespace_manager = namespace_manager

Now we have an empty graph, we can construct OWL classes in it
using the Python classes defined in this module

>>> a = Class(exNs.Opera,graph=g)

Now we can assert rdfs:subClassOf and owl:equivalentClass relationships 
(in the underlying graph) with other classes using the 'subClassOf' 
and 'equivalentClass' descriptors which can be set to a list
of objects for the corresponding predicates.

>>> a.subClassOf = [exNs.MusicalWork]

We can then access the rdfs:subClassOf relationships

>>> print list(a.subClassOf)
[Class: ex:MusicalWork ]

This can also be used against already populated graphs:

#>>> owlGraph = Graph().parse(OWL_NS)
#>>> namespace_manager.bind('owl', OWL_NS, override=False)
#>>> owlGraph.namespace_manager = namespace_manager
#>>> list(Class(OWL_NS.Class,graph=owlGraph).subClassOf)
#[Class: rdfs:Class ]

Operators are also available.  For instance we can add ex:Opera to the extension
of the ex:CreativeWork class via the '+=' operator

>>> a
Class: ex:Opera SubClassOf: ex:MusicalWork
>>> b = Class(exNs.CreativeWork,graph=g)
>>> b += a
>>> print list(a.subClassOf) # doctest +SKIP
[Class: ex:CreativeWork , Class: ex:MusicalWork ]

And we can then remove it from the extension as well

>>> b -= a
>>> a
Class: ex:Opera SubClassOf: ex:MusicalWork

Boolean class constructions can also  be created with Python operators
For example, The | operator can be used to construct a class consisting of a owl:unionOf 
the operands:

>>> c =  a | b | Class(exNs.Work,graph=g)
>>> c
( ex:Opera or ex:CreativeWork or ex:Work )

Boolean class expressions can also be operated as lists (using python list operators)

>>> del c[c.index(Class(exNs.Work,graph=g))]
>>> c
( ex:Opera or ex:CreativeWork )

The '&' operator can be used to construct class intersection:
      
>>> woman = Class(exNs.Female,graph=g) & Class(exNs.Human,graph=g)
>>> woman.identifier = exNs.Woman
>>> woman
( ex:Female and ex:Human )
>>> len(woman)
2

Enumerated classes can also be manipulated

>>> contList = [Class(exNs.Africa,graph=g),Class(exNs.NorthAmerica,graph=g)]
>>> EnumeratedClass(members=contList,graph=g)
{ ex:Africa ex:NorthAmerica }

owl:Restrictions can also be instanciated:

>>> Restriction(exNs.hasParent,graph=g,allValuesFrom=exNs.Human)
( ex:hasParent only ex:Human )

Restrictions can also be created using Manchester OWL syntax in 'colloquial' Python 
>>> exNs.hasParent |some| Class(exNs.Physician,graph=g)
( ex:hasParent some ex:Physician )

>>> Property(exNs.hasParent,graph=g) |max| Literal(1)
( ex:hasParent max 1 )

#>>> print g.serialize(format='pretty-xml')

"""
import itertools
import os
from pprint import pprint

from rdflib import BNode
from rdflib import Literal
from rdflib import Namespace
from rdflib import RDF
from rdflib import RDFS
from rdflib import URIRef
from rdflib import Variable
from rdflib import plugin
from rdflib import query
from rdflib.graph import Graph
from rdflib.collection import Collection
from rdflib.namespace import XSD as _XSD_NS
from rdflib.namespace import NamespaceManager
from rdflib.store import Store
from rdflib.term import Identifier
from rdflib.util import first

"""
From: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/384122

Python has the wonderful "in" operator and it would be nice to have additional 
infix operator like this. This recipe shows how (almost) arbitrary infix 
operators can be defined.

"""

plugin.register('sparql', query.Processor,
    'rdfextras.sparql.processor', 'Processor')

plugin.register('sparql', query.Result,
    'rdfextras.sparql.query', 'SPARQLQueryResult')

plugin.register('xml', query.ResultSerializer, 
    'rdfextras.sparql.query','SPARQLQueryResult')

plugin.register('json', query.ResultSerializer, 
    'rdfextras.sparql.query','SPARQLQueryResult')


# definition of an Infix operator class
# this recipe also works in jython
# calling sequence for the infix is either:
#  x |op| y
# or:
# x <<op>> y

class Infix:
    def __init__(self, function):
        self.function = function
    def __ror__(self, other):
        return Infix(lambda x, self=self, other=other: self.function(other, x))
    def __or__(self, other):
        return self.function(other)
    def __rlshift__(self, other):
        return Infix(lambda x, self=self, other=other: self.function(other, x))
    def __rshift__(self, other):
        return self.function(other)
    def __call__(self, value1, value2):
        return self.function(value1, value2)

OWL_NS = Namespace("http://www.w3.org/2002/07/owl#")

nsBinds = {
    'skos': 'http://www.w3.org/2004/02/skos/core#',
    'rdf' : RDF,
    'rdfs': RDFS,
    'owl' : OWL_NS,
    'list' : URIRef('http://www.w3.org/2000/10/swap/list#'),       
    'dc'  : "http://purl.org/dc/elements/1.1/",
}

def generateQName(graph,uri):
    prefix,uri,localName = graph.compute_qname(classOrIdentifier(uri)) 
    return u':'.join([prefix,localName])    

def classOrTerm(thing):
    if isinstance(thing,Class):
        return thing.identifier
    else:
        assert isinstance(thing,(URIRef,BNode,Literal))
        return thing

def classOrIdentifier(thing):
    if isinstance(thing,(Property,Class)):
        return thing.identifier
    else:
        assert isinstance(thing,(URIRef,BNode)),"Expecting a Class, Property, URIRef, or BNode.. not a %s"%thing
        return thing

def propertyOrIdentifier(thing):
    if isinstance(thing,Property):
        return thing.identifier
    else:
        assert isinstance(thing,URIRef)
        return thing

def manchesterSyntax(thing,store,boolean=None,transientList=False):
    """
    Core serialization
    """
    assert thing is not None
    if boolean:
        if transientList:
            liveChildren=iter(thing)
            children = [manchesterSyntax(child,store) for child in thing ]
        else:
            liveChildren=iter(Collection(store,thing))
            children = [manchesterSyntax(child,store) for child in Collection(store,thing)]
        if boolean == OWL_NS.intersectionOf:
            childList=[]
            named = []
            for child in liveChildren:
                if isinstance(child,URIRef):
                    named.append(child)
                else:
                    childList.append(child)
            if named:
                def castToQName(x):
                    prefix,uri,localName = store.compute_qname(x) 
                    return u':'.join([prefix,localName])
                
                if len(named) > 1:
                    prefix = '( '+ ' and '.join(map(castToQName,named)) + ' )'                
                else:
                    prefix = manchesterSyntax(named[0],store)
                if childList:
                    return prefix+ ' that '+' and '.join(
                             map(lambda x:manchesterSyntax(x,store),childList))
                else:
                    return prefix
            else:
                return '( '+ ' and '.join(children) + ' )'
        elif boolean == OWL_NS.unionOf:
            return '( '+ ' or '.join(children) + ' )'
        elif boolean == OWL_NS.oneOf:
            return '{ '+ ' '.join(children) +' }'
        else:            
            assert boolean == OWL_NS.complementOf
    elif OWL_NS.Restriction in store.objects(subject=thing, predicate=RDF.type):
        prop = list(store.objects(subject=thing, predicate=OWL_NS.onProperty))[0]
        prefix,uri,localName = store.compute_qname(prop)
        propString = u':'.join([prefix,localName])
        for onlyClass in store.objects(subject=thing, predicate=OWL_NS.allValuesFrom):
            return '( %s only %s )'%(propString,manchesterSyntax(onlyClass,store))
        for val in store.objects(subject=thing, predicate=OWL_NS.hasValue):
            return '( %s value %s )'%(propString,manchesterSyntax(val,store))        
        for someClass in store.objects(subject=thing, predicate=OWL_NS.someValuesFrom):    
            return '( %s some %s )'%(propString,manchesterSyntax(someClass,store))
        cardLookup = {OWL_NS.maxCardinality:'max',OWL_NS.minCardinality:'min',OWL_NS.cardinality:'equals'}
        for s,p,o in store.triples_choices((thing,cardLookup.keys(),None)):            
            return '( %s %s %s )'%(propString,cardLookup[p],o.encode('utf-8'))
    compl = list(store.objects(subject=thing, predicate=OWL_NS.complementOf)) 
    if compl:
        return '( not %s )'%(manchesterSyntax(compl[0],store))
    else:
        for boolProp,col in store.query("SELECT ?p ?bool WHERE { ?class a owl:Class; ?p ?bool . ?bool rdf:first ?foo }",
                                         processor="sparql2sql",
                                         initBindings={Variable("?class"):thing},
                                         initNs=nsBinds):
            if not isinstance(thing,URIRef):                
                return manchesterSyntax(col,store,boolean=boolProp)
        try:
            prefix,uri,localName = store.compute_qname(thing) 
            qname = u':'.join([prefix,localName])
        except Exception,e:
            if isinstance(thing,BNode):
                return thing.n3()
            return "<"+thing+">"
            print list(store.objects(subject=thing,predicate=RDF.type))
            raise
            return '[]'#+thing._id.encode('utf-8')+'</em>'            
        if (thing,RDF.type,OWL_NS.Class) not in store:
            return qname.encode('utf-8')
        else:
            return qname.encode('utf-8')

def GetIdentifiedClasses(graph):
    for c in graph.subjects(predicate=RDF.type,object=OWL_NS.Class):
        if isinstance(c,URIRef):
            yield Class(c)

def termDeletionDecorator(prop):
    def someFunc(func):
        func.property = prop
        return func
    return someFunc

class TermDeletionHelper:
    def __init__(self, prop):
        self.prop = prop
    def __call__(self, f):
        def _remover(inst):
            inst.graph.remove((inst.identifier,self.prop,None))
        return _remover

class Individual(object):
    """
    A typed individual
    """
    factoryGraph = Graph()
    def serialize(self,graph):
        for fact in self.factoryGraph.triples((self.identifier,None,None)):
            graph.add(fact)
    def __init__(self, identifier=None,graph=None):
        self.__identifier = identifier is not None and identifier or BNode()
        if graph is None:
            self.graph = self.factoryGraph
        else:
            self.graph = graph    
        self.qname = None
        if not isinstance(self.identifier,BNode):
            try:
                prefix,uri,localName = self.graph.compute_qname(self.identifier) 
                self.qname = u':'.join([prefix,localName])
            except:
                pass
    
    def clearInDegree(self):
        self.graph.remove((None,None,self.identifier))    

    def clearOutDegree(self):
        self.graph.remove((self.identifier,None,None))    

    def delete(self):
        self.clearInDegree()
        self.clearOutDegree()
        
    def replace(self,other):
        for s,p,o in self.graph.triples((None,None,self.identifier)):
            self.graph.add((s,p,classOrIdentifier(other)))
        self.delete()
    
    def _get_type(self):
        for _t in self.graph.objects(subject=self.identifier,predicate=RDF.type):
            yield _t
    def _set_type(self, kind):
        if not kind:
            return  
        if isinstance(kind,(Individual,Identifier)):
            self.graph.add((self.identifier,RDF.type,classOrIdentifier(kind)))
        else:
            for c in kind:
                assert isinstance(c,(Individual,Identifier))
                self.graph.add((self.identifier,RDF.type,classOrIdentifier(c)))
                
    @TermDeletionHelper(RDF.type)            
    def _delete_type(self):
        """
        >>> g = Graph()
        >>> b=Individual(OWL_NS.Restriction,g)
        >>> b.type = RDF.Resource
        >>> len(list(b.type))
        1
        >>> del b.type
        >>> len(list(b.type))
        0
        """
        pass
                
    type = property(_get_type, _set_type, _delete_type)

    def _get_identifier(self):
        return self.__identifier
    def _set_identifier(self, i):
        assert i
        if i != self.__identifier:
            oldStmtsOut = [(p,o) for s,p,o in self.graph.triples((self.__identifier,None,None))]
            oldStmtsIn  = [(s,p) for s,p,o in self.graph.triples((None,None,self.__identifier))]
            for p1,o1 in oldStmtsOut:                
                self.graph.remove((self.__identifier,p1,o1))
            for s1,p1 in oldStmtsIn:                
                self.graph.remove((s1,p1,self.__identifier))
            self.__identifier = i
            self.graph.addN([(i,p1,o1,self.graph) for p1,o1 in oldStmtsOut])
            self.graph.addN([(s1,p1,i,self.graph) for s1,p1 in oldStmtsIn])
        if not isinstance(i,BNode):
            try:
                prefix,uri,localName = self.graph.compute_qname(i) 
                self.qname = u':'.join([prefix,localName])
            except:
                pass
            
    identifier = property(_get_identifier, _set_identifier)
    
    def _get_sameAs(self):
        for _t in self.graph.objects(subject=self.identifier,predicate=OWL_NS.sameAs):
            yield _t
    def _set_sameAs(self, term):
        if not kind:
            return  
        if isinstance(term,(Individual,Identifier)):
            self.graph.add((self.identifier,OWL_NS.sameAs,classOrIdentifier(term)))
        else:
            for c in term:
                assert isinstance(c,(Individual,Identifier))
                self.graph.add((self.identifier,OWL_NS.sameAs,classOrIdentifier(c)))
                
    @TermDeletionHelper(OWL_NS.sameAs)            
    def _delete_sameAs(self):
        pass
                
    sameAs = property(_get_sameAs, _set_sameAs, _delete_sameAs)
    

class AnnotatableTerms(Individual):
    """
    Terms in an OWL ontology with rdfs:label and rdfs:comment
    """
    def __init__(self,identifier,graph=None):
        super(AnnotatableTerms, self).__init__(identifier,graph)
    def _get_comment(self):
        for comment in self.graph.objects(subject=self.identifier,predicate=RDFS.comment):
            yield comment
    def _set_comment(self, comment):
        if not comment:
            return        
        if isinstance(comment,Identifier):
            self.graph.add((self.identifier,RDFS.comment,comment))
        else:
            for c in comment:
                self.graph.add((self.identifier,RDFS.comment,c))
                
    @TermDeletionHelper(RDFS.comment)
    def _del_comment(self):
        pass
    
    comment = property(_get_comment, _set_comment, _del_comment)

    def _get_seeAlso(self):
        for sA in self.graph.objects(subject=self.identifier,predicate=RDFS.seeAlso):
            yield sA
    def _set_seeAlso(self, seeAlsos):
        if not seeAlsos:
            return        
        for s in seeAlsos:
            self.graph.add((self.identifier,RDFS.seeAlso,s))
            
    @TermDeletionHelper(RDFS.seeAlso)
    def _del_seeAlso(self):
        pass
    seeAlso = property(_get_seeAlso, _set_seeAlso, _del_seeAlso)

    def _get_label(self):
        for label in self.graph.objects(subject=self.identifier,predicate=RDFS.label):
            yield label
    def _set_label(self, label):
        if not label:
            return        
        if isinstance(label,Identifier):
            self.graph.add((self.identifier,RDFS.label,label))
        else:
            for l in label:
                self.graph.add((self.identifier,RDFS.label,l))
                
    @TermDeletionHelper(RDFS.label)
    def _delete_label(self):
        """
        >>> g=Graph()
        >>> b=Individual(OWL_NS.Restriction,g)
        >>> b.label = Literal('boo')
        >>> len(list(b.label))
        1
        >>> del b.label
        >>> len(list(b.label))
        0
        """
        pass
        
    label = property(_get_label, _set_label, _delete_label)

class Ontology(AnnotatableTerms):
    """ The owl ontology metadata"""
    def __init__(self, identifier=None,imports=None,comment=None,graph=None):
        super(Ontology, self).__init__(identifier,graph)
        self.imports = imports and imports or []
        self.comment = comment and comment or []
        if (self.identifier,RDF.type,OWL_NS.Ontology) not in self.graph:
            self.graph.add((self.identifier,RDF.type,OWL_NS.Ontology))

    def setVersion(self,version):
        self.graph.set((self.identifier,OWL_NS.versionInfo,version))

    def _get_imports(self):
        for owl in self.graph.objects(subject=self.identifier,predicate=OWL_NS['imports']):
            yield owl
    def _set_imports(self, other):
        if not other:
            return        
        for o in other:
            self.graph.add((self.identifier,OWL_NS['imports'],o))
            
    @TermDeletionHelper(OWL_NS['imports'])
    def _del_imports(self):            
        pass
    
    imports = property(_get_imports, _set_imports, _del_imports)

def AllClasses(graph):
    prevClasses=set()
    for c in graph.subjects(predicate=RDF.type,object=OWL_NS.Class):
        if c not in prevClasses:
            prevClasses.add(c)
            yield Class(c)            

def AllProperties(graph):
    prevProps=set()
    for s,p,o in graph.triples_choices(
               (None,RDF.type,[OWL_NS.Symmetric,
                               OWL_NS.FunctionalProperty,
                               OWL_NS.InverseFunctionalProperty,
                               OWL_NS.TransitiveProperty,
                               OWL_NS.DatatypeProperty,
                               OWL_NS.ObjectProperty])):
        if o in [OWL_NS.Symmetric,
                 OWL_NS.InverseFunctionalProperty,
                 OWL_NS.TransitiveProperty,
                 OWL_NS.ObjectProperty]:
            bType=OWL_NS.ObjectProperty
        else:
            bType=OWL_NS.DatatypeProperty
        if s not in prevProps:
            prevProps.add(s)
            yield Property(s,
                           graph=graph,
                           baseType=bType)            
    
class ClassNamespaceFactory(Namespace):
    def term(self, name):
        return Class(URIRef(self + name))

    def __getitem__(self, key, default=None):
        return self.term(key)

    def __getattr__(self, name):
        if name.startswith("__"): # ignore any special Python names!
            raise AttributeError
        else:
            return self.term(name)    
    
def CastClass(c,graph=None):
    graph = graph is None and c.factoryGraph or graph
    for kind in graph.objects(subject=classOrIdentifier(c),
                              predicate=RDF.type):
        if kind == OWL_NS.Restriction:
            prop = list(graph.objects(subject=classOrIdentifier(c),
                                     predicate=OWL_NS.onProperty))[0]
            return Restriction(prop, graph,identifier=classOrIdentifier(c))
        else:
            for s,p,o in graph.triples_choices((classOrIdentifier(c),
                                                [OWL_NS.intersectionOf,
                                                 OWL_NS.unionOf,
                                                 OWL_NS.oneOf],
                                                None)):
                if p == OWL_NS.oneOf:
                    return EnumeratedClass(classOrIdentifier(c),graph=graph)
                else:
                    return BooleanClass(classOrIdentifier(c),operator=p,graph=graph)
            #assert (classOrIdentifier(c),RDF.type,OWL_NS.Class) in graph
            return Class(classOrIdentifier(c),graph=graph,skipOWLClassMembership=True)
    
class Class(AnnotatableTerms):
    """
    'General form' for classes:
    
    The Manchester Syntax (supported in Protege) is used as the basis for the form 
    of this class
    
    See: http://owl-workshop.man.ac.uk/acceptedLong/submission_9.pdf:
    
    [Annotation]
    ‘Class:’ classID {Annotation
                        ( (‘SubClassOf:’ ClassExpression)
                        | (‘EquivalentTo’ ClassExpression)
                        | (’DisjointWith’ ClassExpression)) }

    Appropriate excerpts from OWL Reference:
    
    ".. Subclass axioms provide us with partial definitions: they represent 
     necessary but not sufficient conditions for establishing class 
     membership of an individual."
     
   ".. A class axiom may contain (multiple) owl:equivalentClass statements"   
                  
    "..A class axiom may also contain (multiple) owl:disjointWith statements.."
    
    "..An owl:complementOf property links a class to precisely one class 
      description."
      
    """
    def _serialize(self,graph):
        for cl in self.subClassOf:
            CastClass(cl,self.graph).serialize(graph)
        for cl in self.equivalentClass:
            CastClass(cl,self.graph).serialize(graph)
        for cl in self.disjointWith:
            CastClass(cl,self.graph).serialize(graph)
        if self.complementOf:
            CastClass(self.complementOf,self.graph).serialize(graph)
        
    def serialize(self,graph):
        for fact in self.graph.triples((self.identifier,None,None)):
            graph.add(fact)
        self._serialize(graph)
    
    def __init__(self, identifier=None,subClassOf=None,equivalentClass=None,
                       disjointWith=None,complementOf=None,graph=None,
                       skipOWLClassMembership = False,comment=None):
        super(Class, self).__init__(identifier,graph)
        if not skipOWLClassMembership and (self.identifier,RDF.type,OWL_NS.Class) not in self.graph and \
           (self.identifier,RDF.type,OWL_NS.Restriction) not in self.graph:
            self.graph.add((self.identifier,RDF.type,OWL_NS.Class))
        
        self.subClassOf      = subClassOf and subClassOf or [] 
        self.equivalentClass = equivalentClass and equivalentClass or []
        self.disjointWith    = disjointWith  and disjointWith or []
        if complementOf:
            self.complementOf    = complementOf
        self.comment = comment and comment or []
        
    def _get_extent(self,graph=None):
        for member in (graph is None and self.graph or graph).subjects(predicate=RDF.type,
                                          object=self.identifier):
            yield member
    def _set_extent(self,other):
        if not other:
            return
        for m in other:
            self.graph.add((classOrIdentifier(m),RDF.type,self.identifier))
            
    @TermDeletionHelper(RDF.type)
    def _del_type(self):            
        pass            
            
    extent = property(_get_extent, _set_extent, _del_type)            

    def _get_annotation(self,term=RDFS.label):
        for annotation in self.graph.objects(subject=self,predicate=term):
            yield annotation
            
    annotation = property(_get_annotation,lambda x:x)            

    def _get_extentQuery(self):
        return (Variable('CLASS'),RDF.type,self.identifier)

    def _set_extentQuery(self,other): pass
            
    extentQuery = property(_get_extentQuery, _set_extentQuery)            
    
    def __hash__(self):
        """
        >>> b=Class(OWL_NS.Restriction)
        >>> c=Class(OWL_NS.Restriction)
        >>> len(set([b,c]))
        1
        """
        return hash(self.identifier)

    def __eq__(self, other):
        assert isinstance(other,Class)
        return self.identifier == other.identifier
    
    def __iadd__(self, other):
        assert isinstance(other,Class)
        other.subClassOf = [self]
        return self

    def __isub__(self, other):
        assert isinstance(other,Class)
        self.graph.remove((classOrIdentifier(other),RDFS.subClassOf,self.identifier))
        return self
    
    def __invert__(self):
        """
        Shorthand for Manchester syntax's not operator
        """
        return Class(complementOf=self)

    def __or__(self,other):
        """
        Construct an anonymous class description consisting of the union of this class and '
        other' and return it
        """
        return BooleanClass(operator=OWL_NS.unionOf,members=[self,other],graph=self.graph)

    def __and__(self,other):
        """
        Construct an anonymous class description consisting of the intersection of this class and '
        other' and return it
        
        >>> exNs = Namespace('http://example.com/')        
        >>> namespace_manager = NamespaceManager(Graph())
        >>> namespace_manager.bind('ex', exNs, override=False)
        >>> namespace_manager.bind('owl', OWL_NS, override=False)
        >>> g = Graph()    
        >>> g.namespace_manager = namespace_manager
        
        Chaining 3 intersections
                
        >>> female      = Class(exNs.Female,graph=g)
        >>> male        = Class(exNs.Human,graph=g)
        >>> youngPerson = Class(exNs.YoungPerson,graph=g)
        >>> youngWoman = female & male & youngPerson
        >>> youngWoman # doctest:+ELLIPSIS
        ex:YoungPerson that _:...
        >>> isinstance(youngWoman, BooleanClass)
        True
        >>> isinstance(youngWoman.identifier, BNode)
        True
        """
        return BooleanClass(operator=OWL_NS.intersectionOf,members=[self,other],graph=self.graph)
            
    def _get_subClassOf(self):
        for anc in self.graph.objects(subject=self.identifier,predicate=RDFS.subClassOf):
            yield Class(anc,
                        graph=self.graph,
                        skipOWLClassMembership=True)
    def _set_subClassOf(self, other):
        if not other:
            return        
        for sc in other:
            self.graph.add((self.identifier,RDFS.subClassOf,classOrIdentifier(sc)))
            
    @TermDeletionHelper(RDFS.subClassOf)
    def _del_subClassOf(self):            
        pass            
            
    subClassOf = property(_get_subClassOf, _set_subClassOf, _del_subClassOf)

    def _get_equivalentClass(self):
        for ec in self.graph.objects(subject=self.identifier,predicate=OWL_NS.equivalentClass):
            yield Class(ec,graph=self.graph)
    def _set_equivalentClass(self, other):
        if not other:
            return
        for sc in other:
            self.graph.add((self.identifier,OWL_NS.equivalentClass,classOrIdentifier(sc)))
            
    @TermDeletionHelper(OWL_NS.equivalentClass)
    def _del_equivalentClass(self):            
        pass                        
            
    equivalentClass = property(_get_equivalentClass, _set_equivalentClass, _del_equivalentClass)

    def _get_disjointWith(self):
        for dc in self.graph.objects(subject=self.identifier,predicate=OWL_NS.disjointWith):
            yield Class(dc,graph=self.graph)
    def _set_disjointWith(self, other):
        if not other:
            return
        for c in other:
            self.graph.add((self.identifier,OWL_NS.disjointWith,classOrIdentifier(c)))
            
    @TermDeletionHelper(OWL_NS.disjointWith)
    def _del_disjointWith(self):            
        pass            
                        
    disjointWith = property(_get_disjointWith, _set_disjointWith, _del_disjointWith)

    def _get_complementOf(self):
        comp = list(self.graph.objects(subject=self.identifier,predicate=OWL_NS.complementOf))
        if not comp:
            return None
        elif len(comp) == 1:
            return Class(comp[0],graph=self.graph)
        else:
            raise Exception(len(comp))
        
    def _set_complementOf(self, other):
        if not other:
            return
        self.graph.add((self.identifier,OWL_NS.complementOf,classOrIdentifier(other)))
        
    @TermDeletionHelper(OWL_NS.complementOf)
    def _del_complementOf(self):            
        pass            
                
    complementOf = property(_get_complementOf, _set_complementOf, _del_complementOf)
    
    def isPrimitive(self):
        if (self.identifier,RDF.type,OWL_NS.Restriction) in self.graph:
            return False
        sc = list(self.subClassOf)
        ec = list(self.equivalentClass)
        for boolClass,p,rdfList in self.graph.triples_choices((self.identifier,
                                                               [OWL_NS.intersectionOf,
                                                                OWL_NS.unionOf],
                                                                None)):
            ec.append(manchesterSyntax(rdfList,self.graph,boolean=p))
        for e in ec:
            return False
        if self.complementOf:
            return False
        return True
    
    def subSumpteeIds(self):
        for s in self.graph.subjects(predicate=RDFS.subClassOf,object=self.identifier):
            yield s
    
    def __repr__(self,full=False,normalization=True):
        """
        Returns the Manchester Syntax equivalent for this class
        """
        exprs = []
        sc = list(self.subClassOf)
        ec = list(self.equivalentClass)
        for boolClass,p,rdfList in self.graph.triples_choices((self.identifier,
                                                               [OWL_NS.intersectionOf,
                                                                OWL_NS.unionOf],
                                                                None)):
            ec.append(manchesterSyntax(rdfList,self.graph,boolean=p))
        dc = list(self.disjointWith)
        c  = self.complementOf
        if c:
            dc.append(c)
        klassKind = ''
        label = list(self.graph.objects(self.identifier,RDFS.label))
        label = label and '('+label[0]+')' or ''
        if sc:
            if full:
                scJoin = '\n                '
            else:
                scJoin = ', '
            necStatements = [
              isinstance(s,Class) and isinstance(self.identifier,BNode) and
                                      repr(CastClass(s,self.graph)) or
                                      #repr(BooleanClass(classOrIdentifier(s),
                                      #                  operator=None,
                                      #                  graph=self.graph)) or 
              manchesterSyntax(classOrIdentifier(s),self.graph) for s in sc]
            if necStatements:
                klassKind = "Primitive Type %s"%label
            exprs.append("SubClassOf: %s"%scJoin.join(necStatements))
            if full:
                exprs[-1]="\n    "+exprs[-1]
        if ec:
            nec_SuffStatements = [    
              isinstance(s,basestring) and s or 
              manchesterSyntax(classOrIdentifier(s),self.graph) for s in ec]
            if nec_SuffStatements:
                klassKind = "A Defined Class %s"%label
            exprs.append("EquivalentTo: %s"%', '.join(nec_SuffStatements))
            if full:
                exprs[-1]="\n    "+exprs[-1]
        if dc:
            exprs.append("DisjointWith %s\n"%'\n                 '.join([
              manchesterSyntax(classOrIdentifier(s),self.graph) for s in dc]))
            if full:
                exprs[-1]="\n    "+exprs[-1]
        descr = list(self.graph.objects(self.identifier,RDFS.comment))
        if full and normalization:
            klassDescr = klassKind and '\n    ## %s ##'%klassKind +\
            (descr and "\n    %s"%descr[0] or '') + ' . '.join(exprs) or ' . '.join(exprs)
        else:
            klassDescr = full and (descr and "\n    %s"%descr[0] or '') or '' + ' . '.join(exprs)
        return (isinstance(self.identifier,BNode) and "Some Class " or "Class: %s "%self.qname)+klassDescr

class OWLRDFListProxy(object):
    def __init__(self,rdfList,members=None):
        members = members and members or []
        if rdfList:
            self._rdfList = Collection(self.graph,rdfList[0])
            for member in members:
                if member not in self._rdfList:
                    self._rdfList.append(classOrIdentifier(member))
        else:
            self._rdfList = Collection(self.graph,BNode(),
                                       [classOrIdentifier(m) for m in members])
            self.graph.add((self.identifier,self._operator,self._rdfList.uri)) 

    #Redirect python list accessors to the underlying Collection instance
    def __len__(self):
        return len(self._rdfList)

    def index(self, item):
        return self._rdfList.index(classOrIdentifier(item))
    
    def __getitem__(self, key):
        return self._rdfList[key]

    def __setitem__(self, key, value):
        self._rdfList[key] = classOrIdentifier(value)
        
    def __delitem__(self, key):
        del self._rdfList[key]    
        
    def clear(self):
        self._rdfList.clear()    

    def __iter__(self):
        for item in self._rdfList:
            yield item

    def __contains__(self, item):
        for i in self._rdfList:
            if i == classOrIdentifier(item):
                return 1
        return 0
    
    def append(self, item):
        self._rdfList.append(item)    

    def __iadd__(self, other):
        self._rdfList.append(classOrIdentifier(other))

class EnumeratedClass(Class,OWLRDFListProxy):
    """
    Class for owl:oneOf forms:
    
    OWL Abstract Syntax is used
    
    axiom ::= 'EnumeratedClass(' classID ['Deprecated'] { annotation } { individualID } ')'
    

    >>> exNs = Namespace('http://example.com/')        
    >>> namespace_manager = NamespaceManager(Graph())
    >>> namespace_manager.bind('ex', exNs, override=False)
    >>> namespace_manager.bind('owl', OWL_NS, override=False)
    >>> g = Graph()    
    >>> g.namespace_manager = namespace_manager
    >>> Individual.factoryGraph = g
    >>> ogbujiBros = EnumeratedClass(exNs.ogbujicBros,
    ...                              members=[exNs.chime,
    ...                                       exNs.uche,
    ...                                       exNs.ejike])
    >>> ogbujiBros
    { ex:chime ex:uche ex:ejike }
    >>> print g.serialize(format='n3')
    @prefix ex: <http://example.com/> .
    @prefix owl: <http://www.w3.org/2002/07/owl#> .
    @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
    <BLANKLINE>
    ex:ogbujicBros a owl:Class;
        owl:oneOf ( ex:chime ex:uche ex:ejike ) .
    <BLANKLINE>
    <BLANKLINE>     
    """
    _operator = OWL_NS.oneOf
    def isPrimitive(self):
        return False
    def __init__(self, identifier=None,members=None,graph=None):
        Class.__init__(self,identifier,graph = graph)
        members = members and members or []
        rdfList = list(self.graph.objects(predicate=OWL_NS.oneOf,subject=self.identifier))
        OWLRDFListProxy.__init__(self, rdfList, members)
    def __repr__(self):
        """
        Returns the Manchester Syntax equivalent for this class
        """
        return manchesterSyntax(self._rdfList.uri,self.graph,boolean=self._operator)        
    
    def serialize(self,graph):
        clonedList = Collection(graph,BNode())
        for cl in self._rdfList:
            clonedList.append(cl)
            CastClass(cl, self.graph).serialize(graph)
        
        graph.add((self.identifier,self._operator,clonedList.uri))
        for s,p,o in self.graph.triples((self.identifier,None,None)):
            if p != self._operator:
                graph.add((s,p,o))
        self._serialize(graph)
    
BooleanPredicates = [OWL_NS.intersectionOf,OWL_NS.unionOf]

class BooleanClassExtentHelper:
    """
    >>> testGraph = Graph()
    >>> Individual.factoryGraph = testGraph
    >>> EX = Namespace("http://example.com/")
    >>> namespace_manager = NamespaceManager(Graph())
    >>> namespace_manager.bind('ex', EX, override=False)
    >>> testGraph.namespace_manager = namespace_manager
    >>> fire  = Class(EX.Fire)
    >>> water = Class(EX.Water) 
    >>> testClass = BooleanClass(members=[fire,water])
    >>> testClass2 = BooleanClass(operator=OWL_NS.unionOf,members=[fire,water])
    >>> for c in BooleanClass.getIntersections():
    ...     print c
    ( ex:Fire and ex:Water )
    >>> for c in BooleanClass.getUnions():
    ...     print c
    ( ex:Fire or ex:Water )
    """    
    def __init__(self, operator):
        self.operator = operator
    def __call__(self, f):
        def _getExtent():
            for c in Individual.factoryGraph.subjects(self.operator):
                yield BooleanClass(c,operator=self.operator)            
        return _getExtent
    
class Callable:
    def __init__(self, anycallable):
        self.__call__ = anycallable    

class BooleanClass(Class,OWLRDFListProxy):
    """
    See: http://www.w3.org/TR/owl-ref/#Boolean
    
    owl:complementOf is an attribute of Class, however
    
    """
    @BooleanClassExtentHelper(OWL_NS.intersectionOf)
    @Callable
    def getIntersections(): pass
    getIntersections = Callable(getIntersections)    

    @BooleanClassExtentHelper(OWL_NS.unionOf)
    @Callable
    def getUnions(): pass
    getUnions = Callable(getUnions)    
            
    def __init__(self,identifier=None,operator=OWL_NS.intersectionOf,
                 members=None,graph=None):
        if operator is None:
            props=[]
            for s,p,o in graph.triples_choices((identifier,
                                                [OWL_NS.intersectionOf,
                                                 OWL_NS.unionOf],
                                                 None)):
                props.append(p)
                operator = p
            assert len(props)==1,repr(props)
        Class.__init__(self,identifier,graph = graph)
        assert operator in [OWL_NS.intersectionOf,OWL_NS.unionOf], str(operator)
        self._operator = operator
        rdfList = list(self.graph.objects(predicate=operator,subject=self.identifier))
        assert not members or not rdfList,"This is a previous boolean class description!"+repr(Collection(self.graph,rdfList[0]).n3())        
        OWLRDFListProxy.__init__(self, rdfList, members)

    def serialize(self,graph):
        clonedList = Collection(graph,BNode())
        for cl in self._rdfList:
            clonedList.append(cl)
            CastClass(cl, self.graph).serialize(graph)
        
        graph.add((self.identifier,self._operator,clonedList.uri))
        
        for s,p,o in self.graph.triples((self.identifier,None,None)):
            if p != self._operator:
                graph.add((s,p,o))
        self._serialize(graph)

    def isPrimitive(self):
        return False

    def changeOperator(self,newOperator):
        """
        Converts a unionOf / intersectionOf class expression into one 
        that instead uses the given operator
        
        
        >>> testGraph = Graph()
        >>> Individual.factoryGraph = testGraph
        >>> EX = Namespace("http://example.com/")
        >>> namespace_manager = NamespaceManager(Graph())
        >>> namespace_manager.bind('ex', EX, override=False)
        >>> testGraph.namespace_manager = namespace_manager
        >>> fire  = Class(EX.Fire)
        >>> water = Class(EX.Water) 
        >>> testClass = BooleanClass(members=[fire,water])
        >>> testClass
        ( ex:Fire and ex:Water )
        >>> testClass.changeOperator(OWL_NS.unionOf)
        >>> testClass
        ( ex:Fire or ex:Water )
        >>> try: testClass.changeOperator(OWL_NS.unionOf)
        ... except Exception, e: print e
        The new operator is already being used!
        
        """
        assert newOperator != self._operator,"The new operator is already being used!"
        self.graph.remove((self.identifier,self._operator,self._rdfList.uri))
        self.graph.add((self.identifier,newOperator,self._rdfList.uri))
        self._operator = newOperator

    def __repr__(self):
        """
        Returns the Manchester Syntax equivalent for this class
        """
        return manchesterSyntax(self._rdfList.uri,self.graph,boolean=self._operator)

    def __or__(self,other):
        """
        Adds other to the list and returns self
        """
        assert self._operator == OWL_NS.unionOf
        self._rdfList.append(classOrIdentifier(other))
        return self

def AllDifferent(members):
    """
    DisjointClasses(' description description { description } ')'
    
    """
    pass

class Restriction(Class):
    """
    restriction ::= 'restriction(' datavaluedPropertyID dataRestrictionComponent 
                                 { dataRestrictionComponent } ')'
                  | 'restriction(' individualvaluedPropertyID 
                      individualRestrictionComponent 
                      { individualRestrictionComponent } ')'    
    """
    
    restrictionKinds = [OWL_NS.allValuesFrom,
                        OWL_NS.someValuesFrom,
                        OWL_NS.hasValue,
                        OWL_NS.maxCardinality,
                        OWL_NS.minCardinality]
    
    def __init__(self,
                 onProperty,
                 graph = Graph(),
                 allValuesFrom=None,
                 someValuesFrom=None,
                 value=None,
                 cardinality=None,
                 maxCardinality=None,
                 minCardinality=None,
                 identifier=None):
        super(Restriction, self).__init__(identifier,
                                          graph=graph,
                                          skipOWLClassMembership=True)
        if (self.identifier,
            OWL_NS.onProperty,
            propertyOrIdentifier(onProperty)) not in graph:
            graph.add((self.identifier,OWL_NS.onProperty,propertyOrIdentifier(onProperty)))
        self.onProperty = onProperty
        restrTypes = [
                      (allValuesFrom,OWL_NS.allValuesFrom ),
                      (someValuesFrom,OWL_NS.someValuesFrom),
                      (value,OWL_NS.hasValue),
                      (cardinality,OWL_NS.cardinality),
                      (maxCardinality,OWL_NS.maxCardinality),
                      (minCardinality,OWL_NS.minCardinality)]
        validRestrProps = [(i,oTerm) for (i,oTerm) in restrTypes if i] 
        assert len(validRestrProps) < 2
        self.restrictionRange = validRestrProps
        for val,oTerm in validRestrProps:
            self.graph.add((self.identifier,oTerm,classOrTerm(val)))   
        if (self.identifier,RDF.type,OWL_NS.Restriction) not in self.graph:
            self.graph.add((self.identifier,RDF.type,OWL_NS.Restriction))
            self.graph.remove((self.identifier,RDF.type,OWL_NS.Class))

    def serialize(self,graph):
        Property(self.onProperty,graph=self.graph).serialize(graph)
        for s,p,o in self.graph.triples((self.identifier,None,None)):
            graph.add((s,p,o))
            if p in [OWL_NS.allValuesFrom,OWL_NS.someValuesFrom]:
                CastClass(o, self.graph).serialize(graph)

    def isPrimitive(self):
        return False

    def __eq__(self, other):
        """
        Equivalence of restrictions is determined by equivalence of the property 
        in question and the restriction 'range'
        """
        assert isinstance(other,Class),repr(other)+repr(type(other))
        if isinstance(other,Restriction):
            return other.onProperty == self.onProperty and \
                   other.restrictionRange == self.restrictionRange
        else:
            return False

    def _get_onProperty(self):
        return list(self.graph.objects(subject=self.identifier,predicate=OWL_NS.onProperty))[0]
    def _set_onProperty(self, prop):
        triple = (self.identifier,OWL_NS.onProperty,propertyOrIdentifier(prop))
        if not prop:
            return
        elif triple in self.graph:
            return
        else:
            self.graph.set(triple)
            
    @TermDeletionHelper(OWL_NS.onProperty)
    def _del_onProperty(self):            
        pass            
                        
    onProperty = property(_get_onProperty, _set_onProperty, _del_onProperty)

    def _get_allValuesFrom(self):
        for i in self.graph.objects(subject=self.identifier,predicate=OWL_NS.allValuesFrom):
            return Class(i,graph=self.graph)
        return None
    def _set_allValuesFrom(self, other):
        triple = (self.identifier,OWL_NS.allValuesFrom,classOrIdentifier(other))
        if not other:
            return
        elif triple in self.graph:
            return
        else:
            self.graph.set(triple)
            
    @TermDeletionHelper(OWL_NS.allValuesFrom)
    def _del_allValuesFrom(self):            
        pass            
                        
    allValuesFrom = property(_get_allValuesFrom, _set_allValuesFrom, _del_allValuesFrom)

    def _get_someValuesFrom(self):
        for i in self.graph.objects(subject=self.identifier,predicate=OWL_NS.someValuesFrom):
            return Class(i,graph=self.graph)
        return None
    def _set_someValuesFrom(self, other):
        triple = (self.identifier,OWL_NS.someValuesFrom,classOrIdentifier(other))
        if not other:
            return
        elif triple in self.graph:
            return
        else:
            self.graph.set(triple)
            
    @TermDeletionHelper(OWL_NS.someValuesFrom)
    def _del_someValuesFrom(self):            
        pass            
                        
    someValuesFrom = property(_get_someValuesFrom, _set_someValuesFrom, _del_someValuesFrom)

    def _get_hasValue(self):
        for i in self.graph.objects(subject=self.identifier,predicate=OWL_NS.hasValue):
            return Class(i,graph=self.graph)
        return None
    def _set_hasValue(self, other):
        triple = (self.identifier,OWL_NS.hasValue,classOrIdentifier(other))
        if not other:
            return
        elif triple in self.graph:
            return
        else:
            self.graph.set(triple)
            
    @TermDeletionHelper(OWL_NS.hasValue)
    def _del_hasValue(self):            
        pass            
                        
    hasValue = property(_get_hasValue, _set_hasValue, _del_hasValue)

    def _get_cardinality(self):
        for i in self.graph.objects(subject=self.identifier,predicate=OWL_NS.cardinality):
            return Class(i,graph=self.graph)
        return None
    def _set_cardinality(self, other):
        triple = (self.identifier,OWL_NS.cardinality,classOrIdentifier(other))
        if not other:
            return
        elif triple in self.graph:
            return
        else:
            self.graph.set(triple)
            
    @TermDeletionHelper(OWL_NS.cardinality)
    def _del_cardinality(self):            
        pass            
                        
    cardinality = property(_get_cardinality, _set_cardinality, _del_cardinality)

    def _get_maxCardinality(self):
        for i in self.graph.objects(subject=self.identifier,predicate=OWL_NS.maxCardinality):
            return Class(i,graph=self.graph)
        return None
    def _set_maxCardinality(self, other):
        triple = (self.identifier,OWL_NS.maxCardinality,classOrIdentifier(other))
        if not other:
            return
        elif triple in self.graph:
            return
        else:
            self.graph.set(triple)
            
    @TermDeletionHelper(OWL_NS.maxCardinality)
    def _del_maxCardinality(self):            
        pass            
                        
    maxCardinality = property(_get_maxCardinality, _set_maxCardinality, _del_maxCardinality)

    def _get_minCardinality(self):
        for i in self.graph.objects(subject=self.identifier,predicate=OWL_NS.minCardinality):
            return Class(i,graph=self.graph)
        return None
    def _set_minCardinality(self, other):
        triple = (self.identifier,OWL_NS.minCardinality,classOrIdentifier(other))
        if not other:
            return
        elif triple in self.graph:
            return
        else:
            self.graph.set(triple)
            
    @TermDeletionHelper(OWL_NS.minCardinality)
    def _del_minCardinality(self):            
        pass            
                        
    minCardinality = property(_get_minCardinality, _set_minCardinality, _del_minCardinality)

    def restrictionKind(self):
        for p in self.graph.triple_choices((self.identifier,
                                            self.restrictionKinds,
                                            None)):
            return p.split(OWL_NS)[-1]
        raise
            
    def __repr__(self):
        """
        Returns the Manchester Syntax equivalent for this restriction
        """
        return manchesterSyntax(self.identifier,self.graph)

### Infix Operators ###

some     = Infix(lambda prop,_class: Restriction(prop,graph=_class.graph,someValuesFrom=_class))
only     = Infix(lambda prop,_class: Restriction(prop,graph=_class.graph,allValuesFrom=_class))
max      = Infix(lambda prop,_class: Restriction(prop,graph=prop.graph,maxCardinality=_class))
min      = Infix(lambda prop,_class: Restriction(prop,graph=prop.graph,minCardinality=_class))
exactly  = Infix(lambda prop,_class: Restriction(prop,graph=prop.graph,cardinality=_class))
value    = Infix(lambda prop,_class: Restriction(prop,graph=prop.graph,value=_class))

PropertyAbstractSyntax=\
"""
%s( %s { %s } 
%s
{ 'super(' datavaluedPropertyID ')'} ['Functional']
{ domain( %s ) } { range( %s ) } )"""

class Property(AnnotatableTerms):
    """
    axiom ::= 'DatatypeProperty(' datavaluedPropertyID ['Deprecated'] { annotation } 
                { 'super(' datavaluedPropertyID ')'} ['Functional']
                { 'domain(' description ')' } { 'range(' dataRange ')' } ')'
            | 'ObjectProperty(' individualvaluedPropertyID ['Deprecated'] { annotation } 
                { 'super(' individualvaluedPropertyID ')' }
                [ 'inverseOf(' individualvaluedPropertyID ')' ] [ 'Symmetric' ] 
                [ 'Functional' | 'InverseFunctional' | 'Functional' 'InverseFunctional' |
                  'Transitive' ]
                { 'domain(' description ')' } { 'range(' description ')' } ')    
    """
    def __init__(self,identifier=None,graph = None,baseType=OWL_NS.ObjectProperty,
                      subPropertyOf=None,domain=None,range=None,inverseOf=None,
                      otherType=None,equivalentProperty=None,comment=None):
        super(Property, self).__init__(identifier,graph)
        assert not isinstance(self.identifier,BNode)
        if (self.identifier,RDF.type,baseType) not in self.graph:
            self.graph.add((self.identifier,RDF.type,baseType))
        self._baseType=baseType
        self.subPropertyOf = subPropertyOf
        self.inverseOf     = inverseOf
        self.domain        = domain
        self.range         = range
        self.comment = comment and comment or []

    def serialize(self,graph):
        for fact in self.graph.triples((self.identifier,None,None)):
            graph.add(fact)
        for p in itertools.chain(self.subPropertyOf,
                                 self.inverseOf):
            p.serialize(graph)
        for c in itertools.chain(self.domain,
                                 self.range):
            CastClass(c,self.graph).serialize(graph)

    def _get_extent(self,graph=None):
        for triple in (graph is None and 
                       self.graph or graph).triples((None,self.identifier,None)):
            yield triple
    def _set_extent(self,other):
        if not other:
            return
        for subj,obj in other:
            self.graph.add((subj,self.identifier,obj))
            
    extent = property(_get_extent, _set_extent)            

    def __repr__(self):
        rt=[]
        if OWL_NS.ObjectProperty in self.type:
            rt.append(u'ObjectProperty( %s annotation(%s)'\
                       %(self.qname,first(self.comment) and first(self.comment) or ''))
            if first(self.inverseOf):
                twoLinkInverse=first(first(self.inverseOf).inverseOf)
                if twoLinkInverse and twoLinkInverse.identifier == self.identifier:
                    inverseRepr=first(self.inverseOf).qname
                else:
                    inverseRepr=repr(first(self.inverseOf))
                rt.append(u"  inverseOf( %s )%s"%(inverseRepr,
                            OWL_NS.Symmetric in self.type and u' Symmetric' or u''))
            for s,p,roleType in self.graph.triples_choices((self.identifier,
                                                            RDF.type,
                                                            [OWL_NS.Functional,
                                                             OWL_NS.InverseFunctionalProperty,
                                                             OWL_NS.Transitive])):
                rt.append(unicode(roleType.split(OWL_NS)[-1]))
        else:
            rt.append('DatatypeProperty( %s %s'\
                       %(self.qname,first(self.comment) and first(self.comment) or ''))            
            for s,p,roleType in self.graph.triples((self.identifier,
                                                    RDF.type,
                                                    OWL_NS.Functional)):
                rt.append(u'   Functional')
        def canonicalName(term,g):
            normalizedName=classOrIdentifier(term)
            if isinstance(normalizedName,BNode):
                return term
            elif normalizedName.startswith(_XSD_NS):
                return unicode(term)
            elif first(g.triples_choices((
                      normalizedName,
                      [OWL_NS.unionOf,
                       OWL_NS.intersectionOf],None))):
                return repr(term)
            else:
                return unicode(term.qname)
        rt.append(u' '.join([u"   super( %s )"%canonicalName(superP,self.graph) 
                              for superP in self.subPropertyOf]))                        
        rt.append(u' '.join([u"   domain( %s )"% canonicalName(domain,self.graph) 
                              for domain in self.domain]))
        rt.append(u' '.join([u"   range( %s )"%canonicalName(range,self.graph) 
                              for range in self.range]))
        rt=u'\n'.join([expr for expr in rt if expr])
        rt+=u'\n)'
        return unicode(rt).encode('utf-8')
                    
    def _get_subPropertyOf(self):
        for anc in self.graph.objects(subject=self.identifier,predicate=RDFS.subPropertyOf):
            yield Property(anc,graph=self.graph)
    def _set_subPropertyOf(self, other):
        if not other:
            return        
        for sP in other:
            self.graph.add((self.identifier,RDFS.subPropertyOf,classOrIdentifier(sP)))
            
    @TermDeletionHelper(RDFS.subPropertyOf)
    def _del_subPropertyOf(self):            
        pass            
                        
    subPropertyOf = property(_get_subPropertyOf, _set_subPropertyOf, _del_subPropertyOf)

    def _get_inverseOf(self):
        for anc in self.graph.objects(subject=self.identifier,predicate=OWL_NS.inverseOf):
            yield Property(anc,graph=self.graph)
    def _set_inverseOf(self, other):
        if not other:
            return        
        self.graph.add((self.identifier,OWL_NS.inverseOf,classOrIdentifier(other)))
        
    @TermDeletionHelper(OWL_NS.inverseOf)
    def _del_inverseOf(self):            
        pass            
                
    inverseOf = property(_get_inverseOf, _set_inverseOf, _del_inverseOf)

    def _get_domain(self):
        for dom in self.graph.objects(subject=self.identifier,predicate=RDFS.domain):
            yield Class(dom,graph=self.graph)
    def _set_domain(self, other):
        if not other:
            return
        if isinstance(other,(Individual,Identifier)):
            self.graph.add((self.identifier,RDFS.domain,classOrIdentifier(other)))
        else:
            for dom in other:
                self.graph.add((self.identifier,RDFS.domain,classOrIdentifier(dom)))
                
    @TermDeletionHelper(RDFS.domain)
    def _del_domain(self):            
        pass            
                                
    domain = property(_get_domain, _set_domain, _del_domain)

    def _get_range(self):
        for ran in self.graph.objects(subject=self.identifier,predicate=RDFS.range):
            yield Class(ran,graph=self.graph)
    def _set_range(self, ranges):
        if not ranges:
            return
        if isinstance(ranges,(Individual,Identifier)):
            self.graph.add((self.identifier,RDFS.range,classOrIdentifier(ranges)))
        else:        
            for range in ranges:
                self.graph.add((self.identifier,RDFS.range,classOrIdentifier(range)))
                
    @TermDeletionHelper(RDFS.range)
    def _del_range(self):            
        pass            
                                
    range = property(_get_range, _set_range, _del_range)
        
def CommonNSBindings(graph,additionalNS={}):
    """
    Takes a graph and binds the common namespaces (rdf,rdfs, & owl)
    """
    namespace_manager = NamespaceManager(graph)
    namespace_manager.bind('rdfs',RDFS.RDFSNS)
    namespace_manager.bind('rdf',RDF.RDFNS)
    namespace_manager.bind('owl',OWL_NS)
    for prefix,uri in additionalNS.items():
        namespace_manager.bind(prefix, uri, override=False)
    graph.namespace_manager = namespace_manager
        
def test():
    import doctest
    doctest.testmod()

if __name__ == '__main__':
    test()
