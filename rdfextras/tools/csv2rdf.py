import sys
import re
import csv
import getopt
import ConfigParser
import fileinput
import codecs
import time
import datetime
import warnings
import urllib2

import rdflib

from rdflib import RDF, RDFS


HELP="""
toRDF.py -b <instance-base> -p <property-base> [-c <classname>] [-i <identity column(s)>] [-l <label columns>] [-s <N>] [-o <output>] [-f configfile] [--col<N> <colspec>] [--prop<N> <property>] <[-d <delim>] [-C] [files...]"

Reads csv files from stdin or given files
if -d is given, use this delimiter
if -s is given, skips N lines at the start
Creates a URI from the columns given to -i, or automatically by numbering if none is given
Outputs RDFS labels from the columns given to -l
if -c is given adds a type triple with the given classname 
if -C is given, the class is defined as rdfs:Class
Outputs one RDF triple per column in each row. 
Output is in n3 format. 
Output is stdout, unless -o is specified

Long options also supported: --base, --propbase, --ident, --class, --label, --out, --defineclass

Long options --col0, --col1, ... can be used to specify conversion for columns. Conversions can be: float(), int(), split(sep, [more]), uri(base, [class]), date(format) 

Long options --prop0, --prop1, ... can be used to use specific properties, rather than ones auto-generated from the headers

-f says to read config from a .ini/config file - the file must contain one section called csv2rdf, with keys like the long options, i.e.: 

[csv2rdf]
out=output.n3
base=http://example.org/
col0=split(";")
col1=split(";", uri("http://example.org/things/","http://xmlns.com/foaf/0.1/Person"))
col2=float()
col3=int()
col4=date("%Y-%b-%d %H:%M:%S")





"""

# bah - ugly global
uris={}


def toProperty(label): 
    """
    CamelCase + lowercase inital a string
    

    FIRST_NM => firstNm

    firstNm => firstNm

    """
    label=re.sub("[^\w]"," ",label)
    label=re.sub("([a-z])([A-Z])", "\\1 \\2", label)
    label=label.split(" ")
    return "".join([label[0].lower()]+[x.capitalize() for x in label[1:]])

def index(l, i): 
    """return a set of indexes from a list
    >>> index([1,2,3],(0,2))
    (1, 3)
    """
    return tuple([l[x] for x in i])

def csv_reader(csv_data, dialect=csv.excel, **kwargs):

    csv_reader = csv.reader(csv_data,
                            dialect=dialect, **kwargs)
    for row in csv_reader:
        # decode UTF-8 back to Unicode, cell by cell:
        yield [unicode(cell, 'utf-8', errors='replace') for cell in row]

def prefixuri(x, prefix, class_=None):
    if prefix: 
        r=rdflib.URIRef(prefix+urllib2.quote(x.encode("utf8").replace(" ", "_"), safe=""))
    else: 
        r=rdflib.URIRef(x)
    uris[x]=(r, class_)
    return r

# meta-language for config
def _config_ignore(**args): 
    return "ignore"

def _config_uri(prefix=None, class_=None): 
    return lambda x: prefixuri(x, prefix, class_)

def _config_literal(): 
    return rdflib.Literal

def _config_float(f=None): 
    if not f: 
        return lambda x: rdflib.Literal(float(x))
    if callable(f): 
        return lambda x: rdflib.Literal(float(f(x)))
    raise Exception("Function passed to float is not callable")


def _config_replace(a, b): 
    return lambda x: x.replace(a,b)

def _config_int(f=None): 
    if not f: 
        return lambda x: rdflib.Literal(int(x))
    if callable(f): 
        return lambda x: rdflib.Literal(int(f(x)))
    raise Exception("Function passed to int is not callable")

def _config_date(format_): 
    return lambda x: rdflib.Literal(datetime.datetime.strptime(x,format_))

