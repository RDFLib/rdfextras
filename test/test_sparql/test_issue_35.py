import unittest

from rdfextras.sparql.parser import Query

qstring = r"""SELECT ?f where { ?f <#b> <c#d> }"""

class TestIssue35(unittest.TestCase):
    def test_issue_35(self):
        res = Query.parseString(qstring)
        assert res is not None

if __name__ == "__main__":
    unittest.main()

