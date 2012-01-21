from rdflib import BNode
from rdflib import Literal
from rdflib import URIRef
from rdflib.graph import Graph
from rdflib.query import Result
from xml.dom import XML_NAMESPACE
from xml.sax.saxutils import XMLGenerator
from xml.sax.xmlreader import AttributesNSImpl
from cStringIO import StringIO
import itertools

SPARQL_XML_NAMESPACE = u'http://www.w3.org/2005/sparql-results#'

# Migrated in from rdflib.QueryResult
class QueryResult(object):
    """
    A common class for representing query result in a variety of formats, namely:
    
    xml   : as an XML string using the XML result format of the query language
    python: as Python objects
    json  : as JSON
    """
    def __init__(self,pythonResult):
        self.rt = pythonResult
    
    def serialize(self,format='xml'):
        pass

try:
    from Ft.Xml import MarkupWriter
    class SPARQLXMLWriter:
        """
        4Suite-based SPARQL XML Writer
        """
        def __init__(self,output):
            self.writer = MarkupWriter(output, indent=u"yes")
            self.writer.startDocument()
            self.writer.startElement(u'sparql',namespace=SPARQL_XML_NAMESPACE)
            self.askResult=False
        
        def write_header(self,allvarsL):
            self.writer.startElement(u'head', namespace=SPARQL_XML_NAMESPACE)
            if allvarsL:
                for i in xrange(0,len(allvarsL)) :
                    self.writer.startElement(u'variable',namespace=SPARQL_XML_NAMESPACE,attributes={u'name':unicode(allvarsL[i])})
                    self.writer.endElement(u'variable')
            self.writer.endElement( u'head')
        
        def write_results_header(self,orderBy,distinct):
            self.writer.startElement(u'results',namespace=SPARQL_XML_NAMESPACE,attributes={u'ordered' : unicode(orderBy and 'true' or 'false'),
                                                                                           u'distinct': unicode(distinct and 'true' or 'false')})
        
        def write_start_result(self):
            self.writer.startElement(u'result',namespace=SPARQL_XML_NAMESPACE)
            self._resultStarted = True
        
        def write_end_result(self):
            assert self._resultStarted
            self.writer.endElement(u'result',namespace=SPARQL_XML_NAMESPACE)
            self._resultStarted = False
        
        def write_ask(self,val):
            self.writer.startElement(u'boolean', namespace=SPARQL_XML_NAMESPACE)
            self.writer.text((val and u't' or u'f')+unicode(val)[1:])
            self.writer.endElement(u'boolean')
            self.askResult=True
        
        def write_binding(self,name,val):
            assert self._resultStarted
            if val is not None:
                attrs = {u'name':unicode(name)}
                self.writer.startElement(u'binding', namespace=SPARQL_XML_NAMESPACE, attributes=attrs)
                if isinstance(val,URIRef) :
                    self.writer.startElement(u'uri', namespace=SPARQL_XML_NAMESPACE)
                    self.writer.text(val)
                    self.writer.endElement(u'uri')
                elif isinstance(val,BNode) :
                    self.writer.startElement(u'bnode', namespace=SPARQL_XML_NAMESPACE)
                    self.writer.text(val)
                    self.writer.endElement(u'bnode')
                elif isinstance(val,Literal) :
                    attrs = {}
                    if val.language :
                        attrs[(u'lang', XML_NAMESPACE)] = unicode(val.language)
                    elif val.datatype:
                        attrs[u'datatype'] = unicode(val.datatype)
                    self.writer.startElement(u'literal', namespace=SPARQL_XML_NAMESPACE, attributes=attrs)
                    self.writer.text(val)
                    self.writer.endElement(u'literal')
                
                else:
                    raise Exception("Unsupported RDF term: %s"%val)
                
                self.writer.endElement(u'binding')
        
        def close(self):
            if not self.askResult:
                self.writer.endElement(u'results')
            self.writer.endElement(u'sparql')
    
