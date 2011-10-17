import pycurl
import json
import os
import time
from glob import glob
from StringIO import StringIO
from lxml import etree
from pprint import pprint, pformat
import urllib2

def curl_get(url):
    body = StringIO()
    header = StringIO()
    c = pycurl.Curl()
    c.setopt(pycurl.URL, url)
    c.setopt(pycurl.WRITEFUNCTION, body.write)
    c.setopt(pycurl.HEADERFUNCTION, header.write)
    c.setopt(pycurl.FOLLOWLOCATION, 1)
    c.setopt(pycurl.MAXREDIRS, 5)
    c.setopt(pycurl.HTTPHEADER, ["User-Agent: PyCurl",
                                 "Accept: application/sparql-results+json, */*;q=0.5",
                                 "Content-Type: application/sparql-query"])
    c.perform()
    status = c.getinfo(c.HTTP_CODE)
    c.close()
    return status, body, header

def sesame():
    baseuri = "http://localhost:8080/openrdf-sesame/repositories/spb2?"
    ql="&amp;queryLn=SPARQL"
    query= "query=%s"
    limit="&amp;limit=10"
    infer="&amp;infer=false"
    if 'sp2b' not in os.getcwd():
        os.chdir('/Users/httpd/Python/SemWeb/rdfextras-working/test/sp2b')
    for idx, testFile in enumerate(glob('queries/*.sparql')):
        q = open(testFile).read()
        uri = baseuri+(''.join([query % urllib2.quote(q), limit, infer, ql]))
        t1 = time.time()
        status, body, header = curl_get(uri)
        t2 = time.time()
        if status == 200:
            res = json.loads(body.getvalue())
            if res in (True, False):
                results = [res] if res else []
            else:
                results = res[u'results'][u'bindings']
            print("Q%s\t%s\t%f" % (testFile[9:-7], len(results), t2-t1))
        else:
            print("Q%s\t%s\t%f" % (testFile[9:-7], 'X', 'X'))
    

sesame()

def readres(s):
    res = etree.parse(StringIO(s.replace('&nbsp;',' ')),
                     etree.HTMLParser(encoding='utf-8')).xpath('//boolean')
    if res:
        return {'true':True, 'false':False}[res[0].text]
    else:
        res = etree.parse(StringIO(s.replace('&nbsp;',' ')),
                         etree.HTMLParser(encoding='utf-8')).xpath('//binding')
        return res
    # title = u''+div[0].xpath('./h2')[0].text.strip()
    # composition = [u''+x.text.strip() for x in div[0].xpath('./ul/li')]
    # terms_of_reference = u''+div[0].xpath('./p')[0].text.strip()
    # return title, composition, terms_of_reference.encode('iso-8859-1', 'ignore')

def mulgara():
    baseuri = "http://localhost:8080/mulgara/sparql?"
    format="&amp;format=json"
    query= "query=%s"
    if 'sp2b' not in os.getcwd():
        os.chdir('/Users/httpd/Python/RDF/rdflib/rdfextras-working/test/sp2b')
    for idx, testFile in enumerate(glob('queries/*.sparql')): #[40:50]):
        q = open(testFile).read()
        uri = baseuri+(''.join([query % urllib2.quote(q), format]))
        t1 = time.time()
        status, body, header = curl_get(uri)
        t2 = time.time()
        if status == 200:
            res = body.getvalue()
            # print("Result %s" % res)
            res = readres(res)
            if not isinstance(res, list):
                if res:
                    res = [res]
                else:
                    res = []
            print("Q%s\t%s\t%f" % (testFile[9:-7], len(res), t2-t1))
        else:
            print("Failed %s %s" % (status, body.getvalue()))
    

# mulgara()

def joseki():
    baseuri = "http://localhost:8080/joseki/sp2b?"
    # dgu = "&amp;default-graph-uri=sp2b"
    ss = "&amp;stylesheet=%2Fxml-to-html.xsl"
    output="&output=json"
    query= "query=%s"
    if 'sp2b' not in os.getcwd():
        os.chdir('/Users/httpd/Python/RDF/rdflib/rdfextras-working/test/sp2b')
    for idx, testFile in enumerate(glob('queries/*.sparql')): #[40:50]):
        q = open(testFile).read()
        uri = baseuri+(''.join([query % urllib2.quote(q), ss, output]))
        t1 = time.time()
        status, body, header = curl_get(uri)
        t2 = time.time()
        if status == 200:
            # print(body.getvalue())
            res = json.loads(body.getvalue())
            if res in (True, False):
                results = [res]
            elif  "boolean" in res:
                # print(res)
                results = [True] if res['boolean'] else []
            else:
                # vars = res[u'head'][u'vars']
                results = res[u'results'][u'bindings']
            print("Q%s\t%s\t%f" % (testFile[9:-7], len(results), t2-t1))
        else:
            print("Failed %s %s" % (status, body.getvalue()))
    
# gort()
