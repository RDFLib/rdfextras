# -*- coding: utf-8 -*-
#
#
# $Date: 2007/08/05 11:56:43 $
#
"""
:see: `SPARQL Specification <http://www.w3.org/TR/rdf-sparql-query/>`_
:authors: `Ivan Herman <http://www.ivan-herman.net">`, `Sergio Fernández 
    <http://www.wikier.org">`_, `Carlos Tejo Alonso <http://www.dayures.net>`_
:organization: `World Wide Web Consortium <http://www.w3.org>`_ and 
    `Foundation CTIC <http://www.fundacionctic.org/>`_.
:license: `W3C® SOFTWARE NOTICE AND LICENSE 
    <href="http://www.w3.org/Consortium/Legal/2002/copyright-software-20021231">`_
:requires: `simplejson <http://cheeseshop.python.org/pypi/simplejson>`_ package.
:requires: `PyXML <http://pyxml.sourceforge.net/>`_ package.
:requires: `RDFLib <http://rdflib.net>`_ package.
"""

from Wrapper import JSON, SELECT, SPARQLWrapper
import urllib2
from types import *

##############################################################################
class Value :
    """
    Class encapsulating a single binding for a variable.
    
    :cvar URI: the string denoting a URI variable
    :cvar Literal: the string denoting a Literal variable
    :cvar TypedLiteral: the string denoting a typed literal variable
    :cvar BNODE: the string denoting a blank node variable
    
    :ivar variable: The original variable, stored for an easier reference
    :type variable: string
    :ivar value: Value of the binding
    :type value: string
    :ivar type: Type of the binding
    :type type: string; one of  ``Value.URI``, ``Value.Literal``, 
        ``Value.TypedLiteral``, or ``Value.BNODE``
    :ivar lang: Language tag of the binding, or ``None`` if not set
    :type lang: string
    :ivar datatype: Datatype of the binding, or ``None`` if not set
    :type datatype: string (URI)
    """
    URI          = "uri"
    Literal      = "literal"
    TypedLiteral = "typed-literal"
    BNODE        = "bnode"
    
    def __init__(self,variable,binding) :
        """
        :param variable: the variable for that binding. Stored for an easier 
            reference
        :param binding: the binding dictionary part of the return result for 
            a specific binding
        """
        self.variable  = variable
        self.value     = binding['value']
        self.type      = binding['type']
        self.lang      = None
        self.datatype  = None
        try :
            self.lang = binding['xml:lang']
        except :
            # no lang is set
            pass
        try :
            self.datatype = binding['datatype']
        except :
            pass
    