except:
    class SPARQLXMLWriter:
        """
        Python saxutils-based SPARQL XML Writer
        """
        def __init__(self, output, encoding='utf-8'):
            writer = XMLGenerator(output, encoding)
            writer.startDocument()
            writer.startPrefixMapping(u'sparql',SPARQL_XML_NAMESPACE)
            writer.startPrefixMapping(u'xml', XML_NAMESPACE)
            writer.startElementNS((SPARQL_XML_NAMESPACE, u'sparql'), u'sparql', AttributesNSImpl({}, {}))
            self.writer = writer
            self._output = output
            self._encoding = encoding
            self.askResult=False
        
        def write_header(self,allvarsL):
            self.writer.startElementNS((SPARQL_XML_NAMESPACE, u'head'), u'head', AttributesNSImpl({}, {}))
            for i in xrange(0,len(allvarsL)) :
                attr_vals = {
                    (None, u'name'): unicode(allvarsL[i]),
                    }
                attr_qnames = {
                    (None, u'name'): u'name',
                    }
                self.writer.startElementNS((SPARQL_XML_NAMESPACE, u'variable'),
                                             u'variable',
                                             AttributesNSImpl(attr_vals, attr_qnames))
                self.writer.endElementNS((SPARQL_XML_NAMESPACE, u'variable'), u'variable')
            self.writer.endElementNS((SPARQL_XML_NAMESPACE, u'head'), u'head')
        
        def write_ask(self,val):
            raise
        
        def write_results_header(self,orderBy,distinct):
            attr_vals = {
                (None, u'ordered')  : unicode(orderBy and 'true' or 'false'),
                (None, u'distinct') : unicode(distinct and 'true' or 'false'),
                }
            attr_qnames = {
                (None, u'ordered')  : u'ordered',
                (None, u'distinct') : u'distinct'
                }
            self.writer.startElementNS((SPARQL_XML_NAMESPACE, u'results'),
                                         u'results',
                                         AttributesNSImpl(attr_vals, attr_qnames))
        
        def write_start_result(self):
            self.writer.startElementNS(
                    (SPARQL_XML_NAMESPACE, u'result'), u'result', AttributesNSImpl({}, {}))
            self._resultStarted = True
        
        def write_end_result(self):
            assert self._resultStarted
            self.writer.endElementNS((SPARQL_XML_NAMESPACE, u'result'), u'result')
            self._resultStarted = False
        
        def write_binding(self,name,val):
            assert self._resultStarted
            if val:
                attr_vals = {
                    (None, u'name')  : unicode(name),
                    }
                attr_qnames = {
                    (None, u'name')  : u'name',
                    }
                self.writer.startElementNS((SPARQL_XML_NAMESPACE, u'binding'),
                                       u'binding',
                                       AttributesNSImpl(attr_vals, attr_qnames))
                
                if isinstance(val,URIRef) :
                    self.writer.startElementNS((SPARQL_XML_NAMESPACE, u'uri'),
                                           u'uri',
                                           AttributesNSImpl({}, {}))
                    self.writer.characters(val)
                    self.writer.endElementNS((SPARQL_XML_NAMESPACE, u'uri'),u'uri')
                elif isinstance(val,BNode) :
                    self.writer.startElementNS((SPARQL_XML_NAMESPACE, u'bnode'),
                                           u'bnode',
                                           AttributesNSImpl({}, {}))
                    self.writer.characters(val)
                    self.writer.endElementNS((SPARQL_XML_NAMESPACE, u'bnode'),u'bnode')
                elif isinstance(val,Literal) :
                    attr_vals = {}
                    attr_qnames = {}
                    if val.language :
                        attr_vals[(XML_NAMESPACE, u'lang')] = val.language
                        attr_qnames[(XML_NAMESPACE, u'lang')] = u"xml:lang"
                    elif val.datatype:
                        attr_vals[(None,u'datatype')] = val.datatype
                        attr_qnames[(None,u'datatype')] = u'datatype'
                    
                    self.writer.startElementNS((SPARQL_XML_NAMESPACE, u'literal'),
                                           u'literal',
                                           AttributesNSImpl(attr_vals, attr_qnames))
                    self.writer.characters(val)
                    self.writer.endElementNS((SPARQL_XML_NAMESPACE, u'literal'),u'literal')
                
                else:
                    raise Exception("Unsupported RDF term: %s"%val)
                
                self.writer.endElementNS((SPARQL_XML_NAMESPACE, u'binding'),u'binding')
        
        def close(self):
            self.writer.endElementNS((SPARQL_XML_NAMESPACE, u'results'), u'results')
            self.writer.endElementNS((SPARQL_XML_NAMESPACE, u'sparql'), u'sparql')
            self.writer.endDocument()
        
    

def retToJSON(val):
    if isinstance(val,URIRef):
        return '"type": "uri", "value" : "%s"' % val
    elif isinstance(val,BNode) :
        return '"type": "bnode", "value" : "%s"' % val
    elif isinstance(val,Literal):
        if val.language != "":
            return '"type": "literal", "xml:lang" : "%s", "value" : "%s"' % (val.language, val)
            attr += ' xml:lang="%s" ' % val.language
        elif val.datatype != "" and val.datatype != None:
            return '"type": "typed=literal", "datatype" : "%s", "value" : "%s"' % (val.datatype, val)
        else:
            return '"type": "literal", "value" : "%s"' % val
    else:
        return '"type": "literal", "value" : "%s"' % val

