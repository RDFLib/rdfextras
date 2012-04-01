# -*- coding: utf-8 -*-
"""
$Date: 2005/11/04 14:06:36 $, by $Author: ivan $, $Revision: 1.1 $

API for the SPARQL operators.
-----------------------------

The operators (eg, 'lt') return a *function* that can be added to the AND
clause of a query. The parameters are either regular values or query strings.

The resulting function has one parameter (the binding directory), it can be
combined with others or be plugged to into an array of constraints.

For example::

    constraints = [lt("?m", 42)]

for checking whether "?m" is smaller than the (integer) value 42. It can be
combined using the lambda function, for example::

    constraints = [lambda(b): lt("?m", 42")(b) or lt("?n", 134)(b)]

is the expression for::

   AND ?m < 42 || ?n < 134

(Clearly, the relative complexity is only on the API level; a SPARQL
language parser that starts with a SPARQL expression can map on this API).

"""

import sys, re
from rdflib.term import Literal, BNode, URIRef, Variable
from rdflib.namespace import XSD
from rdfextras.sparql.graph import _createResource
from rdfextras.sparql import _questChar, Debug

# We replace str with a custom function below. This messes things up after
# 2to3 conversion, which replaces basestring with str. At some point, we should
# clean this up properly - i.e. don't override the builtin str.
str_ = basestring

def queryString(v):
    """
    Boolean test whether this is a a query string or not
    :param v: the value to be checked
    :returns: True if it is a query string
    """

    return isinstance(v,str_) and len(v) != 0 and v[0] == _questChar

def getLiteralValue(v):
    """
    Return the value in a literal, making on the fly conversion on datatype
    (using the datatypes that are implemented)
    :param v: the Literal to be converted
    :returns: the result of the conversion.
    """
    return v

def getValue(param):
    """
    Returns a *value retrieval function*. The return value can be plugged in a
    query; it would return the value of param directly if param is a real value,
    and the run-time value if param is a query string of the type "?xxx".
    If no binding is defined at the time of call, the return value is None.

    :param param: query string, Unbound instance, or real value
    :returns: a function taking one parameter (the binding directory)
    """

    if isinstance(param,Variable):
        unBound = True

    else:
        unBound = queryString(param)

        if not unBound:

            if isinstance(param, Literal):
                value = getLiteralValue(param)
            elif callable(param):
                return param
            else:
                value = param

            return lambda(bindings): value

    def f(bindings):
        if unBound:
            # @@note, param must be reassigned to avoid tricky issues of scope
            # see: http://docs.python.org/ref/naming.html
            _param = isinstance(param, Variable) and param or Variable(param[1:])
            val = bindings[_param]
            if isinstance(val,Literal):
                return getLiteralValue(val)
            else:
                return val
        else:
            return value

    return f

def lt(a, b):
    """
    Operator for '&lt;'
    :param a: value or query string
    :param b: value or query string
    :returns: comparison method
    """
    fa = getValue(a)
    fb = getValue(b)

    def f(bindings):
        try:
            return fa(bindings) < fb(bindings)
        except:
            # raise
            # this is the case when the operators are incompatible
            if Debug:
                (typ,val,traceback) = sys.exc_info()
                sys.excepthook(typ, val, traceback)
            return False

    return f

##
# Operator for '&lt;='
# @param a value or query string
# @param b value or query string
# @return comparison method
def le(a, b):
    fa = getValue(a)
    fb = getValue(b)

    def f(bindings):
        try:
            return fa(bindings) <= fb(bindings)
        except:
            # this is the case when the operators are incompatible
            if Debug:
                (typ,val,traceback) = sys.exc_info()
                sys.excepthook(typ, val, traceback)
            return False

    return f

