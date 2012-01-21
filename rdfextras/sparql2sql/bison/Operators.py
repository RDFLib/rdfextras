from Util import ListRedirect

class BinaryOperator(object):
    NAME = ''
    def __init__(self,left,right):
        self.left = left
        self.right = right

    def __repr__(self):
        return "(%s %s %s)"%(
            isinstance(self.left,ListRedirect) and self.left.reduce() or self.left,
            self.NAME,
            isinstance(self.right,ListRedirect) and self.right.reduce() or self.right)

class EqualityOperator(BinaryOperator):
    NAME = '='

class NotEqualOperator(BinaryOperator):
    NAME = '!='

class LessThanOperator(BinaryOperator):
    NAME = '<'

class LessThanOrEqualOperator(BinaryOperator):
    NAME = '<='

class GreaterThanOperator(BinaryOperator):
    NAME = '>'

class GreaterThanOrEqualOperator(BinaryOperator):
    NAME = '>='

class UnaryOperator(object):
    NAME = ''
    def __init__(self, argument):
        self.argument = argument
    
    def __repr__(self):
        return "(%s %s)" % (
            self.NAME,
            isinstance(self.argument,ListRedirect) \
                and self.argument.reduce() \
                or self.argument)

class LogicalNegation(UnaryOperator):
    NAME = '!'

class NumericPositive(UnaryOperator):
    NAME = '+'

class NumericNegative(UnaryOperator):
    NAME = '-'        

# Convenience
# from rdfextras.sparql2sql.bison.Operators import BinaryOperator
# from rdfextras.sparql2sql.bison.Operators import EqualityOperator
# from rdfextras.sparql2sql.bison.Operators import NotEqualOperator
# from rdfextras.sparql2sql.bison.Operators import LessThanOperator
# from rdfextras.sparql2sql.bison.Operators import LessThanOrEqualOperator
# from rdfextras.sparql2sql.bison.Operators import GreaterThanOperator
# from rdfextras.sparql2sql.bison.Operators import GreaterThanOrEqualOperator
# from rdfextras.sparql2sql.bison.Operators import UnaryOperator
# from rdfextras.sparql2sql.bison.Operators import LogicalNegation
# from rdfextras.sparql2sql.bison.Operators import NumericPositive
# from rdfextras.sparql2sql.bison.Operators import NumericNegative
