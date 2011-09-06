# -*- coding: utf-8 -*-
# epydoc
#
"""
:var JSON: to be used to set the return format to JSON
:var XML: to be used to set the return format to XML (SPARQL XML format or 
    RDF/XML, depending on the query type). This is the default.
:var TURTLE: to be used to set the return format to Turtle
:var N3: to be used to set the return format to N3 (for most of the SPARQL
    services this is equivalent to Turtle)

:var POST: to be used to set HTTP POST
:var GET: to be used to set HTTP GET. This is the default.

:var SELECT: to be used to set the query type to SELECT. This is, usually, 
    determined automatically.
:var CONSTRUCT: to be used to set the query type to CONSTRUCT. This is, 
    usually, determined automatically.
:var ASK: to be used to set the query type to ASK. This is, usually, 
    determined automatically.
:var DESCRIBE: to be used to set the query type to DESCRIBE. This is, 
    usually, determined automatically.

:see: `SPARQL Specification <http://www.w3.org/TR/rdf-sparql-query/>`_
:authors: U{Ivan Herman<http://www.ivan-herman.net">}, U{Sergio Fernández<http://www.wikier.org">}, U{Carlos Tejo Alonso<http://www.dayures.net>}
:organization: U{World Wide Web Consortium<http://www.w3.org>} and U{Foundation CTIC<http://www.fundacionctic.org/>}.
:license: U{W3C® SOFTWARE NOTICE AND LICENSE<href="http://www.w3.org/Consortium/Legal/2002/copyright-software-20021231">}
:requires: U{simplejson<http://cheeseshop.python.org/pypi/simplejson>} package.
:requires: U{PyXML<http://pyxml.sourceforge.net/>} package.
:requires: U{RDFLib<http://rdflib.net>} package.

"""
import urllib, urllib2
import re

MEANINGLESS_URI = 'tag:nobody@nowhere:2007:meaninglessURI'
BNODE_IDENT_PATTERN = re.compile('(?P<label>_\:[^\s]+)')

#  Possible output format keys...
JSON   = "json"
XML    = "xml"
TURTLE = "n3"
N3     = "n3"
_allowedFormats = [JSON, XML, TURTLE, N3]

# Possible HTTP methods
POST = "POST"
GET  = "GET"
_allowedRequests = [POST, GET]

# Possible SPARQL query type
SELECT     = "SELECT"
CONSTRUCT  = "CONSTRUCT"
ASK        = "ASK"
DESCRIBE   = "DESCRIBE"
_allowedQueryTypes = [SELECT, CONSTRUCT, ASK, DESCRIBE]

# Possible output format (mime types) that can be converted by the local 
# script. Unfortunately, it does not work by simply setting the return format,
# because there is still a certain level of confusion among implementations.

# For example, Joseki returns application/javascript and not the
# sparql-results+json thing that is required... i.e, alternatives should be
# given... Andy Seaborne told me (June 2007) that the right return format is 
# now added to his CVS, ie, future releases of joseki will be o.k., too. The
# situation with turtle and n3 is even more confusing because the text/n3 and
# text/turtle mime types have just been proposed and not yet widely used...

_SPARQL_DEFAULT  = ["application/sparql-results+xml", 
                            "application/rdf+xml", "*/*"]
_SPARQL_XML      = ["application/sparql-results+xml"]
_SPARQL_JSON     = ["application/sparql-results+json", "text/javascript"]
_RDF_XML         = ["application/rdf+xml"]
_RDF_N3          = ["text/rdf+n3",
                    "application/n-triples","application/turtle",
                    "application/n3","text/n3","text/turtle"]
_ALL             = ["*/*"]
_RDF_POSSIBLE    = _RDF_XML + _RDF_N3
_SPARQL_POSSIBLE = _SPARQL_XML + _SPARQL_JSON + _RDF_XML + _RDF_N3

# This is very ugly. The fact is that the key for the choice of the output
# format is not defined. Virtuoso uses 'format', joseki uses 'output', rasqual
# seems to use "results"

# Lee Feigenbaum told me that virtuoso also understand 'output' these days, so I
# removed 'format'. I do not have info about the others yet, ie, for the time
# being I keep the general mechanism. Hopefully, in a future release, I can get
# rid of that. However, these processors are (hopefully) oblivious to the
# parameters they do not understand. So: just repeat all possibilities in the
# final URI. UGLY!!!!!!!

_returnFormatSetting = ["output","results"]