def _config_split(sep=None, f=None):
    if not f: f=rdflib.Literal
    if not callable(f): raise Exception("Function passed to split is not callable!")
    return lambda x: [f(y.strip()) for y in x.split(sep) if y.strip()!=""]

config_functions={ "ignore": _config_ignore, 
                   "uri": _config_uri, 
                   "literal": _config_literal,
                   "float": _config_float, 
                   "int": _config_int,
                   "date": _config_date,
                   "split": _config_split,
                   "replace": _config_replace
                   }

def column(v):
    """Return a function for column mapping"""
    
    return eval(v, config_functions)
    

class CSV2RDF(object): 
    def __init__(self): 

        self.CLASS=None
        self.BASE=None
        self.PROPBASE=None
        self.IDENT='auto'
        self.LABEL=None
        self.DEFINECLASS=False
        self.SKIP=0
        self.DELIM=","

        self.COLUMNS={}
        self.PROPS={}

        self.OUT=codecs.getwriter("utf-8")(sys.stdout, errors='replace')
    
        self.triples=0

    def triple(self, s,p,o):
        self.OUT.write("%s %s %s .\n"%(s.n3(), p.n3(), o.n3()))
        self.triples+=1

    def convert(self, csvreader): 

        start=time.time()

        if self.OUT:
            sys.stderr.write("Output to %s\n"%self.OUT.name)

        if self.IDENT!="auto" and not isinstance(self.IDENT, tuple): 
            self.IDENT=(self.IDENT,)

        if not self.BASE: 
            warnings.warn("No base given, using http://example.org/instances/")
            self.BASE=rdflib.Namespace("http://example.org/instances/")

        if not self.PROPBASE:
            warnings.warn("No property base given, using http://example.org/property/")
            self.PROPBASE=rdflib.Namespace("http://example.org/props/")

        if self.DEFINECLASS:
            self.triple(self.CLASS, RDF.type, RDFS.Class)

        # skip lines at the start
        for x in range(self.SKIP): csvreader.next()

        # read header line
        headers=dict(enumerate([self.PROPBASE[toProperty(x)] for x in csvreader.next()]))
        # override header properties if some are given
        for k,v in self.PROPS.iteritems():
            headers[k]=v

        rows=0
        for l in csvreader:
            try: 
                if self.IDENT=='auto': 
                    uri=self.BASE["%d"%rows]
                else:
                    uri=self.BASE["_".join([urllib2.quote(x.encode("utf8").replace(" ", "_"), safe="") for x in index(l, self.IDENT)])]

                if self.LABEL: 
                    self.triple(uri, RDFS.label, rdflib.Literal(" ".join(index(l, self.LABEL))))

                if self.CLASS:
                    # type triple
                    self.triple(uri, RDF.type, self.CLASS)


                for i,x in enumerate(l):        
                    x=x.strip()
                    if x!='': 
                        if self.COLUMNS.get(i)=="ignore": continue
                        try: 
                            o=self.COLUMNS.get(i, rdflib.Literal)(x)
                            if isinstance(o, list): 
                                for _o in o: self.triple(uri, headers[i], _o)
                            else: 
                                self.triple(uri, headers[i], o)

                        except Exception, e:
                            warnings.warn("Could not process value for column %d:%s in row %d, ignoring: %s "%(i,headers[i],rows, e.message))

                rows+=1
                if rows % 100000 == 0 : 
                    sys.stderr.write("%d rows, %d triples, elapsed %.2fs.\n"%(rows, self.triples, time.time()-start))
            except: 
                sys.stderr.write("Error processing line: %d\n"%rows)
                raise

        # output types/labels for generated URIs
        classes=set()
        for l,x in uris.iteritems(): 
            u,c=x
            self.triple(u, RDFS.label, rdflib.Literal(l))
            if c: 
                c=rdflib.URIRef(c)
                classes.add(c)
                self.triple(u, RDF.type, c)

        for c in classes:
            self.triple(c, RDF.type, RDFS.Class)


        self.OUT.close()
        sys.stderr.write("Converted %d rows into %d triples.\n"%(rows, self.triples))
        sys.stderr.write("Took %.2f seconds.\n"%(time.time()-start))

                        