def gt(a, b):
    """
    Operator for '&gt;'
    :param a: value or query string
    :param b: value or query string
    :returns: comparison method
    """

    fa = getValue(a)
    fb = getValue(b)

    def f(bindings):
        try:
            return fa(bindings) > fb(bindings)
        except:
            # this is the case when the operators are incompatible
            if Debug:
                (typ,val,traceback) = sys.exc_info()
                sys.excepthook(typ, val, traceback)
            return False

    return f

def ge(a, b):
    """
    Operator for '&gt;='
    :param a: value or query string
    :param b: value or query string
    :returns: comparison method
    """
    fa = getValue(a)
    fb = getValue(b)

    def f(bindings):
        try:
            return fa(bindings) >= fb(bindings)
        except:
            # this is the case when the operators are incompatible
            if Debug:
                (typ,val,traceback) = sys.exc_info()
                sys.excepthook(typ, val, traceback)
            return False

    return f

def eq(a, b):
    """
    Operator for '='
    :param a: value or query string
    :param b: value or query string
    :returns: comparison method
    """
    fa = getValue(a)
    fb = getValue(b)

    def f(bindings):
        try:
            return fa(bindings) == fb(bindings)
        except:
            # this is the case when the operators are incompatible
            if Debug:
                (typ,val,traceback) = sys.exc_info()
                sys.excepthook(typ, val, traceback)
            return False

    return f


def neq(a, b):
    """
    Operator for '!='
    :param a: value or query string
    :param b: value or query string
    :returns: comparison method
    """
    fa = getValue(a)
    fb = getValue(b)

    def f(bindings):
        try:
            return fa(bindings) != fb(bindings)
        except:
            # this is the case when the operators are incompatible
            if Debug:
                (typ,val,traceback) = sys.exc_info()
                sys.excepthook(typ, val, traceback)
            return False

    return f

def __getVariableName(v):
    if isinstance(v, Variable):
        return v
    elif queryString(v):
        return v[1:]
    else:
        return None
def bound(a):
    """
    Is the variable bound
    :param a: value or query string
    :returns: check method
    """

    v = __getVariableName(a)

    def f(bindings):
        if v == None:
            return False
        if v in bindings:
            val = bindings[v]
            return not (val == None)
        else:
            return False

    return f

def isURI(a):
    """
    Is the variable bound to a URIRef
    :param a: value or query string
    :returns: check method
    """
    v = __getVariableName(a)

    def f(bindings):
        if v == None:
            return False
        try:
            val = bindings[v]
            if val == None:
                return False
            else:
                return isinstance(val, URIRef)
        except:
            return False

    return f


def isIRI(a):
    """
    Is the variable bound to a IRIRef (this is just an alias for URIRef)
    :param a: value or query string
    :returns: check method
    """
    return isURI(a)


def isBlank(a):
    """
    Is the variable bound to a Blank Node
    :param a: value or query string
    :returns: check method
    """

    v = __getVariableName(a)

    def f(bindings):
        if v == None:
            return False
        try:
            val = bindings[v]
            if val == None:
                return False
            else:
                return isinstance(val, BNode)
        except:
            return False

    return f

def isLiteral(a):
    """
    Is the variable bound to a Literal
    :param a: value or query string
    :returns: check method
    """

    v = __getVariableName(a)

    def f(bindings):
        if v == None:
            return False
        try:
            val = bindings[v]
            if val == None:
                return False
            else:
                return isinstance(val, Literal)
        except:
            return False

    return f

def str(a):
    """
    Return the string version of a resource
    :param a: value or query string
    :returns: check method
    """

    v = __getVariableName(a)

    def f(bindings):
        if v == None:
            return ""
        try:
            val = bindings[v]
            if val == None:
                return ""
            else:
                from __builtin__ import str as _str
                return _str(val)
        except:
            return ""

    return f

def lang(a):
    """Return the lang value of a literal
    :param a: value or query string
    :returns: check method
    """

    v = __getVariableName(a)

    def f(bindings):
        if v == None:
            return ""

        try:
            val = bindings[v]
            if val == None:
                return ""
            elif val.language == None:
                return ""
            else:
                return val.language

        except:
            return ""

    return f

