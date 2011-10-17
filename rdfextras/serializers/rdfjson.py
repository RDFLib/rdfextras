# RdfJsonSerializer.py
# Author: Rob Sanderson
# RDFLib 3.1 compatibility updates: Richard Jones

# TODO:
#   This code writes the entire JSON object into memory before serializing,
#   but we should consider streaming the output to deal with arbitrarily
#  large graphs

"""
This serialiser will output an RDF Graph as an RDF JSON formatted document.

See:
  http://docs.api.talis.com/platform-api/output-types/rdf-json

It was originally written by Rob Sanderson as a plugin for RDFLib 2.x.
This version modifies the import paths for compatibility with RDFLib 3.x
and changes its name to RdfJsonSerializer due to the large number of
other JSON serialisations of RDF.

See:
  http://code.google.com/p/rdflib/issues/detail?id=76


Example usage:

.. sourcecode:: pycon

    >>> from rdflib import Graph, plugin
    >>> from rdflib.serializer import Serializer
    >>> from StringIO import StringIO
    >>> plugin.register("rdf-json", Serializer, 
    ...     "rdfextras.serializers.rdfjson", "RdfJsonSerializer")
    ...
    >>> plugin.register("rdf-json-pretty", Serializer,
    ...     "rdfextras.serializers.rdfjson", "PrettyRdfJsonSerializer")
    ...
    >>> test = '''
    ... <http://example.org/about> 
    ...     <http://purl.org/dc/elements/1.1/title> 
    ...    "Anna's Homepage" .'''
    ...
    >>> g = Graph()
    >>> g.parse(StringIO(test), format="n3") # doctest: +ELLIPSIS
    <Graph identifier=... (<class 'rdflib.graph.Graph'>)>
    >>> print(g.serialize(None, format="rdf-json")) 
    {
      "http://example.org/about": {
        "http://purl.org/dc/elements/1.1/title": [
          {
            "type": "literal", 
            "value": "Anna's Homepage"
          }
        ]
      }
    }
    >>> print(g.serialize(None, format="rdf-json-pretty")) 
    {
      "xmlns$rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#", 
      "http://example.org/about": {
        "ns1$title": [
          {
            "type": "literal", 
            "value": "Anna's Homepage"
          }
        ]
      }, 
      "xmlns$ns1": "http://purl.org/dc/elements/1.1/"
    }
"""

from rdflib.serializer import Serializer
from rdflib.term import URIRef
from rdflib.term import Literal

try:
    import json
except ImportError:
    import simplejson as json

from rdflib.util import uniq

class RdfJsonSerializer(Serializer):
    """
    This serialiser outputs an RDF Graph as an RDF JSON formatted document.
    Output may be direct to console: 

    .. sourcecode:: python
        
        g.serialize(None, format="rdf-json)

    or to a named file:

    .. sourcecode:: python
        
        g.serialize("/tmp/results.json", format="rdf-json)

    See:
        http://docs.api.talis.com/platform-api/output-types/rdf-json

    Params:
    :stream: a stream, or None, as per standard with rdflib serializers
    :base: a base URI
    :encoding: type of RDFJson encoding - either "rdf-json" for vanilla, 
               RDFJson or "rdf-json-pretty" for a prettified output. 

    Example usage:
    
    .. sourcecode:: python
        from rdflib import Graph, plugin
        from rdflib.serializer import Serializer

        plugin.register("rdf-json", Serializer, 
                "rdfextras.serializers.rdfjson", "RdfJsonSerializer")

        g = Graph()
        g.parse("test.rdf")
        g.serialize(None, "rdf-json")

    """
    gdataColon = 0

    def __init__(self, store):
        super(RdfJsonSerializer, self).__init__(store)
        self.gdataColon = 0
        self.prettyPredName = 0


    def serialize(self, stream, base=None, encoding=None, **args):
        self.base = base
        self.__stream = stream
        self.__serialized = {}
        self.write = lambda u: stream.write(u.encode(self.encoding, 'replace'))
        self.jsonObj = {}

        self.initObj()

        for subject in self.store.subjects():
            self.subject(subject)

        srlzd = json.dumps(self.jsonObj, indent=2)
        self.write(srlzd)
        del self.__serialized

    def initObj(self):
        pass

    def subject(self, subject):
        if not subject in self.__serialized:
            self.__serialized[subject] = 1

            if isinstance(subject, URIRef): 
                uri = self.relativize(subject)
            else:
                # Blank Node
                uri = '%s' % subject.n3()                
                if self.gdataColon:
                    uri = uri.replace(':', '$')
            data = {}
            for predicate, objt in self.store.predicate_objects(subject):
                if self.prettyPredName:
                    predname = self.store.namespace_manager.qname(predicate)
                else:
                    predname = self.relativize(predicate)
                if self.gdataColon:
                    predname = predname.replace(':', '$')
                value = self.value(objt)
                if data.has_key(predname):
                    data[predname].append(value)
                else:
                    data[predname] = [value]
            self.jsonObj[uri] = data

    def value(self, objt):
        data = {}
        if isinstance(objt, Literal):
            data['type'] = 'literal'
            if objt.language:
                data['lang'] = objt.language
            if objt.datatype:
                data['datatype'] = objt.datatype
            data['value'] = objt
        else:
            if isinstance(objt, URIRef):
                href = self.relativize(objt)
                data['type'] = 'uri'
            else:
                # BNode
                href= '%s' % objt.n3()                
                if self.gdataColon:
                    href = href.replace(':', '$')
                data['type'] = 'bnode'
            data['value'] = href

        return data

class PrettyRdfJsonSerializer(RdfJsonSerializer):
    """
    This serialiser outputs an RDF Graph as an RDF JSON formatted document.
    Output may be direct to console: 

    .. sourcecode:: python
        
        g.serialize(None, format="rdf-json)

    or to a named file:

    .. sourcecode:: python
        
        g.serialize("/tmp/results.json", format="rdf-json)

    See:
        http://docs.api.talis.com/platform-api/output-types/rdf-json

    Params:
    :stream: a stream, or None, as per standard with rdflib serializers
    :base: a base URI
    :encoding: type of RDF/JSON encoding - either "rdf-json" (for vanilla RDF/JSON) or "rdf-json-pretty" (for a prettified output). 

    Example usage:
    
    .. sourcecode:: python
        from rdflib import Graph, plugin
        from rdflib.serializer import Serializer

        plugin.register("rdf-json-pretty", Serializer, 
            "rdfextras.serializers.rdfjson", "PrettyRdfJsonSerializer")

        g = Graph()
        g.parse("test.rdf")
        g.serialize("/tmp/results.json", "rdf-json-pretty")
    
    """

    def __init__(self, store):
        super(PrettyRdfJsonSerializer, self).__init__(store)
        self.gdataColon = 1
        self.prettyPredName = 1

    def __bindings(self):
        store = self.store
        nm = store.namespace_manager
        bindings = {}
        for predicate in uniq(store.predicates()):
            prefix, namespace, name = nm.compute_qname(predicate)
            bindings[prefix] = URIRef(namespace)
        RDFNS = URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
        if "rdf" in bindings:
            assert bindings["rdf"]==RDFNS
        else:
            bindings["rdf"] = RDFNS
        for prefix, namespace in bindings.iteritems():
            yield prefix, namespace

    def initObj(self):
        for b in self.__bindings():            
            self.jsonObj['xmlns$%s' % b[0]] = '%s' % b[1]

