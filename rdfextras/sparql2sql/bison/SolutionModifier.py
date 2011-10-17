ASCENDING_ORDER   = 1
DESCENDING_ORDER  = 2
UNSPECIFIED_ORDER = 3

ORDER_VALUE_MAPPING = {
    ASCENDING_ORDER   : 'Ascending',
    DESCENDING_ORDER  : 'Descending',
    UNSPECIFIED_ORDER : 'Default',
}

class SolutionModifier(object):
    def __init__(self, orderClause=None, limitClause=None, offsetClause=None):
        self.orderClause = orderClause
        self.limitClause = limitClause
        self.offsetClause = offsetClause

    def __repr__(self):
        if not(self.orderClause or self.limitClause or self.offsetClause):
            return ""
        return "<SoutionModifier:%s%s%s>" % (
            self.orderClause and  ' ORDER BY %s' % self.orderClause or '',
            self.limitClause and  ' LIMIT %s' % self.limitClause or '',
            self.offsetClause and ' OFFSET %s' % self.offsetClause or '')

class ParsedOrderConditionExpression(object):
    """
    A list of OrderConditions
    
    OrderCondition ::= (('ASC'|'DESC')BrackettedExpression )|(FunctionCall|Var|BrackettedExpression)
    """
    def __init__(self, expression, order):
        self.expression = expression
        self.order = order

    def __repr__(self):
        return "%s(%s)" % (
            ORDER_VALUE_MAPPING[self.order],
            self.expression.reduce())

# Convenience

# from rdfextras.sparql2sql.bison.SolutionModifier import ASCENDING_ORDER
# from rdfextras.sparql2sql.bison.SolutionModifier import DESCENDING_ORDER
# from rdfextras.sparql2sql.bison.SolutionModifier import UNSPECIFIED_ORDER
# from rdfextras.sparql2sql.bison.SolutionModifier import SolutionModifier
# from rdfextras.sparql2sql.bison.SolutionModifier import ParsedOrderConditionExpression
