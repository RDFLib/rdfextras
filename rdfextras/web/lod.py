import re
import rdflib
import warnings

from endpoint import endpoint as lod
import endpoint

from flask import render_template, request, make_response, redirect

from rdfextras.sparql.results.htmlresults import term_to_string

lod.jinja_env.filters["term_to_string"]=term_to_string

LABEL_PROPERTIES=[rdflib.RDFS.label, 
                  rdflib.URIRef("http://purl.org/dc/elements/1.1/title"), 
                  rdflib.URIRef("http://xmlns.com/foaf/0.1/name")]

def get_label(t): 
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
            warnings.warn("Multiple types for label '%s': (%s) rewriting to '%s_'"%(l,rtypes[l], l))           
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
                warnings.warn("Multiple resources for label '%s': (%s) rewriting to '%s_'"%(l,rresources[t][l], l))           
                l+="_"
            rresources[t][l]=r

    return rresources



def format_to_mime(format): 
    if format=="rdf": return format, endpoint.RDFXML_MIME
    if format=="n3": return format, endpoint.N3_MIME
    if format=="nt": return format, endpoint.NTRIPLES_MIME

    return "rdf", endpoint.RDFXML_MIME

def get_resource(label, type_): 
    if type_ and type_ not in lod.config["rtypes"]:
        return "No such type_ %s"%type_, 404
    try: 
        t=lod.config["rtypes"][type_]
        print lod.config["rresources"][t], label
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
    format,mimetype_=format_to_mime(format)
    response=make_response(graph.serialize(format=format))

    response.headers["Content-Type_"]=mimetype_

    return response

@lod.route("/page/<type_>/<label>")
@lod.route("/page/<label>")
def page(label, type_=None):
    r=get_resource(label, type_)
    if isinstance(r,tuple): # 404
        return r

    outprops=list(lod.config["graph"].predicate_objects(r))
    inprops=list(lod.config["graph"].subject_predicates(r))

    return render_template("lodpage.html", 
                           outprops=outprops, 
                           inprops=inprops, 
                           label=label, 
                           graph=lod.config["graph"],
                           type_=type_, 
                           resource=r)

@lod.route("/resource/<type_>/<label>")
@lod.route("/resource/<label>")
def resource(label, type_=None): 
    if type_:
        return redirect("/page/%s/%s"%(type_,label),303)
    else:
        return redirect("/page/%s"%label,303)
        

@lod.route("/")
def index(): 
    return render_template("lodindex.html", 
                           types=lod.config["types"], 
                           resources=lod.config["resources"],
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
    import bookdb
    g=bookdb.bookdb
    
    serve(g, True)
