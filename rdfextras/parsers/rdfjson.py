# RdfJsonParser.py
# Author: Rob Sanderson
# RDFLib 3.1 compatibility updates: Richard Jones
#
#
# TODO:
#   This code reads the entire JSON object into memory before parsing,
#   but we should consider streaming the input to deal with arbitrarily
#   large graphs
"""
This serialiser will read in an RDF/JSON formatted document and create
an RDF graph

See:
  http://docs.api.talis.com/platform-api/output-types/rdf-json

It was originally written by Rob Sanderson as a plugin for RDFLib 2.x.
This version modifies the import paths for compatibility with RDFLib 3.x
and changes its name to RdfJsonParser due to the large number of
other JSON serialisations of RDF.

See:
  http://code.google.com/p/rdflib/issues/detail?id=76


"""

import logging
try:
    import json
except ImportError:
    import simplejson as json

from rdflib.parser import Parser
from rdflib.term import URIRef, BNode, Literal
log = logging.getLogger(__name__)

class RdfJsonParser(Parser):
    
    def __init__(self):
        pass

    def parse(self, source, sink, **args):
        """
        Parse an RDF/JSON-formatted document and create an RDF graph.
        
        Params:
        :source: a stream (a URL, a file or a StringIO object) or 
                 a string (of data), as per the standard API for 
                 rdflib parsers.

        Example usage:

        >>> from rdflib import Graph, plugin
        >>> from rdflib.parser import Parser
        >>> plugin.register("rdf-json", Parser, 
        ...    "rdfextras.parsers.rdfjson", "RdfJsonParser")
        ...
        >>> g = Graph()
        >>> testrdfjson = '''{
        ...   "http://example.org/about" : 
        ...     {
        ...        "http://purl.org/dc/elements/1.1/title": [ 
        ...             { "type" : "literal" , "value" : "Anna's Homepage." } 
        ...         ]
        ...     }
        ... }'''
        ... 
        >>> g.parse(data=testrdfjson, format="rdf-json") # doctest: +ELLIPSIS
        <Graph identifier=... (<class 'rdflib.graph.Graph'>)>
        >>> rdfxml = g.serialize(format="xml")
        >>> assert '''Anna's Homepage''' in rdfxml
        """

        data = source.getByteStream().read()
        objs = json.loads(data)

        # check if pretty-json
        keys = objs.keys()
        pretty = 0
        bindings = {}

        for k in keys:
            if k.startswith('xmlns$') or k.startswith('xmlns:'):
                pretty = 1
                bindings[k[6:]] = objs[k]

        for k in keys:
            if not k.startswith('xmlns$') and not k.startswith('xmlns:'):
                if k[0] == "_" and k[1] in [':', '$']:
                    # bnode
                    s = BNode(k[2:])
                else:
                    # uri
                    s = URIRef(k)
                # predicates
                preds = objs[k]
                for (p, v) in preds.items():
                    if pretty:
                        dpidx = p.find('$')
                        if dpidx == -1:                            
                            dpidx = p.find(':')
                        if dpidx > -1:
                            pfx = p[:dpidx]
                            dmn = bindings.get(pfx, '')
                            if dmn:
                                pred = URIRef(dmn + p)
                            else:
                                raise ValueError("Unassigned Prefix: %s" % pfx)
                        else:
                            pred = URIRef(p)
                    else:
                        pred = URIRef(p)
                        
                    for vh in v:
                        value = vh['value']
                        vt = vh['type']
                        if vt == 'literal':
                            args = {}
                            lang = vh.get('lang', '')
                            if lang:
                                args['lang'] = lang                            
                            datatype = vh.get('datatype', '')
                            if datatype:
                                args['datatype'] = datatype
                            val = Literal(value, **args)
                        elif vt == 'uri':
                            val = URIRef(value)
                        elif vt == 'bnode':
                            val = BNode(val[2:])
                        sink.add((s, pred, val))
        # returns None
