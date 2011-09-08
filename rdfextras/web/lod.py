import re
import rdflib
import warnings
import urllib2
import collections

from endpoint import endpoint as lod

from flask import render_template, request, make_response, redirect, url_for, g

import mimeutils 

from rdfextras.sparql.results.htmlresults import term_to_string

from werkzeug.routing import BaseConverter
from werkzeug.urls import url_quote

class RDFUrlConverter(BaseConverter):
    def __init__(self, url_map):
        BaseConverter.__init__(self,url_map)
        self.regex="[^/].*?"
    def to_url(self, value):
        return url_quote(value, self.map.charset, safe=":")

lod.url_map.converters['rdf'] = RDFUrlConverter
lod.jinja_env.filters["term_to_string"]=term_to_string

LABEL_PROPERTIES=[rdflib.RDFS.label, 
                  rdflib.URIRef("http://purl.org/dc/elements/1.1/title"), 
                  rdflib.URIRef("http://xmlns.com/foaf/0.1/name"),
                  rdflib.URIRef("http://www.w3.org/2006/vcard/ns#fn"),
                  rdflib.URIRef("http://www.w3.org/2006/vcard/ns#org")
                  
                  ]

def resolve(r):
    """
    URL is the potentially local URL
    realurl is the one used in the data. 

    return {url, realurl, label}
    """
    if isinstance(r, rdflib.Literal): 
        return { 'url': None, 'realurl': None, 'label': get_label(r), 'lang': r.language }
        
    localurl=None
    if lod.config["types"]==[None]: 
        if (r, rdflib.RDF.type, None) in g.graph:
            localurl=url_for("resource", label=urllib2.unquote(localname(r)))
    else:
        for t in g.graph.objects(r,rdflib.RDF.type):
            if t in lod.config["types"]: 
                localurl=url_for("resource", type_=lod.config["types"][t], label=urllib2.unquote(localname(r)))
                break
    url=r
    if localurl: url=localurl
    return { 'url': url, 'realurl': r, 'label': get_label(r) }

def localname(t): 
    """qname computer is not quite what we want"""
    
    r=t[max(t.rfind("/"), t.rfind("#"))+1:]
    # pending apache 2.2.18 being available 
    # work around %2F encoding bug for AllowEncodedSlashes apache option
    r=r.replace("%2F", "_")
    return r

def get_label(t): 
    if isinstance(t, rdflib.Literal): return unicode(t)
    for l in lod.config["label_properties"]:
        try: 
            return g.graph.objects(t,l).next()
        except: 
            pass
    try: 
        #return g.graph.namespace_manager.compute_qname(t)[2]
        return urllib2.unquote(localname(t))
    except: 
        return t

def label_to_url(label):
    label=re.sub(re.compile('[^\w ]',re.U), '',label)
    return re.sub(" ", "_", label)

def detect_types(graph): 
    types={}
    types[rdflib.RDFS.Class]=localname(rdflib.RDFS.Class)
    types[rdflib.RDF.Property]=localname(rdflib.RDF.Property)
    for t in set(graph.objects(None, rdflib.RDF.type)):
        types[t]=localname(t)

    # make sure type triples are in graph
    for t in types: 
        graph.add((t, rdflib.RDF.type, rdflib.RDFS.Class))

    return types

def reverse_types(types): 
    rtypes={}
    for t,l in types.iteritems(): 
        while l in rtypes: 
            warnings.warn(u"Multiple types for label '%s': (%s) rewriting to '%s_'"%(l,rtypes[l], l))           
            l+="_"
        rtypes[l]=t
    return rtypes

            
def find_resources(graph): 
    resources=collections.defaultdict(dict)
    
    for t in lod.config["types"]: 
        resources[t]={}
        for x in graph.subjects(rdflib.RDF.type, t): 
            resources[t][x]=_quote(localname(x))

    #resources[rdflib.RDFS.Class]=lod.config["types"].copy()

    return resources

def reverse_resources(resources): 
    rresources={}
    for t,res in resources.iteritems(): 
        rresources[t]={}
        for r, l in res.iteritems():
            while l in rresources[t]: 
                warnings.warn(u"Multiple resources for label '%s': (%s) rewriting to '%s_'"%(repr(l),rresources[t][l], repr(l+'_')))           
                l+="_"
                
            rresources[t][l]=r

    return rresources


def _quote(l): 
    if isinstance(l,unicode): 
        l=l.encode("utf-8")
    return urllib2.quote(l, safe="")
        

def get_resource(label, type_): 
    label=_quote(label)
    if type_ and type_ not in lod.config["rtypes"]:
        return "No such type_ %s"%type_, 404
    try: 
        t=lod.config["rtypes"][type_]
        return lod.config["rresources"][t][label]

    except: 
        return "No such resource %s"%label, 404

@lod.route("/download/<format_>")
def download(format_):
    format_,mimetype_=mimeutils.format_to_mime(format_)
    response=make_response(g.graph.serialize(format=format_))

    response.headers["Content-Type"]=mimetype_

    return response        


@lod.route("/data/<type_>/<rdf:label>.<format_>")
@lod.route("/data/<rdf:label>.<format_>")
def data(label, format_, type_=None):
    r=get_resource(label, type_)
    if isinstance(r,tuple): # 404
        return r
    #graph=g.graph.query('DESCRIBE %s'%r.n3())
    # DESCRIBE <uri> is broken. 
    # http://code.google.com/p/rdfextras/issues/detail?id=25
    graph=g.graph.query('CONSTRUCT { %s ?p ?o . } WHERE { %s ?p ?o } '%(r.n3(), r.n3())).graph
    graph+=g.graph.query('CONSTRUCT { ?s ?p %s . } WHERE { ?s ?p %s } '%(r.n3(), r.n3()))

    format_,mimetype_=mimeutils.format_to_mime(format_)
    response=make_response(graph.serialize(format=format_))

    response.headers["Content-Type"]=mimetype_

    return response