##############################################################################
class Bindings :
    """
    Class encapsulating one query result, based on the JSON return format. It
    decodes the return values to make it a bit more usable for a standard
    usage. The class consumes the return value and instantiates a number of
    attributes that can be consulted directly. See the list of variables.
    
    The `Serializing SPARQL Query Results in JSON 
    <http://www.w3.org/TR/rdf-sparql-json-res/>`_ explains the details of the
    JSON return structures. Very succintly: the return data has "bindings", 
    which means a list of dictionaries. Each dictionary is a possible binding
    of the SELECT variables to ``Value`` instances. This structure is made a
    bit more usable by this class.
    
    :ivar fullResult: The original dictionary of the results, stored for an 
        easier reference
    :ivar head: Header part of the return, see the JSON return format document
        for details
    :ivar variables: List of unbounds (variables) of the original query. It is
        an array of strings. None in the case of an ASK query
    :ivar bindings: The final bindings: array of dictionaries, mapping 
        variables to ``Value`` instances.
    (If unbound, then no value is set in the dictionary; that can be easily 
        checked with
    ``var in res.bindings[..]``, for example.)
    :ivar askResult: by default, set to False; in case of an ASK query, the 
        result of the query
    :type askResult: Boolean
    """
    def __init__(self,retval) :
        """
        :param retval: the query result, instance of a ``Wrapper.QueryResult``
        """
        self.fullResult  = retval._convertJSON()
        self.head        = self.fullResult['head']
        self.variables   = None
        try :
            self.variables   = self.fullResult['head']['vars']
        except :
            pass
        
        self.bindings    = []
        try :
            for b in self.fullResult['results']['bindings'] :
                # this is a single binding.  It is a dictionary per variable;
                # each value is a dictionary again that has to be converted 
                # into a Value instance
                newBind = {}
                for key in self.variables :
                    if key in b :
                        # there is a real binding for this key
                        newBind[key] = Value(key,b[key])
                self.bindings.append(newBind)
        except :
            pass
        
        self.askResult = False
        try :
            self.askResult = self.fullResult["boolean"]
        except :
            pass
    
    def getValues(self,key) :
        """A shorthand for the retrieval of all bindings for a single key. It
        is equivalent to "``[b[key] for b in self[key]]``"
        :param key: possible variable
        :return: list of ``Value`` instances
        """
        try :
            return [b[key] for b in self[key]]
        except :
            return []
    
    def __contains__(self,key) :
        """Emulation of the "``key in obj``" operator. Key can be a string for
        a variable or an array/tuple of strings.
        
        If ``key`` is a variable, the return value is ``True`` if there is at
        least one binding where ``key`` is bound. If ``key`` is an array or
        tuple, the return value is ``True`` if there is at least one binding
        where *all* variables in ``key`` are bound.
        
        :param key: possible variable, or array/tuple of variables
        :return: whether there is a binding of the variable in the return
        :rtype: Boolean
        """
        if len(self.bindings) == 0 : return False
        if type(key) is ListType or type(key) is TupleType :
            # check first whether they are all really variables
            if False in [ k in self.variables for k in key ]: return False
            for b in self.bindings :
                # try to find a binding where all key elements are present
                if False in [ k in b for k in key ] :
                    # this is not a binding for the key combination, move on...
                    continue
                else :
                    # yep, this one is good!
                    return True
            return False
        else :
            if key not in self.variables : return False
            for b in self.bindings :
                if key in b : return True
            return False
    
    def __getitem__(self,key) :
        """Emulation of the ``obj[key]`` operator. Slice notation is also
        available. The goal is to choose the right bindings among the
        available ones. The return values are always arrays of bindings, ie,
        arrays of dictionaries mapping variable keys to ``Value`` instances.
        The different value settings mean the followings:
         
        * ``obj[key]`` returns the bindings where ``key`` has a valid value
        * ``obj[key1,key2,...]`` returns the bindings where *all* 
            ``key1,key2,...`` have valid values
        * ``obj[(key1,key2,...):(nkey1,nkey2,...)]`` returns the bindings 
            where all ``key1,key2,...`` have
         valid values and *none* of the ``nkey1,nkey2,...`` have valid values
        * ``obj[:(nkey1,nkey2,...)]`` returns the bindings where *none* of 
            the ``nkey1,nkey2,...`` have valid values
        
        In all cases complete bindings are returned, ie, the values for other
        variables, not present among the keys in the call, may or may not be
        present depending on the query results.
        
        :param key: possible variable or array/tuple of keys with possible 
            slice notation
        :return: list of bindings
        :rtype: array of variable -> ``Value``  dictionaries
        """
        def _checkKeys(keys) :
            if len(keys) == 0 : return False
            for k in keys :
                if not isinstance(k,StringTypes) or not k in self.variables: 
                    return False
            return True
        
        def _nonSliceCase(key) :
            if isinstance(key,StringTypes) and key != "" \
                and key in self.variables :
                # unicode or string:
                return [key]
            elif type(key) is ListType or type(key) is TupleType :
                if _checkKeys(key) :
                    return key
            return False
        
        # The arguments should be reduced to arrays of variables, ie, unicode
        # strings
        yes_keys = []
        no_keys  = []
        if type(key) is SliceType :
            # Note: None for start or stop is all right
            if key.start :
                yes_keys = _nonSliceCase(key.start)
                if yes_keys == False : raise TypeError
            if key.stop :
                no_keys  = _nonSliceCase(key.stop)
                if no_keys  == False : raise TypeError
        else :
            yes_keys = _nonSliceCase(key)
        
        # got it right, now get the right binding line with the constraints
        retval = []
        for b in self.bindings :
            # first check whether the 'yes' part is all there:
            if False in [k in b for k in yes_keys] : continue
            if True  in [k in b for k in no_keys]  : continue
            # if we got that far, we shouild be all right!
            retval.append(b)
        # if retval is of zero length, no hit; an exception should be raised 
        # to stay within the python style
        if len(retval) == 0 :
            raise IndexError
        return retval
    
    def convert(self) :
        """This is just a convenience method, returns ``self``.
        
        Although ``Binding`` is not a subclass of 
        ``SPARQL.Wrapper.QueryResult``, it is returned as a result by
        ``SPARQLWrapper2.query``, just like ``SPARQL.Wrapper.QueryResult`` is
        returned by ``SPARQL.SPARQLWrapper.query``. Consequently,
        having an empty ``convert`` method to imitate :class:`QueryResult`'s
        convert :meth:`~SPARQL.Wrapper.QueryResult.convert` may avoid 
        unnecessary problems.
        """
        return self
    

##############################################################################

class SPARQLWrapper2(SPARQLWrapper) :
    """Subclass of ``Wrapper<SPARQL.SPARQLWrapper>`` that works with a JSON
    SELECT return result only. The query result is automatically set to a
    ``Bindings`` instance. Makes the average query processing a bit
    simpler..."""
    def __init__(self,baseURI,defaultGraph=None) :
        """
        Class encapsulating a full SPARQL call. In contrast to the
        :class:`SPARQL.SPARQLWrapper` superclass, the return format
        cannot be set (it is defaulted to :class:`Wrapper.JSON`).
        :param baseURI: string of the SPARQL endpoint's URI
        :type baseURI: string
        :keyword defaultGraph: URI for the default graph. Default is None, can
            be set via an explicit call, too
        :type defaultGraph: string
        """
        SPARQLWrapper.__init__(
            self, baseURI,returnFormat=JSON,defaultGraph=defaultGraph)
    
    def setReturnFormat(self,format) :
        """Set the return format (overriding the inherited method
        :meth:`SPARQL.SPARQLWrapper.setReturnFormat`). This method does 
        nothing; this class instance should work with JSON only. The method
        is defined just to avoid possible errors by erronously setting the
        return format. When using this class, the user can safely ignore this
        call.
        :param format: return format
        """
        pass
    
    def query(self) :
        """Execute the query and do an automatic conversion.
            
        Exceptions can be raised if either the URI is wrong or the HTTP sends
        back an error. The usual urllib2 exceptions are raised, which cover
        possible SPARQL errors, too.
        
        If the query type is *not* SELECT, the method falls back to the
        ``corresponding method in the superclass<SPARQLWrapper.query>``.
        
        :return: query result
        :rtype: ``Bindings`` instance
        """
        res = SPARQLWrapper.query(self)
        if self.queryType == SELECT :
            return Bindings(res)
        else :
            return res
    
    def queryAndConvert(self) :
        """This is here to override the inherited method; it is equivalent to
        ``query``.
        
        If the query type is *not* SELECT, the method falls back to the
        corresponding method in the superclass 
            :class:`SPARQLWrapper.queryAndConvert`.
        
        :return: the converted query result.
        """
        if self.queryType == SELECT :
            return self.query()
        else :
            return SPARQLWrapper.queryAndConvert(self)
    


