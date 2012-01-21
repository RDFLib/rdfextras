from rdflib.query import Result as QueryResult
from rdflib import Namespace, Variable, BNode, URIRef, Literal

SPARQL_NS = Namespace('http://www.w3.org/2005/sparql-results#')
sparqlNsBindings = {u'sparql':SPARQL_NS}

def CastToTerm(node):
    """
    Helper function that casts domlette node in SPARQL results
    to appropriate rdflib term
    """
    if node.localName == 'bnode':
        return BNode(node.firstChild.nodeValue)
    elif node.localName == 'uri':
        return URIRef(node.firstChild.nodeValue)
    elif node.localName == 'literal':
        if node.xpath('string(@datatype)'):
            dT = URIRef(node.xpath('string(@datatype)'))
            if False:#not node.xpath('*'):
                return Literal('',datatype=dT)
            else:
                return Literal(node.firstChild.nodeValue,
                               datatype=dT)
        else:
            if False:#not node.xpath('*'):
                return Literal('')
            else:
                return Literal(node.firstChild.nodeValue)
    else:
        raise Exception('Unknown answer type')

def TraverseSPARQLResultDOM(doc,asDictionary=False):
    """
    Returns a generator over tuples of results
    by (4Suite) XPath evaluation over the result XML
    """
    vars = [Variable(v.nodeValue) for v in
             doc.xpath('/sparql:sparql/sparql:head//@name',
             explicitNss=sparqlNsBindings)]
    for result in doc.xpath('/sparql:sparql/sparql:results/sparql:result',
                            explicitNss=sparqlNsBindings):
        currBind = {}
        values = []
        for binding in result.xpath('sparql:binding',
                                    explicitNss=sparqlNsBindings):
            varVal = binding.xpath('string(@name)')
            var = Variable(varVal)
            term = CastToTerm(binding.xpath('*')[0])
            values.append(term)
            currBind[var]=term
        if asDictionary:
            yield currBind,vars
        else:
            yield tuple(values),vars


class SPARQLResult(QueryResult):
    """
    Query result class for SPARQL
    
    xml   : as an XML string conforming to the SPARQL XML result format:
            http://www.w3.org/TR/rdf-sparql-XMLres/
    python: as Python objects
    json  : as JSON
    graph : as an RDFLib Graph - for CONSTRUCT and DESCRIBE queries
    """
    def __init__(self,result):
        self.result    = result
        self.resultDOM = None
        self.noAnswers = 0
        self.askAnswer = None
    
    def _parseResults(self):
        if self.resultDOM is not None:
            from Ft.Xml.Domlette import NonvalidatingReader
            self.resultDOM = NonvalidatingReader.parseString(self.result)
            self.askAnswer=self.resultDOM.xpath(
                                'string(/sparql:sparql/sparql:boolean)',
                                explicitNss=sparqlNsBindings)
    
    def __len__(self):
        raise NotImplementedError("Results are an iterable!")
    
    def __iter__(self):
        """Iterates over the result entries"""
        self._parseResults()
        if not self.askAnswer:
            for rt,vars in TraverseSPARQLResultDOC(self.resultDOM):
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
    