if __name__=='__main__':


    csv2rdf=CSV2RDF()
    
    opts,files=getopt.getopt(sys.argv[1:], 
                             "hc:b:p:i:o:Cf:l:s:d:", 
                             ["out=","base=","delim=", "propbase=","class=","ident=", "label=", "skip=", "defineclass","help"])
    opts=dict(opts)

    if "-h" in opts or "--help" in opts:
        print HELP
        sys.exit(-1)

    if "-f" in opts: 
        config = ConfigParser.ConfigParser()
        config.readfp(open(opts["-f"]))
        for k,v in config.items("csv2rdf"): 
            if k=="out":
                csv2rdf.OUT=codecs.open(v, "w", "utf-8")
            elif k=="base": 
                csv2rdf.BASE=rdflib.Namespace(v)
            elif k=="propbase":
                csv2rdf.PROPBASE=rdflib.Namespace(v)
            elif k=="class": 
                csv2rdf.CLASS=rdflib.URIRef(v)
            elif k=="defineclass":
                csv2rdf.DEFINECLASS=bool(v)
            elif k=="ident": 
                csv2rdf.IDENT=eval(v)
            elif k=="label":
                csv2rdf.LABEL=eval(v)
            elif k=="delim": 
                csv2rdf.DELIM=v
            elif k=="skip": 
                csv2rdf.SKIP=int(v)
            elif k.startswith("col"):
                csv2rdf.COLUMNS[int(k[3:])]=column(v)
            elif k.startswith("prop"):
                csv2rdf.PROPS[int(k[4:])]=rdflib.URIRef(v)
                
    if "-o" in opts: 
        csv2rdf.OUT=codecs.open(opts["-o"], "w", "utf-8")
    if "--out" in opts: 
        csv2rdf.OUT=codecs.open(opts["--out"], "w", "utf-8")

    if "-b" in opts:
        csv2rdf.BASE=rdflib.Namespace(opts["-b"])
    if "--base" in opts:
        csv2rdf.BASE=rdflib.Namespace(opts["--base"])

    if "-d" in opts: 
        csv2rdf.DELIM=opts["-d"]
    if "--delim" in opts: 
        csv2rdf.DELIM=opts["--delim"]

    if "-p" in opts: 
        csv2rdf.PROPBASE=rdflib.Namespace(opts["-p"])
    if "--propbase" in opts:
        csv2rdf.PROPBASE=rdflib.Namespace(opts["--propbase"])

    if "-l" in opts: 
        csv2rdf.LABEL=eval(opts["-l"])
    if "--label" in opts: 
        csv2rdf.LABEL=eval(opts["--label"])

    if "-i" in opts: 
        csv2rdf.IDENT=eval(opts["-i"])        
    if "--ident" in opts: 
        csv2rdf.IDENT=eval(opts["--ident"])

    if "-s" in opts: 
        csv2rdf.SKIP=int(opts["-s"])
    if "--skip" in opts: 
        csv2rdf.SKIP=int(opts["--skip"])

    if "-c" in opts:
        csv2rdf.CLASS=rdflib.URIRef(opts["-c"])
    if "--class" in opts: 
        csv2rdf.CLASS=rdflib.URIRef(opts["--class"])

    for k,v in opts.iteritems(): 
        if k.startswith("--col"):
            csv2rdf.COLUMNS[int(k[5:])]=column(v)
        elif k.startswith("--prop"):
            csv2rdf.PROPS[int(k[6:])]=rdflib.URIRef(v)            

    if csv2rdf.CLASS and ( "-C" in opts or "--defineclass" in opts ): 
        csv2rdf.DEFINECLASS=True
        
    csv2rdf.convert(csv_reader(fileinput.input(files), delimiter=csv2rdf.DELIM))