def langmatches(lang, _range):
    lv = getValue(lang)
    rv = getValue(_range)

    def f(bindings):
        if lv == None:
            return False

        if rv == None:
            return False

        return _langMatch(lv(bindings), rv(bindings))

    return f

def _langMatch(lang, _range):
	"""

    Borrowed from http://dev.w3.org/2004/PythonLib-IH/RDFClosure/RestrictedDatatype.py
    Author: Ivan Herman

	Implementation of the extended filtering algorithm, as defined in
    point 3.3.2, of `RFC 4647 <http://www.rfc-editor.org/rfc/rfc4647.txt>`_,
    on matching language ranges and language tags.

	Needed to handle the C{rdf:PlainLiteral} datatype.

	:param range: language range
	:param lang: language tag
	:returns: boolean
	"""

	def _match(r, l):
		"""Matching of a range and language item: either range is a wildcard
        or the two are equal
		:param r: language range item
		:param l: language tag item
		:rtype: boolean
		"""
		return r == '*' or r == l

	rangeList = _range.strip().lower().split('-')
	langList  = lang.strip().lower().split('-')

	if not _match(rangeList[0], langList[0]): return False

	rI = 1
	rL = 1

	while rI < len(rangeList):
		if rangeList[rI] == '*':
			rI += 1
			continue

		if rL >= len(langList):
			return False

		if _match(rangeList[rI], langList[rL]):
			rI += 1
			rL += 1
			continue

		if len(langList[rL]) == 1:
			return False

		else:
			rL += 1
			continue
	return True

def datatype(a):
    """Return the datatype URI of a literal
    :param a: value or query string
    :returns: check method

    """

    v = __getVariableName(a)

    def f(bindings):
        if v == None:
            if isinstance(a, Literal):
                return a.datatype
            else:
                raise TypeError(a)

        try :

            val = bindings[v]

            if val == None:
                return TypeError(v)
            elif isinstance(val, Literal) and not val.language:
                return val.datatype
            else:
                raise TypeError(val)

        except:
            raise TypeError(v)

    return f


def isOnCollection(collection, item, triplets):
    """
    Generate a method that can be used as a global constaint in sparql to
    check whether the 'item' is an element of the 'collection' (a.k.a. list).
    Both collection and item can be a real resource or a query string.
    Furthermore, item might be a plain string, that is then turned into a
    literal run-time. The method returns an adapted method.

    Is a resource on a collection?

    The operator can be used to check whether the 'item' is an element of the
    'collection' (a.k.a. list). Both collection and item can be a real resource
    or a query string.

    :param collection: is either a query string (that has to be bound by the query) or an RDFLib Resource
      representing the collection

    :param item: is either a query string (that has to be bound by the query), an RDFLib Resource, or
      a data type value that is turned into a corresponding Literal (with possible datatype)
      that must be tested to be part of the collection

    :returns: a function

    """
    # check_subject(collection)
    collUnbound = False

    if isinstance(collection, Variable):
        collUnbound = True
        collection  = collection

    elif queryString(collection):
        # just keep 'collection', no reason to reassign
        collUnbound = True

    else:
        collUnbound = False
        # if we got here, this is a valid collection resource

    if isinstance(item, Variable):
        queryItem = item
        itUnbound  = True

    elif queryString(item):
        queryItem = item
        itUnbound = True

    else:
        # Note that an exception is raised if the 'item' is invalid
        queryItem = _createResource(item)
        itUnbound = False

    def checkCollection(bindings):
        try:
            if collUnbound == True:
                # the binding should come from the binding
                coll = bindings[collection]
            else:
                coll = collection

            if itUnbound == True:
                it = bindings[queryItem]
            else:
                it = queryItem

            return it in triplets.items(coll)

        except:
            # this means that the binding is not available. But that also
            # means that the global constraint was used, for example, with
            # the optional triplets; not available binding means that the
            # method is irrelevant for those ie, it should not become a
            # show-stopper, hence it returns True
            return True

    return checkCollection