def bindingJSON(name, val):
    if val == None:
        return ""
    retval = ''
    retval += '                   "%s" : {' % name
    retval += retToJSON(val)
    # retval += '}\n'
    return retval


class SavedIterable(object):
    """Wrap an iterable and cache it.
    
    From http://code.activestate.com/recipes/576941/
    
    Recipe 576941: Caching iterable wrapper
    
    The SavedIterable can be accessed streamingly, while still being
    incrementally cached. Later attempts to iterate it will access the
    whole of the sequence.
    
    When it has been cached to its full extent once, it reduces to a
    thin wrapper of a sequence iterator. The SavedIterable will pickle
    into a list.
    
    >>> s = SavedIterable(xrange(5))
    >>> iter(s).next()
    0
    >>> list(s)
    [0, 1, 2, 3, 4]
    
    >>> iter(s)   # doctest: +ELLIPSIS
    <listiterator object at 0x...>
    
    >>> import pickle
    >>> pickle.loads(pickle.dumps(s))
    [0, 1, 2, 3, 4]
    
    >>> u = SavedIterable(xrange(5))
    >>> one, two = iter(u), iter(u)
    >>> one.next(), two.next()
    (0, 0)
    >>> list(two)
    [1, 2, 3, 4]
    >>> list(one)
    [1, 2, 3, 4]
    
    >>> SavedIterable(range(3))
    [0, 1, 2]
    """
    def __new__(cls, iterable):
        if isinstance(iterable, list):
            return iterable
        return object.__new__(cls)
    
    def __init__(self, iterable):
        self.iterator = iter(iterable)
        self.data = []
    
    def __iter__(self):
        if self.iterator is None:
            return iter(self.data)
        return self._incremental_caching_iter()
    
    def _incremental_caching_iter(self):
        indices = itertools.count()
        while True:
            idx = indices.next()
            try:
                yield self.data[idx]
            except IndexError:
                pass
            else:
                continue
            if self.iterator is None:
                return
            try:
                x = self.iterator.next()
                self.data.append(x)
                yield x
            except StopIteration:
                self.iterator = None
    
    def __reduce__(self):
        # pickle into a list with __reduce__
        # (callable, args, state, listitems)
        return (list, (), None, iter(self))
    