##############################################################################
class SPARQLWrapper :
    """
    Wrapper around an online access to a SPARQL Web entry point.
    
    The same class instance can be reused for subsequent queries. The values
    of the base Graph URI, return formats, etc, are retained from one query to
    the next (in other words, only the query string changes). The instance can
    also be reset to its initial values using the ``resetQuery`` method.
    
    :cvar pattern: regular expression used to determine whether a query is of
        type ``CONSTRUCT``, ``SELECT``, ``ASK``, or ``DESCRIBE``.
    :type pattern: compiled regular expression (see the Python ``re`` module)
    :ivar baseURI: the URI of the SPARQL service
    """
    pattern = re.compile(r"""
                (?P<base>(\s*BASE\s*[<].*[>])\s*)*
                (?P<prefixes>(\s*PREFIX\s*.*[:]\s*[<].*[>])\s*)*
                (?P<queryType>(CONSTRUCT|SELECT|ASK|DESCRIBE))""", 
                    re.VERBOSE | re.IGNORECASE)
    
    def __init__(self,baseURI,returnFormat=XML,defaultGraph=None) :
        """
        Class encapsulating a full SPARQL call.
        :param baseURI: string of the SPARQL endpoint's URI
        :type baseURI: string
        :keyword returnFormat: Default: ``XML``.
            Can be set to JSON or Turtle/N3
        
        No local check is done, the parameter is simply sent to the endpoint.
        Eg, if the value is set to JSON and a construct query is issued, it is
        up to the endpoint to react or not, this wrapper does not check.
        
        Possible values:
        ``JSON``, ``XML``, ``TURTLE``, ``N3` (constants in this module). The 
            value can also be set via explicit call, see below.
        :type returnFormat: string
        :keyword defaultGraph: URI for the default graph. Default is None, the
            value can be set either via an explicit call to 
            ``addDefaultGraph`` or as part of the query string.
        :type defaultGraph: string
        """
        self.debug       = False
        self.nsBindings  = {}
        self.baseURI     = baseURI
        self._querytext  = []
        self._defaultGraph = defaultGraph
        if defaultGraph : self._querytext.append(
                                ("default-graph-uri",defaultGraph))
        if returnFormat in _allowedFormats :
            self.returnFormat = returnFormat
        else :
            self.returnFormat = XML
        self._defaultReturnFormat = self.returnFormat
        self.queryString = """SELECT * WHERE{ ?s ?p ?o }"""
        self.method    = GET
        self.queryType = SELECT
    
    def resetQuery(self) :
        """Reset the query, ie, return format, query, default or named graph
        settings, etc, are reset to their default values."""
        self._querytext = []
        if self._defaultGraph : self._querytext.append(
                                ("default-graph-uri",self._defaultGraph))
        self.returnFormat = self._defaultReturnFormat
        self.method    = GET
        self.queryType = SELECT
        self.queryString = """SELECT * WHERE{ ?s ?p ?o }"""
    
    def setReturnFormat(self,format) :
        """Set the return format. If not an allowed value, the setting is
        ignored.
        
        :param format: Possible values: are ``JSON``, ``XML``, ``TURTLE``, 
            ``N3`` (constants in this module). All other cases are ignored.
        :type format: string
        """
        if format in _allowedFormats :
            self.returnFormat = format
    
    def addDefaultGraph(self,uri) :
        """Add a default graph URI.
        
        :param uri: URI of the graph
        :type uri: string
        """
        if uri :
            self._querytext.append(("default-graph-uri",uri))
    
    def addNamedGraph(self,uri) :
        """Add a named graph URI.
       
       :param uri: URI of the graph
       :type uri: string
        """
        if uri :
            self._querytext.append(("named-graph-uri",uri))
    
    def addExtraURITag(self,key,value):
        """Some SPARQL endpoints require extra key value pairs.
        E.g., in virtuoso, one would add C{should-sponge=soft} to the query
        forcing virtuoso to retrieve graphs that are not stored in its local
        database.
        :param key: key of the query part
        :type key: string
        :param value: value of the query part
        :type value: string
        """
        self._querytext.append((key,value))
    
    def setNamespaceBindings(self,bindings) :
        """A shortcut for setting namespace bindings that will be added to the
        prolog of the query
        :param bindings: A dictionary of prefixs to URIs
        """
        self.nsBindings.update(bindings)
    
    def setQuery(self,query) :
        """Set the SPARQL query text. Note: no check is done on the validity
        of the query (syntax or otherwise) by this module, except for testing
        the query type (SELECT, ASK, etc). Syntax and validity checking is
        done by the SPARQL service itself.
        :param query: query text
        :type query: string
        """
        if self.bNodeAsURI:
            query = re.sub(BNODE_IDENT_PATTERN,'<\g<label>>',query)
        self.queryString = '\n'.join(['\n'.join(['PREFIX %s: <%s>'%(key,val)
                                    for key,val in self.nsBindings.items()]),
                                 query])
        if self.debug:
            print self.queryString
        self.queryType   = self._parseQueryType(query)
    
    def _parseQueryType(self,query) :
        """Parse the SPARQL query and return its type (ie, ``SELECT``, 
            ``ASK``, etc).
        
        Note that the method returns ``SELECT`` if nothing is specified. This
        is just to get all other methods running; in fact, this means that the
        query is erronous, because the query must be, according to the SPARQL
        specification, one of Select, Ask, Describe, or Construct. The SPARQL
        endpoint should raise an exception (via urllib) for such syntax error.
        
        :param query: query text
        :type query: string
        :rtype: string
        """
        r_queryType = self.pattern.search(query).group("queryType").upper()
        
        if r_queryType in _allowedQueryTypes :
            return r_queryType
        else :
            # raise Exception("Illegal SPARQL Query; must be one of" + \
            #                         "SELECT, ASK, DESCRIBE, or CONSTRUCT")
            return SELECT
    
    def setMethod(self,method) :
        """Set the invocation method. By default, this is L{GET}, but can be 
        set to L{POST}.
        :param method: should be either L{GET} or L{POST}. Other cases are 
            ignored.
        """
        if method in _allowedRequests : self.method = method
    
    def _getURI(self) :
        """Return the URI as sent (or to be sent) to the SPARQL endpoint. The
        URI is constructed with the base URI given at initialization, plus all
        the other parameters set.
        :return: URI
        :rtype: string
        """
        finalQueryText = [t for t in self._querytext ]
        finalQueryText.append(("query",self.queryString))
        
        if self.returnFormat != XML :
            # This is very ugly. The fact is that the key for the choice of 
            # the output format is not defined. Virtuoso uses 'format',
            # sparqler uses 'output'
            # However, these processors are (hopefully) oblivious to the 
            # parameters they do not understand. So: just repeat all 
            # possibilities in the final URI. UGLY!!!!!!!
            for f in _returnFormatSetting: finalQueryText.append(
                                                    (f,self.returnFormat))
        return self.baseURI + "?" + urllib.urlencode(finalQueryText)
    
    def _createRequest(self) :
        """Internal method to create request according a HTTP method. Returns
        a ``urllib2.Request`` object of the urllib2 Python library
        :return: request
        """
        if self.queryType == SELECT or self.queryType == ASK :
            if self.returnFormat == XML:
                acceptHeader = ",".join(_SPARQL_XML)
            elif self.returnFormat == JSON:
                acceptHeader = ",".join(_SPARQL_JSON)
            # elif self.returnFormat == N3 or self.returnFormat == TURTLE :
            #     acceptHeader = ",".join(_SPARQL_XML)
            else :
                acceptHeader = ",".join(_ALL)
        else :
            if self.returnFormat == N3 or self.returnFormat == TURTLE :
                acceptHeader = ",".join(_RDF_N3)
            elif self.returnFormat == XML :
                acceptHeader = ",".join(_RDF_XML)
            # elif self.returnFormat == JSON :
            #     acceptHeader = ",".join(_RDF_XML)
            else :
                acceptHeader = ",".join(_ALL)
        
        if self.method == POST :
            # by POST
            if self.debug:
                print "POST (Content-Type: application/x-www-form-urlencoded)"
                print "Accept: ", acceptHeader
                print self.queryString
            request = urllib2.Request(self.baseURI)
            request.add_header("Content-Type",
                                    "application/x-www-form-urlencoded")
            request.add_header("Accept",acceptHeader)
            values = { "query" : self.queryString }
            data = urllib.urlencode(values)
            request.add_data(data)
        else:
            # by GET
            # Some versions of Joseki do not work well if no Accept header is
            # given.
            # Although it is probably o.k. in newer versions, it does not harm
            # to have that set once and for all...
            if self.debug:
                print "GET ", self._getURI()
                print "Accept: ", acceptHeader
            request = urllib2.Request(self._getURI())
            request.add_header("Accept",acceptHeader)
        return request
    
    def _query(self):
        """Internal method to execute the query. Returns the output of the
        C{urllib2.urlopen} method of the standard Python library
        """
        request = self._createRequest()
        return urllib2.urlopen(request)
    
    def query(self) :
        """Execute the query.
        
        Exceptions can be raised if either the URI is wrong or the HTTP sends
        back an error (this is also the case when the query is syntactically
        incorrect, leading to an HTTP error sent back by the SPARQL endpoint).
        The usual urllib2 exceptions are raised, which therefore cover
        possible SPARQL errors, too.
        
        Note that some combinations of return formats and query types may not
        make sense. For example, a SELECT query with Turtle response is
        meaningless (the output of a SELECT is not a Graph), or a CONSTRUCT
        query with JSON output may be a problem because, at the moment, there
        is no accepted JSON serialization of RDF (let alone one implemented by
        SPARQL endpoints). In such cases the returned media type of the result
        is unpredictable and may differ from one SPARQL endpoint
        implementation to the other. (Endpoints usually fall back to one of
        the "meaningful" formats, but it is up to the specific implementation
        to choose which one that is.)
        
        :return: query result
        :rtype: ``QueryResult`` instance
        """
        return QueryResult(self._query())
    
    def queryAndConvert(self) :
        """Macro like method: issue a query and return the converted results.
        :return: the converted query result. See the conversion methods for
            more details.
        """
        res = self.query()
        return res.convert()
    


