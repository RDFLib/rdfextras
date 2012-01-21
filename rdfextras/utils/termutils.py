"""Convenience functions for working with Terms and Graphs."""
from rdflib import BNode
from rdflib import Graph
from rdflib import Literal
from rdflib import URIRef
from rdflib import Variable
from rdflib.term import Statement
from rdflib.graph import QuotedGraph

__all__ = ['SUBJECT', 'PREDICATE', 'OBJECT', 'CONTEXT', 'TERM_COMBINATIONS', 
           'REVERSE_TERM_COMBINATIONS', 'TERM_INSTANTIATION_DICT',
           'GRAPH_TERM_DICT', 'normalizeGraph', 'term2Letter', 
           'constructGraph', 'triplePattern2termCombinations',
           'type2TermCombination', 'statement2TermCombination', 
           'escape_quotes']

SUBJECT = 0
PREDICATE = 1
OBJECT = 2
CONTEXT = 3
TERM_COMBINATIONS = dict(
    [(term, index) for index, term, in enumerate([
'UUUU', 'UUUB', 'UUUF', 'UUVU', 'UUVB', 'UUVF', 'UUBU', 'UUBB', 'UUBF',
'UULU', 'UULB', 'UULF', 'UUFU', 'UUFB', 'UUFF',
#
'UVUU', 'UVUB', 'UVUF', 'UVVU', 'UVVB', 'UVVF', 'UVBU', 'UVBB', 'UVBF',
'UVLU', 'UVLB', 'UVLF', 'UVFU', 'UVFB', 'UVFF',
#
'VUUU', 'VUUB', 'VUUF', 'VUVU', 'VUVB', 'VUVF', 'VUBU', 'VUBB', 'VUBF',
'VULU', 'VULB', 'VULF', 'VUFU', 'VUFB', 'VUFF',
#
'VVUU', 'VVUB', 'VVUF', 'VVVU', 'VVVB', 'VVVF', 'VVBU', 'VVBB', 'VVBF',
'VVLU', 'VVLB', 'VVLF', 'VVFU', 'VVFB', 'VVFF',
#
'BUUU', 'BUUB', 'BUUF', 'BUVU', 'BUVB', 'BUVF', 'BUBU', 'BUBB', 'BUBF',
'BULU', 'BULB', 'BULF', 'BUFU', 'BUFB', 'BUFF',
#
'BVUU', 'BVUB', 'BVUF', 'BVVU', 'BVVB', 'BVVF', 'BVBU', 'BVBB', 'BVBF',
'BVLU', 'BVLB', 'BVLF', 'BVFU', 'BVFB', 'BVFF',
#
'FUUU', 'FUUB', 'FUUF', 'FUVU', 'FUVB', 'FUVF', 'FUBU', 'FUBB', 'FUBF',
'FULU', 'FULB', 'FULF', 'FUFU', 'FUFB', 'FUFF',
#
'FVUU', 'FVUB', 'FVUF', 'FVVU', 'FVVB', 'FVVF', 'FVBU', 'FVBB', 'FVBF',
'FVLU', 'FVLB', 'FVLF', 'FVFU', 'FVFB', 'FVFF',
#
'sUUU', 'sUUB', 'sUUF', 'sUVU', 'sUVB', 'sUVF', 'sUBU', 'sUBB', 'sUBF',
'sULU', 'sULB', 'sULF', 'sUFU', 'sUFB', 'sUFF',
#
'sVUU', 'sVUB', 'sVUF', 'sVVU', 'sVVB', 'sVVF', 'sVBU', 'sVBB', 'sVBF',
'sVLU', 'sVLB', 'sVLF', 'sVFU', 'sVFB', 'sVFF'
])])
REVERSE_TERM_COMBINATIONS = dict(
    [(value, key) for key, value in TERM_COMBINATIONS.items()])

TERM_INSTANTIATION_DICT = {
    'U':URIRef,
    'B':BNode,
    'V':Variable,
    'L':Literal
}
GRAPH_TERM_DICT = {
    'F': (QuotedGraph, URIRef),
    'U': (Graph, URIRef),
    'B': (Graph, BNode)
}

def normalizeGraph(graph):
    """Takes an instance of a ``Graph`` and returns the instance's identifier 
    and  ``type``. 
    
    Types are ``U`` for a :class:`~rdflib.graph.Graph`, ``F`` for 
    a :class:`~rdflib.graph.QuotedGraph` and ``B`` for a 
    :class:`~rdflib.graph.ConjunctiveGraph`
    
    >>> from rdflib import plugin
    >>> from rdflib.graph import Graph, ConjunctiveGraph, QuotedGraph
    >>> from rdflib.store import Store
    >>> from rdflib import URIRef, Namespace
    >>> from rdfextras.utils.termutils import normalizeGraph
    >>> memstore = plugin.get('IOMemory', Store)()
    >>> g = Graph(memstore, URIRef("http://purl.org/net/bel-epa/gjh"))
    >>> normalizeGraph(g)
    (rdflib.term.URIRef('http://purl.org/net/bel-epa/gjh'), 'U')
    >>> g = ConjunctiveGraph(memstore, Namespace("http://purl.org/net/bel-epa/gjh"))
    >>> normalizeGraph(g)  #doctest: +ELLIPSIS
    (rdflib.term.BNode(...), 'B')
    >>> g = QuotedGraph(memstore, Namespace("http://purl.org/net/bel-epa/gjh"))
    >>> normalizeGraph(g)
    (Namespace('http://purl.org/net/bel-epa/gjh'), 'F')
    
    """
    if isinstance(graph,QuotedGraph):
        return graph.identifier, 'F'
    else:
        return graph.identifier, term2Letter(graph.identifier)


