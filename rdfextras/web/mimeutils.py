
try: 
    import mimeparse
except: 
    import warnings
    warnings.warn("mimeparse not found - I need this for content negotiation, install with 'easy_install mimeparse'")
    mimeparse=None
    
# sparql results
JSON_MIME="application/sparql-results+json"
XML_MIME="application/sparql-results+xml"

HTML_MIME="text/html"
N3_MIME="text/n3"
RDFXML_MIME="application/rdf+xml"
NTRIPLES_MIME="text/plain"

FORMAT_MIMETYPE={ "rdf": RDFXML_MIME, "n3": N3_MIME, "nt": NTRIPLES_MIME }
MIMETYPE_FORMAT=dict(map(reversed,FORMAT_MIMETYPE.items()))

def mime_to_format(mimetype): 
    if mimetype in MIMETYPE_FORMAT:
        return MIMETYPE_FORMAT[mimetype]
    return "rdf"
    
def format_to_mime(format): 
    if format in FORMAT_MIMETYPE:
        return format, FORMAT_MIMETYPE[format]
    return "xml", RDFXML_MIME
    
    

def resultformat_to_mime(format): 
    if format=='xml': return XML_MIME
    if format=='json': return JSON_MIME
    if format=='html': return HTML_MIME
    return "text/plain"
    
def best_match(cand, header): 
    if mimeparse:
        return mimeparse.best_match(cand,header)
    return None