def addOperator(args, combinationArg):
    """
    SPARQL numeric + operator implemented via Python
    """
    return ' + '.join([
        "sparqlOperators.getValue(%s)%s" % (
            i, combinationArg and "(%s)" % combinationArg or '')
                for i in args])

def XSDCast(source, target=None):
    """
    XSD Casting/Construction Support
    For now (this may be an issue since Literal doesn't override comparisons)
    it simply creates a Literal with the target datatype using the 'lexical'
    value of the source
    """
    sFunc = getValue(source)

    def f(bindings):
        rt = sFunc(bindings)

        if isinstance(rt, Literal) and rt.datatype == target:
            # Literal already has target datatype
            return rt
        else:
            return Literal(rt, datatype=target)

    return f

def regex(item, pattern, flag=None):
    """
    Invokes the XPath fn:matches function to match text against a regular
    expression pattern.
    The regular expression language is defined in XQuery 1.0 and XPath 2.0
    Functions and Operators section 7.6.1 Regular Expression Syntax
    """
    a = getValue(item)
    b = getValue(pattern)

    if flag:
        cFlag = 0
        usedFlags = []

        # Maps XPath REGEX flags (http://www.w3.org/TR/xpath-functions/#flags)
        # to Python's re flags
        for fChar,_flag in [
                ('i', re.IGNORECASE), ('s', re.DOTALL), ('m', re.MULTILINE)]:
            if fChar in flag and fChar not in usedFlags:
                cFlag |= _flag
                usedFlags.append(fChar)

        def f1(bindings):
            try:
                return bool(re.compile(b(bindings),cFlag).search(a(bindings)))
            except:
                return False
        return f1

    else:
        def f2(bindings):
            try:
                return bool(re.compile(b(bindings)).search(a(bindings)))
            except:
                return False
        return f2

    def f(bindings):
        try:
            return bool(re.compile(a(bindings)).search(b(bindings)))
        except Exception, e:
            print e
            return False
    return f

def EBV(a):
    """
    * If the argument is a typed literal with a datatype of xsd:boolean,
      the EBV is the value of that argument.
    * If the argument is a plain literal or a typed literal with a
      datatype of xsd:string, the EBV is false if the operand value
      has zero length; otherwise the EBV is true.
    * If the argument is a numeric type or a typed literal with a datatype
      derived from a numeric type, the EBV is false if the operand value is
      NaN or is numerically equal to zero; otherwise the EBV is true.
    * All other arguments, including unbound arguments, produce a type error.

    """
    fa = getValue(a)

    def f(bindings):
        try:
            rt = fa(bindings)

            if isinstance(rt, Literal):

                if rt.datatype == XSD.boolean:
                    ebv = rt.toPython()

                elif rt.datatype == XSD.string or rt.datatype is None:
                    ebv = len(rt) > 0

                else:
                    pyRT = rt.toPython()

                    if isinstance(pyRT,Literal):
                        #Type error, see: http://www.w3.org/TR/rdf-sparql-query/#ebv
                        raise TypeError("http://www.w3.org/TR/rdf-sparql-query/#ebv")
                    else:
                        ebv = pyRT != 0

                return ebv

            else:
                print rt, type(rt)
                raise

        except Exception, e:
            if isinstance(e, KeyError):
                # see: http://www.w3.org/TR/rdf-sparql-query/#ebv
                raise TypeError("http://www.w3.org/TR/rdf-sparql-query/#ebv")
            # this is the case when the operators are incompatible
            raise

            if Debug:
                (typ,val,traceback) = sys.exc_info()
                sys.excepthook(typ, val, traceback)

            return False

    return f
