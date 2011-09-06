"""
[28] FunctionCall ::= IRIref ArgList

http://www.w3.org/TR/rdf-sparql-query/#evaluation
"""
from Util import ListRedirect

STR         = 0
LANG        = 1
LANGMATCHES = 2
DATATYPE    = 3
BOUND       = 4
isIRI       = 5
isURI       = 6
isBLANK     = 7
isLITERAL   = 8
sameTERM    = 9

FUNCTION_NAMES = {
    STR : 'STR',
    LANG : 'LANG',
    LANGMATCHES : 'LANGMATCHES',
    DATATYPE : 'DATATYPE',
    BOUND : 'BOUND',
    isIRI : 'isIRI',
    isURI : 'isURI',
    isBLANK : 'isBLANK',
    isLITERAL : 'isLITERAL',
    sameTERM : 'sameTERM'
}

class FunctionCall(object):
    def __init__(self, name, arguments=None):
        self.name = name
        self.arguments = arguments is None and [] or arguments

    def __repr__(self):
        return "%s(%s)" % (
            self.name,
            ','.join([isinstance(i, ListRedirect) and i.reduce() or i 
                        for i in self.arguments]))

class ParsedArgumentList(ListRedirect):
    def __init__(self, arguments):
        self._list = arguments

class ParsedREGEXInvocation(object):
    def __init__(self, arg1, arg2, arg3=None):
        self.arg1 = arg1
        self.arg2 = arg2
        self.arg3 = arg3

    def __repr__(self):
        return "REGEX(%s, %s%s)" % (
                 isinstance(self.arg1, ListRedirect) \
                    and self.arg1.reduce() or self.arg1,
                 isinstance(self.arg2, ListRedirect) \
                    and self.arg2.reduce() or self.arg2,
                 isinstance(self.arg3, ListRedirect) \
                    and self.arg3.reduce() or self.arg3,)

class BuiltinFunctionCall(FunctionCall):
    def __init__(self, name, arg1, arg2=None):
        if arg2:
            arguments = [arg1, arg2]
        else:
            arguments = [arg1]
        super(BuiltinFunctionCall,self).__init__(name,arguments)

    def __repr__(self):
        #print self.name
        #print [type(i) for i in self.arguments]
        return "%s(%s)" % (
            FUNCTION_NAMES[self.name],
            ','.join([isinstance(i,ListRedirect) \
                and str(i.reduce()) \
                or repr(i) 
                    for i in self.arguments]))
    
# Convenience


# from rdfextras.sparql2sql.bison.FunctionLibrary import STR
# from rdfextras.sparql2sql.bison.FunctionLibrary import LANG
# from rdfextras.sparql2sql.bison.FunctionLibrary import LANGMATCHES
# from rdfextras.sparql2sql.bison.FunctionLibrary import DATATYPE
# from rdfextras.sparql2sql.bison.FunctionLibrary import BOUND
# from rdfextras.sparql2sql.bison.FunctionLibrary import isIRI
# from rdfextras.sparql2sql.bison.FunctionLibrary import isURI
# from rdfextras.sparql2sql.bison.FunctionLibrary import isBLANK
# from rdfextras.sparql2sql.bison.FunctionLibrary import isLITERAL
# from rdfextras.sparql2sql.bison.FunctionLibrary import sameTERM
# from rdfextras.sparql2sql.bison.FunctionLibrary import FUNCTION_NAMES
# from rdfextras.sparql2sql.bison.FunctionLibrary import FunctionCall
# from rdfextras.sparql2sql.bison.FunctionLibrary import ParsedArgumentList
# from rdfextras.sparql2sql.bison.FunctionLibrary import ParsedREGEXInvocation
# from rdfextras.sparql2sql.bison.FunctionLibrary import BuiltinFunctionCall
