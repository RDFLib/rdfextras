try:
    from flask import Flask, render_template, request, make_response, Markup
except:
    raise Exception("Flask not found - install with 'easy_install flask'")

import rdflib
import rdfextras
import sys

import mimeutils

endpoint = Flask(__name__)

endpoint.jinja_env.globals["rdflib_version"]=rdflib.__version__
endpoint.jinja_env.globals["rdfextras_version"]=rdfextras.__version__
endpoint.jinja_env.globals["python_version"]=sys.version


@endpoint.route("/sparql", methods=['GET', 'POST'])
def query():
    q=request.values["query"]
    
    a=request.headers["Accept"]
    
    format="xml" # xml is default
    if mimeutils.HTML_MIME in a:
        format="html"
    if mimeutils.JSON_MIME in a: 
        format="json"

    # output parameter overrides header
    format=request.values.get("output", format) 

    mimetype=mimeutils.resultformat_to_mime(format)
    
    # force-accept parameter overrides mimetype
    mimetype=request.values.get("force-accept", mimetype)

    # pretty=None
    # if "force-accept" in request.values: 
    #     pretty=True

    # default-graph-uri

    results=endpoint.config["graph"].query(q).serialize(format=format)
    if format=='html':
        response=make_response(render_template("results.html", results=Markup(results), q=q))
    else:
        response=make_response(results)

    response.headers["Content-Type"]=mimetype
    return response


@endpoint.route("/")
def index():
    return render_template("index.html")

def serve(graph_,debug=False):
    get(graph_).run(debug=debug)

def get(graph_):
    endpoint.config["graph"]=graph_
    return endpoint

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