@lod.route("/page/<type_>/<rdf:label>")
@lod.route("/page/<rdf:label>")
def page(label, type_=None):
    r=get_resource(label, type_)
    if isinstance(r,tuple): # 404
        return r

    outprops=sorted([ (resolve(x[0]), resolve(x[1])) for x in g.graph.predicate_objects(r) if x[0]!=rdflib.RDF.type])
    types=sorted([ resolve(x) for x in g.graph.objects(r,rdflib.RDF.type)])
    
    inprops=sorted([ (resolve(x[0]), resolve(x[1])) for x in g.graph.subject_predicates(r)])
    
    return render_template("lodpage.html", 
                           outprops=outprops, 
                           inprops=inprops, 
                           label=get_label(r),
                           urilabel=label,
                           graph=g.graph,
                           type_=type_, 
                           types=types,
                           resource=r)

@lod.route("/resource/<type_>/<rdf:label>")
@lod.route("/resource/<rdf:label>")
def resource(label, type_=None): 
    """
    Do ContentNegotiation for some resource and 
    redirect to the appropriate place
    """
    
    mimetype=mimeutils.best_match([mimeutils.RDFXML_MIME, mimeutils.N3_MIME, 
        mimeutils.NTRIPLES_MIME, mimeutils.HTML_MIME], request.headers["Accept"])
        
    if mimetype and mimetype!=mimeutils.HTML_MIME:
        path="data"
        ext="."+mimeutils.mime_to_format(mimetype)
    else:
        path="page"
        ext=""
        
    #print "label", label
    if type_:
        if ext!='' :
            url=url_for(path, type_=type_, label=label, format_=ext)
        else:
            url=url_for(path, type_=type_, label=label)
    else:
        if ext!='':
            url=url_for(path, label=label, format_=ext)
        else: 
            url=url_for(path, label=label)

    return redirect(url, 303)
        
        

@lod.route("/")
def index(): 
    types=sorted([resolve(x) for x in lod.config["types"]], key=lambda x: x['label'])
    resources={}
    for t in types:
        turl=t["realurl"]
        resources[turl]=sorted([resolve(x) for x in lod.config["resources"][turl]][:10], 
            key=lambda x: x.get('label'))
        if len(lod.config["resources"][turl])>10:
            resources[turl].append({ 'url': t["url"], 'label': "..." })
        t["count"]=len(lod.config["resources"][turl])
    
    return render_template("lodindex.html", 
                           types=types, 
                           resources=resources,
                           graph=g.graph)

##################

def serve(graph_,debug=False):
    get(graph_).run(debug=debug)


def get(graph, types='auto',image_patterns=["\.[png|jpg|gif]$"], 
        label_properties=LABEL_PROPERTIES, 
        hierarchy_properties=[ rdflib.RDFS.subClassOf, rdflib.RDFS.subPropertyOf ] ):

    lod.config["graph"]=graph
    lod.config["label_properties"]=label_properties
    lod.config["hierarchy_properties"]=hierarchy_properties
    
    if types=='auto':
        lod.config["types"]=detect_types(graph)
    elif types==None: 
        lod.config["types"]=[None]
    else: 
        lod.config["types"]=types

    lod.config["rtypes"]=reverse_types(lod.config["types"])

    lod.config["resources"]=find_resources(graph)
    lod.config["rresources"]=reverse_resources(lod.config["resources"])
    
    return lod

def format_from_filename(f):
    if f.endswith('n3'): return 'n3'
    if f.endswith('nt'): return 'nt'
    return 'xml'
    

if __name__=='__main__':
    import rdflib

    rdflib.plugin.register('sparql', rdflib.query.Processor,
                           'rdfextras.sparql.processor', 'Processor')
    rdflib.plugin.register('sparql', rdflib.query.Result,
                           'rdfextras.sparql.query', 'SPARQLQueryResult')

    rdflib.plugin.register('xml', rdflib.query.ResultParser, 
                           'rdfextras.sparql.results.xmlresults','XMLResultParser')
    rdflib.plugin.register('xml', rdflib.query.ResultSerializer, 
                           'rdfextras.sparql.results.xmlresults','XMLResultSerializer')

    rdflib.plugin.register('html', rdflib.query.ResultSerializer, 
                           'rdfextras.sparql.results.htmlresults','HTMLResultSerializer')

    rdflib.plugin.register('html', rdflib.serializer.Serializer, 
                           'rdfextras.sparql.results.htmlresults','HTMLSerializer')

    
    rdflib.plugin.register('json', rdflib.query.ResultParser, 
                           'rdfextras.sparql.results.jsonresults','JSONResultParser')
    rdflib.plugin.register('json', rdflib.query.ResultSerializer, 
                           'rdfextras.sparql.results.jsonresults','JSONResultSerializer')
    
    import sys, codecs
    if len(sys.argv)>1:
        gr=rdflib.Graph()
        for f in sys.argv[1:]:
            sys.stderr.write("Loading %s\n"%f)
            gr.load(f, format=format_from_filename(f))
    else:
        import bookdb
        gr=bookdb.bookdb
    
    serve(gr, True)