##############################################################################
class QueryResult :
    """
    Wrapper around an a query result. Users should not create instances of
    this class, it is generated by a
    :meth:`~rdfextras.tools.Client.SPARQLWrapper.query` call. The results can
    be converted to various formats, or used directly.
    
    If used directly: the class gives access to the direct http request
    results ``self.response``: it is a file-like object with two additional
    methods: ``geturl()`` to return the URL of the resource retrieved and
    ``info()`` that returns the meta-information of the HTTP result as a
    dictionary-like object (see the urllib2 standard library module of
    Python).
    
    For convenience, these methods are also available on the instance. The
    ``__iter__`` and ``next`` methods are also implemented (by mapping them to
    ``self.response``). This means that the common idiom::
        for l in obj : do_something_with_line(l)
    would work, too.
    
    :ivar response: the direct HTTP response; a file-like object, as return 
        by the ``urllib2.urlopen`` library call.
    """
    def __init__(self,response) :
        """
        @param response: HTTP response stemming from a L{SPARQLWrapper.query} call
        """
        self.response = response
        """Direct response, see class comments for details"""
    
    def geturl(self) :
        """Return the URI of the original call.
        :return: URI
        :rtype: string
        """
        return self.response.geturl()
    
    def info(self) :
        """Return the meta-information of the HTTP result.
        :return: meta information
        :rtype: dictionary
        """
        return self.response.info()
    
    def __iter__(self) :
        """Return an iterator object. This method is expected for the inclusion
        of the object in a standard C{for} loop.
        """
        return self.response.__iter__()
    
    def next(self) :
        """Method for the standard iterator."""
        return self.response.next()
    
    def _convertJSON(self) :
        """
        Convert a JSON result into a Python dict. This method can be overwritten in a subclass
        for a different conversion method.
        :return: converted result
        :rtype: Python dictionary
        """
        raise NotImplementedError("JSON object mapping not supported")
    
    def _convertXML(self) :
        """
        Convert an XML result into a Python dom tree. This method can be overwritten in a
        subclass for a different conversion method.
        :return: converted result
        :rtype: 4Suite DOMlette instance (http://infinitesque.net/projects/4Suite/docs/CoreManual.html#domlette_API)
        """
        try:
            from Ft.Xml import InputSource
            from Ft.Xml.Domlette import NonvalidatingReader
        except ImportError:
            raise Exception(
                    "4Suite-XML needs to be installed (http://pypi.python.org/pypi/4Suite-XML/1.0.2)")
        return NonvalidatingReader.parseStream(self.response,MEANINGLESS_URI)
    
    def _convertRDF(self) :
        """
        Convert an RDF/XML result into an RDFLib triple store. This method can
            be overwritten in a subclass for a different conversion method.
        :return: converted result
        :rtype: RDFLib Graph
        """
        from rdflib import ConjunctiveGraph
        retval = ConjunctiveGraph()
        # this is a strange hack. If the publicID is not set, rdflib (or the 
        # underlying xml parser) makes a funny (and, as far as I could see, 
        # meaningless) error message...
        retval.load(self.response,publicID=' ')
        return retval
    
    def _convertN3(self) :
        """
        Convert an RDF Turtle/N3 result into a string. This method can be 
        overwritten in a subclass for a different conversion method.
        :return: converted result
        :rtype: string
        """
        retval = ""
        for l in self.response :
            retval += l
        return retval
    
    def convert(self) :
        """
        Encode the return value depending on the return format:
        * in the case of XML, a DOM top element is returned;
        * in the case of JSON, a simplejson conversion will return a 
            dictionary;
        * in the case of RDF/XML, the value is converted via RDFLib into a 
            Graph instance.
        In all other cases the input simply returned.
        
        :return: the converted query result. See the conversion methods for 
            more details.
        """
        ct = self.response.info()["content-type"]
        if True in [ct.find(q) != -1 for q in _SPARQL_XML] :
            return self._convertXML()
        elif True in [ct.find(q) != -1 for q in _SPARQL_JSON]  :
            return self._convertJSON()
        elif True in [ct.find(q) != -1 for q in _RDF_XML] :
            return self._convertRDF()
        elif True in [ct.find(q) != -1 for q in _RDF_N3] :
            return self._convertN3()
        else :
            # this should cover, well, the rest of the cases...
            return self.response
    



