from flask import Flask, render_template, request, make_response, Markup
endpoint = Flask(__name__)

graph=None

JSON_MIME="application/sparql-results+json"
XML_MIME="application/sparql-results+xml"
HTML_MIME="text/html"
N3_MIME="text/plain"
RDFXML_MIME="application/rdf+xml"

def formatToMime(format): 
    if format=='xml': return XML_MIME
    if format=='json': return JSON_MIME
    if format=='html': return HTML_MIME
    return "text/plain"

@endpoint.route("/sparql", methods=['GET', 'POST'])
def query():
    q=request.values["query"]
    
    a=request.headers["Accept"]
    
    format="xml" # xml is default
    if HTML_MIME in a:
        format="html"
    if JSON_MIME in a: 
        format="json"

    # output parameter overrides header
    format=request.values.get("output", format) 

    mimetype=formatToMime(format)
    
    # force-accept parameter overrides mimetype
    mimetype=request.values.get("force-accept", mimetype)

    # pretty=None
    # if "force-accept" in request.values: 
    #     pretty=True

    # default-graph-uri

    results=graph.query(q).serialize(format=format)
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
    global graph 
    graph=graph_
    endpoint.run(debug=debug)

def get(graph_):
    global graph
    graph=graph_
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
