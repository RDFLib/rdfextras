# RdfJsonParser.py
# Author: Richard Jones
#
# This serialiser will read in an JSON-LD formatted document and create
# an RDF Graph
# See:
#   http://json-ld.org/
#
# TODO:
#   This code reads the entire JSON object into memory before parsing,
#   but we should consider streaming the input to deal with arbitrarily
#   large graphs
"""
Example usage:

from rdflib import Graph, plugin
from rdflib.parser import Parser
plugin.register("json-ld", Parser, "jsonld.JsonLDParser", "JsonLDParser")
g = Graph()
g.parse("test-ld.json", format="json-ld")
"""

try:
    import json
except ImportError:
    import simplejson as json

from rdflib.parser import Parser
from rdflib.term import URIRef, BNode, Literal

from copy import deepcopy
import re

class JsonLDParser(Parser):
    
    def __init__(self):
        self.default_subject = None
        self.namespaces = []

        # regular expressions used        
        #self.uriref = r'<([^:]+:[^\s"<>]+)>'
        #self.literal = r'"([^"\\]*(?:\\.[^"\\]*)*)"'
        #self.litinfo = r'(?:@([a-z]+(?:-[a-z0-9]+)*)|\^\^' + self.uriref + r')?'

        #self.r_line = re.compile(r'([^\r\n]*)(?:\r\n|\r|\n)')
        #self.r_wspace = re.compile(r'[ \t]*')
        #self.r_wspaces = re.compile(r'[ \t]+')
        #self.r_tail = re.compile(r'[ \t]*\.[ \t]*')
        #self.r_uriref = re.compile(self.uriref)
        #self.r_nodeid = re.compile(r'_:([A-Za-z][A-Za-z0-9]*)')
        #self.r_literal = re.compile(self.literal + self.litinfo)
        #self.uriref = r'[<]{0,1}(.*)[>]{0,1}' # uris

    def parse(self, source, sink, **args):

        # load the incoming stream into a json object
        data = source.getByteStream().read()
        jsonObj = json.loads(data)

        self.sink = sink

        # get the default subject which is used if no "@" is provided
        self.default_subject = args.get("default_subject")

        # get the namespace portion and the graph portion
        self.namespaces = jsonObj.get("#", [])
        ld_graph = jsonObj.get("@", [])

        # go through the subject portions of the ld_graph and process
        # them
        for subject_graph in ld_graph:
            # go through the predicates in the subject_graph and handle
            # them
            self.parse_subject_graph(subject_graph)

    def get_subject(self, subject_dict):
        subject = subject_dict.get("@", self.default_subject)
        if subject is None:
            raise ValueError("No Default Subject and no explicit subject in subject_dict: %s" % str(subject_dict))
        return URIRef(subject)

    def get_subject_namespaces(self, subject_graph):
        ns = subject_graph.get("#", None)
        if ns is None:
            # there are no subject specific namespaces, so just send back   
            # the default namespaces
            return self.namespaces
        local_namespaces = deepcopy(self.namespaces)
        for n in ns:
            local_namespaces[n] = ns[n]
        return local_namespaces

    def get_rdf_types(self, subject_graph):
        t = subject_graph.get("a", None)
        if t is None:
            return None
        return self.parse_value(t)

    def parse_value(self, value_entity):
        value_objects = []

        # value entity could be a string or an array
        if isinstance(value_entity, list):
            for entity in value_entity:
                value_objs = self.parse_value(entity)
                if len(value_objs) > 1:
                    raise ValueError("Multiple nested arrays found in rdf object: " + str(value_entity)) 
                value_objects.append(value_objs[0]) # there should be only one (see error thrown above)
            return value_objects
        else:
            # value of the form (N3 format):
            # [value]@[lang]^^[datatype]
            return [self.parse_single_object(value_entity)]

    def parse_single_object(self, obj):
        # taken from the ntriples parser (but couldn't re-use directly)
        objt = self.uriref(obj) or self.nodeid(obj) or self.literal(obj)
        if objt is False:
            raise ValueError("Unrecognised object type: " + str(obj))
        return objt

    def uriref(self, obj):
        if obj.startswith("<") and obj.endswith(">") and not obj.startswith("<_:"):
            uri = obj[1:len(obj) - 1]
            return URIRef(uri)
        return False

    def nodeid(self, obj):
        if obj.startswith("<_") or obj.startswith("_:"):
            if obj.startswith("<") and obj.endswith(">"):
                bnode = obj[1:len(obj) - 1]
                return BNode(bnode)
            else:
                return BNode(obj)
        return False

    def literal(self, obj):
        rx = re.compile('([^(\\@)^(\^\^)]*)(\\@){0,1}([^\^]*)(\^\^){0,1}(.*)')
        if not obj.startswith("<") and not obj.startswith("_:"):
            m = rx.match(obj)
            # group 1 is the literal
            # group 3 is the language
            # group 5 is the datatype
            literal = m.group(1) if m.group(1) is not None and m.group(1) != "" else None
            lang = m.group(3) if m.group(3) is not None and m.group(3) != "" else None
            datatype = m.group(5) if m.group(5) is not None and m.group(5) != "" else None
            lit = Literal(literal, lang, datatype)
            return lit
        return False

    def parse_predicate(self, pred, local_namespaces):
        bits = pred.split(":", 1)
        if len(bits) == 1:
            # we need to prefix with the #base namespace
            vocab = local_namespaces.get("#vocab")
            if vocab is None:
                raise ValueError("predicate with no prefix provided, and no #vocab provided: " + pred)
            return URIRef(vocab + bits[0])
        else:
            ns = local_namespaces.get(bits[0])
            if ns is not None:
                return URIRef(ns + bits[1])
            vocab = local_namespaces.get("#vocab")
            if vocab is None:
                raise ValueError("predicate with un-identified prefix, and no #vocab provided: " + pred)
            return URIRef(vocab + bits[1])

    def parse_subject_graph(self, subject_graph):
        
        # get the subject/default subject or throw an error
        subject = self.get_subject(subject_graph)

        # get the subject-local namespaces
        local_namespaces = self.get_subject_namespaces(subject_graph)
        
        # handle the special case of rdf:type
        type_values = self.get_rdf_types(subject_graph)

        # add what we know so far to the sink
        if type_values is not None:
            for type_value in type_values:
                self.sink.add((subject, URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"), type_value))

        for pred in subject_graph.keys():
            if pred == "@" or pred == "#" or pred == "a":
                continue # skip the special keys

            # interpret the predicate
            predicate = self.parse_predicate(pred, local_namespaces)

            # for each predicate, get a list of the predicate and its objects
            # as tuples (i.e. get a list of tuples)
            objects = self.parse_value(subject_graph[pred])

            for obj in objects:
                self.sink.add((subject, predicate, obj))
            
