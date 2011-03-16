import re
import rdflib
import warnings

from endpoint import endpoint as lod

from flask import render_template, request, make_response, redirect, url_for

import mimeutils 

from rdfextras.sparql.results.htmlresults import term_to_string

lod.jinja_env.filters["term_to_string"]=term_to_string

LABEL_PROPERTIES=[rdflib.RDFS.label, 
                  rdflib.URIRef("http://purl.org/dc/elements/1.1/title"), 
                  rdflib.URIRef("http://xmlns.com/foaf/0.1/name"),
                  rdflib.URIRef("http://www.w3.org/2006/vcard/ns#fn"),
                  rdflib.URIRef("http://www.w3.org/2006/vcard/ns#org")
                  
                  ]

def resolve(r):
    """
    return (realurl, localurl, label)
    """
    if isinstance(r, rdflib.Literal): 
        return { 'url': None, 'realurl': None, 'localurl': None, 'label': get_label(r) }
        
    localurl=None
    if lod.config["types"]==[None]: 
        if (r, rdflib.RDF.type, None) in lod.config["graph"]:
            localurl="/%s"%label_to_url(r)
    else:
        for t in lod.config["graph"].objects(r,rdflib.RDF.type):
            if t in lod.config["types"]: 
                localurl=url_for("resource", type_=lod.config["types"][t], label=label_to_url(get_label(r)))
                break
    url=r
    if localurl: url=localurl
    return { 'url': url, 'realurl': r, 'localurl': url, 'label': get_label(r) }

def get_label(t): 
    if isinstance(t, rdflib.Literal): return unicode(t)
    for l in lod.config["label_properties"]:
        try: 
            return lod.config["graph"].objects(t,l).next()
        except: 
            pass
    try: 
        return lod.config["graph"].namespace_manager.compute_qname(t)[2]
    except: 
        return t

def label_to_url(label):
    label=re.sub(re.compile('[^\w ]',re.U), '',label)
    return re.sub(" ", "_", label)

def detect_types(graph): 
    types={}
    for t in set(graph.objects(None, rdflib.RDF.type)):
        types[t]=label_to_url(get_label(t))

    return types

def reverse_types(types): 
    rtypes={}
    for t,l in types.iteritems(): 
        while l in rtypes: 
            warnings.warn(u"Multiple types for label '%s': (%s) rewriting to '%s_'"%(l,rtypes[l], l))           
            l+="_"
        rtypes[l]=t
    return rtypes

            
def find_resources(): 
    resources={}
    graph=lod.config["graph"]

    for t in lod.config["types"]: 
        resources[t]={}
        for x in graph.subjects(rdflib.RDF.type, t): 
            resources[t][x]=label_to_url(get_label(x))
            
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



def get_resource(label, type_): 
    if type_ and type_ not in lod.config["rtypes"]:
        return "No such type_ %s"%type_, 404
    try: 
        t=lod.config["rtypes"][type_]
        return lod.config["rresources"][t][label]

    except: 
        return "No such resource %s"%label, 404



@lod.route("/data/<type_>/<label>.<format>")
@lod.route("/data/<label>.<format>")
def data(label, format, type_=None):
    r=get_resource(label, type_)
    if isinstance(r,tuple): # 404
        return r
    graph=lod.config["graph"].query('DESCRIBE %s'%r.n3())
    format,mimetype_=mimeutils.format_to_mime(format)
    response=make_response(graph.serialize(format=format))

    response.headers["Content-Type_"]=mimetype_

    return response

@lod.route("/page/<type_>/<label>")
@lod.route("/page/<label>")
def page(label, type_=None):
    r=get_resource(label, type_)
    if isinstance(r,tuple): # 404
        return r

    outprops=sorted([ (resolve(x[0]), resolve(x[1])) for x in lod.config["graph"].predicate_objects(r) 
               if x[0]!=rdflib.RDF.type])
    types=sorted([ resolve(x) for x in lod.config["graph"].objects(r,rdflib.RDF.type)])
    
    inprops=sorted([ (resolve(x[0]), resolve(x[1])) for x in lod.config["graph"].subject_predicates(r)])
    
    return render_template("lodpage.html", 
                           outprops=outprops, 
                           inprops=inprops, 
                           label=get_label(r), 
                           graph=lod.config["graph"],
                           type_=type_, 
                           types=types,
                           resource=r)

@lod.route("/resource/<type_>/<label>")
@lod.route("/resource/<label>")
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

    if type_:
        if ext!='' :
            url=url_for(path, type_=type_, label=label, format=ext)
        else:
            url=url_for(path, type_=type_, label=label)
    else:
        if ext!='':
            url=url_for(path, label=label, format=ext)
        else: 
            url=url_for(path, label=label)

    return redirect(url, 303)
        
        

@lod.route("/")
def index(): 
    types=sorted([resolve(x) for x in lod.config["types"]], key=lambda x: x['label'])
    resources={}
    for t in lod.config["types"]:
        resources[t]=sorted([resolve(x) for x in lod.config["resources"][t]], 
            key=lambda x: x.get('label'))
    
    
    return render_template("lodindex.html", 
                           types=types, 
                           resources=resources,
                           graph=lod.config["graph"])

##################

def serve(graph_,debug=False):
    get(graph_).run(debug=debug)

def get(graph_, types='auto',image_patterns=["\.[png|jpg|gif]$"], label_properties=LABEL_PROPERTIES):

    lod.config["graph"]=graph_
    lod.config["label_properties"]=label_properties
    
    if types=='auto':
        lod.config["types"]=detect_types(graph_)
    elif types==None: 
        lod.config["types"]=[None]
    else: 
        lod.config["types"]=types

    lod.config["rtypes"]=reverse_types(lod.config["types"])

    lod.config["resources"]=find_resources()
    lod.config["rresources"]=reverse_resources(lod.config["resources"])
    
    return lod

def format_from_filename(f):
    if f.endswith('n3'): return 'n3'
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
        g=rdflib.Graph()
        g.load(sys.argv[1], format=format_from_filename(sys.argv[1]))
    else:
        import bookdb
        g=bookdb.bookdb
    
    serve(g, True)