class SPARQLQueryResult(Result):
    """
    Query result class for SPARQL
    
    xml   : as an XML string conforming to the SPARQL XML result format: http://www.w3.org/TR/rdf-sparql-XMLres/
    python: as Python objects
    json  : as JSON
    graph : as an RDFLib Graph - for CONSTRUCT and DESCRIBE queries
    """
    def __init__(self,qResult):
        """
        The constructor is the result straight from sparql-p, which is uple of
        1) a list of tuples (in select order, each item is the valid binding
        for the corresponding variable or 'None') for SELECTs , a SPARQLGraph
        for DESCRIBE/CONSTRUCT, and boolean for ASK 
        2) the variables selected
        3) *all* the variables in the Graph Patterns 
        4) the order clause 
        5) the DISTINCT clause
        """
        self.noAnswers = 0
        self.construct=False
        if isinstance(qResult,bool):
            self.askAnswer = [qResult]
            result=None
            selectionF=None
            allVars=None
            orderBy=None
            distinct=None
            topUnion = None
        elif isinstance(qResult,Graph):
            self.askAnswer = []
            result=qResult
            self.construct=True
            selectionF=None
            allVars=None
            orderBy=None
            distinct=None
            topUnion = None
        else:
            self.askAnswer = []
            # print("qResult",qResult)
            result,selectionF,allVars,orderBy,distinct,topUnion = qResult
        self.result = result
        self.topUnion = topUnion
        if isinstance(qResult,bool):
            self.selected = result
        else:
            self.selected = isinstance(result,list) and result or SavedIterable(result)
        self.selectionF = selectionF
        self.allVariables = allVars
        self.orderBy = orderBy
        self.distinct = distinct
    
    def __len__(self):
        if isinstance(self.selected,list):
            return len(self.selected)
        elif isinstance(self.selected,SavedIterable):
            raise NotImplementedError("Results are an iterable!")
        else:
            return 1
    
    def __iter__(self):
        """Iterates over the result entries"""
        if isinstance(self.selected,(list,SavedIterable)):
            if self.topUnion and not self.orderBy:
                for binding in self.topUnion:
                    self.noAnswers += 1
                    if not binding:
                        continue
                    if len(self.selectionF)==1:
                        yield binding[self.selectionF[0]]
                    else:
                        yield [binding.get(i) for i in self.selectionF]
            else:
                for item in self.selected:
                    self.noAnswers += 1
                    yield item
        else:
            self.noAnswers = len(self.selected)
            yield self.selected
    
    def serialize(self,format='xml'):
        if isinstance(self.result,Graph):
            return self.result.serialize(format=format)
        elif format == 'python':
            if self.askAnswer:
                return self.askAnswer[0]
            else:
                return self
        elif format in ['json','xml']:
           retval = ""
           allvarsL = self.allVariables
           
           #In either serialization form we need to know the length of the answers
           
           if format == "json" :
               retval += '    "results" : {\n'
               retval += '          "ordered" : %s,\n' % (self.orderBy and 'true' or 'false')
               retval += '          "distinct" : %s,\n' % (self.distinct and 'true' or 'false')
               retval += '          "bindings" : [\n'
               #We need to load the entire list in memory for JSON serialization
               self.selected = list(self.selected)
               self.noAnswers = len(self.selected)
               for i in xrange(0,len(self.selected)):
                   hit = self.selected[i]
                   retval += '               {\n'
                   bindings = []
                   if len(self.selectionF) == 0:
                        for j in xrange(0, len(allvarsL)):
                            b = bindingJSON(allvarsL[j],hit[j])
                            if b != "":
                                bindings.append(b)
                   elif len(self.selectionF) == 1:
                       bindings.append(bindingJSON(self.selectionF[0],hit))
                   else:
                        for j in xrange(0, len(self.selectionF)):
                            b = bindingJSON(self.selectionF[j],hit[j])
                            if b != "":
                                bindings.append(b)
                   
                   retval += "},\n".join(bindings)
                   retval += "}\n"
                   retval += '                }'
                   if i != len(self.selected) -1:
                       retval += ',\n'
                   else:
                       retval += '\n'
               retval += '           ]\n'
               retval += '    }\n'
               retval += '}\n'
               
               selected_vars = self.selectionF
               
               if len(selected_vars) == 0:
                   selected_vars = allvarsL
               
               header = ""
               header += '{\n'
               header += '   "head" : {\n        "vars" : [\n'
               for i in xrange(0,len(selected_vars)) :
                   header += '             "%s"' % selected_vars[i]
                   if i == len(selected_vars) - 1 :
                       header += '\n'
                   else :
                       header += ',\n'
               header += '         ]\n'
               header += '    },\n'
               
               retval = header + retval
           
           elif format == "xml" :
               # xml output
               out = StringIO()
               writer = SPARQLXMLWriter(out)
               if self.askAnswer:
                   writer.write_header(allvarsL)
                   writer.write_ask(self.askAnswer[0])
               else:
                   writer.write_header(allvarsL)
                   writer.write_results_header(self.orderBy,self.distinct)
                   if self.topUnion:
                       for binding in self.topUnion:
                           self.noAnswers += 1
                           writer.write_start_result()
                           assert isinstance(binding,dict),repr(binding)
                           for key,val in binding.items():
                               if not self.selectionF or key in self.selectionF:
                                   writer.write_binding(key,val)
                           writer.write_end_result()
                   else:
                       for hit in self.selected :
                           self.noAnswers += 1
                           if len(self.selectionF) == 0 :
                               assert not self.topUnion,"topUnion should not be specified!"
                               writer.write_start_result()
                               if len(allvarsL) == 1:
                                   hit = (hit,) # Not an iterable - a parser bug?
                               for j in xrange(0,len(allvarsL)) :
                                   if not len(hit) < j+1:
                                       writer.write_binding(allvarsL[j],hit[j])
                               writer.write_end_result()
                           elif len(self.selectionF) == 1 :
                               writer.write_start_result()
                               writer.write_binding(self.selectionF[0],hit)
                               writer.write_end_result()
                           else:
                               writer.write_start_result()
                               for j in xrange(0,len(self.selectionF)) :
                                   writer.write_binding(self.selectionF[j],hit[j])
                               writer.write_end_result()
               writer.close()
               return out.getvalue()
           
           return retval
        else:
           raise Exception("Result format not implemented: %s"%format)

# Convenience
# from rdfextras.sparql2sql.QueryResult import retToJSON
# from rdfextras.sparql2sql.QueryResult import bindingJSON
# from rdfextras.sparql2sql.QueryResult import SPARQLXMLWriter
# from rdfextras.sparql2sql.QueryResult import QueryResult
# from rdfextras.sparql2sql.QueryResult import SavedIterable
# from rdfextras.sparql2sql.QueryResult import SPARQLQueryResult