def term2Letter(term):
    """Relate a given term to one of several key types: 
     
    * :class:`~rdflib.term.BNode`, 
    * :class:`~rdflib.term.Literal`, 
    * :class:`~rdflib.term.Statement`
    * :class:`~rdflib.term.URIRef`, 
    * :class:`~rdflib.term.Variable`
    * :class:`~rdflib.graph.Graph`
    * :class:`~rdflib.graph.QuotedGraph`
     
    >>> import rdflib
    >>> from rdflib import plugin
    >>> from rdflib import URIRef, Namespace
    >>> from rdflib.term import BNode, Literal, Variable, Statement
    >>> from rdflib.graph import Graph, ConjunctiveGraph, QuotedGraph
    >>> from rdflib.store import Store
    >>> from rdfextras.utils.termutils import term2Letter
    >>> term2Letter(URIRef('http://purl.org/net/bel-epa.com/'))
    'U'
    >>> term2Letter(BNode())
    'B'
    >>> term2Letter(Literal(u''))
    'L'
    >>> term2Letter(Variable(u'x'))
    'V'
    >>> term2Letter(Graph())
    'B'
    >>> term2Letter(QuotedGraph("IOMemory", None))
    'F'
    >>> term2Letter(None)
    'L'
    >>> term2Letter(Statement((None, None, None), None))
    's'
    
    """
    if isinstance(term,URIRef):
        return 'U'
    elif isinstance(term,BNode):
        return 'B'
    elif isinstance(term,Literal):
        return 'L'
    elif isinstance(term,QuotedGraph):
        return 'F'
    elif isinstance(term,Variable):
        return 'V'
    elif isinstance(term,Statement):
        return 's'
    elif isinstance(term,Graph):
        return term2Letter(term.identifier)
    elif term is None:
        return 'L'
    else:
        raise Exception(
            ("The given term (%s) is not an instance of any " + \
            "of the known types (URIRef, BNode, Literal, QuotedGraph, " + \
            "or Variable).  It is a %s") \
            % (term, type(term)))


def constructGraph(key):
    """Given a key (one of 'F', 'U' or 'B'), returns 
    a tuple containing a ``Graph`` and an appropriate referent.
            
    >>> from rdfextras.utils.termutils import constructGraph
    >>> constructGraph('F')
    (<class 'rdflib.graph.QuotedGraph'>, <class 'rdflib.term.URIRef'>)
    >>> constructGraph('U')
    (<class 'rdflib.graph.Graph'>, <class 'rdflib.term.URIRef'>)
    >>> constructGraph('B')
    (<class 'rdflib.graph.Graph'>, <class 'rdflib.term.BNode'>)
    
    """
    return GRAPH_TERM_DICT[key]


def triplePattern2termCombinations((s,p,o)):
    """Maps a triple pattern to term combinations (non-functioning)"""
    combinations=[]
    #combinations.update(TERM_COMBINATIONS)
    if isinstance(o,Literal):
        for key,val in TERM_COMBINATIONS.items():
            if key[OBJECT] == 'O':
                combinations.append(val)
    return combinations


def type2TermCombination(member,klass,context):
    """Maps a type to a TermCombo"""
    try:
        rt = TERM_COMBINATIONS['%sU%s%s' % \
                        (term2Letter(member),
                         term2Letter(klass),
                         normalizeGraph(context)[-1])]
        return rt
    except:
        raise Exception("Unable to persist" + \
                        "classification triple: %s %s %s" % \
                                    (member,'rdf:type',klass,context))


def statement2TermCombination(subject,predicate,obj,context):
    """Maps a statement to a Term Combo"""
    return TERM_COMBINATIONS['%s%s%s%s' % \
                        (term2Letter(subject), term2Letter(predicate),
                         term2Letter(obj), normalizeGraph(context)[-1])]


def escape_quotes(qstr):
    """
    #FIXME:  This *may* prove to be a performance bottleneck and should 
             perhaps be implemented in C (as it was in 4Suite RDF)

    Ported from Ft.Lib.DbUtil
    """
    if qstr is None:
        return ''
    tmp = qstr.replace("\\","\\\\")
    tmp = tmp.replace("'", "\\'")
    return tmp



# Convenience for replacing "from termutils import *"

# from rdfextras.utils.termutils import SUBJECT
# from rdfextras.utils.termutils import PREDICATE
# from rdfextras.utils.termutils import OBJECT
# from rdfextras.utils.termutils import CONTEXT
# from rdfextras.utils.termutils import TERM_COMBINATIONS
# from rdfextras.utils.termutils import REVERSE_TERM_COMBINATIONS
# from rdfextras.utils.termutils import TERM_INSTANTIATION_DICT
# from rdfextras.utils.termutils import GRAPH_TERM_DICT
# from rdfextras.utils.termutils import normalizeGraph
# from rdfextras.utils.termutils import term2Letter
# from rdfextras.utils.termutils import constructGraph
# from rdfextras.utils.termutils import triplePattern2termCombinations
# from rdfextras.utils.termutils import type2TermCombination
# from rdfextras.utils.termutils import statement2TermCombination
# from rdfextras.utils.termutils import escape_quotes
