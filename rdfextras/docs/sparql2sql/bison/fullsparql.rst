.. _rdfextras_sparql_bison_fullsparql: RDFExtras SPARQL implementations

|today|

=====================================================================
:mod:`~rdfextras.sparql2sql.bison` BisonGen full SPARQL syntax parser
=====================================================================

Post to rdflib-dev Sat, 20 May 2006
===================================
I just checked in the most recent version of what had been an
experimental, generated (see:
http://copia.ogbuji.net/blog/2005-04-27/Of_BisonGe) parser for the
full SPARQL syntax, I had been working on to hook up with sparql-p.
It parses a SPARQL query into a set of Python objects representing the
components of the grammar:

http://svn.rdflib.net/trunk/rdflib/sparql/bison/

The parses itself is a Python/C extension, so the setup.py had to be
modified in order to compile it into a Python module.

I also checked in a test harness that's meant to work with the DAWG test cases:

http://svn.rdflib.net/trunk/test/BisonSPARQLParser

I'm currently stuck on this test case, but working through it:

http://www.w3.org/2001/sw/DataAccess/tests/#optional-outer-filter-with-bound

The test harness only checks for parsing, it doesn't evaluate the
parsed query against the corresponding set of test data, but can be
easily be extended to do so.

I'm not sure about the state of those test cases, some have been 'accepted'
and some haven't. I came across a couple that were illegal according to the
most recent SPARQL grammar (the bad tests are noted in the test harness).
Currently the parser is stand-alone, it doesn't invoke sparql-p for a few
reasons:

* I wanted to get it through parsing the queries in the test case first
* Our integrated version of sparql-p is outdated as there is a more recent version  that Ivan has been working on with some improvements we should consider integrating
* Some of the more complex combinations of Graph Patterns don't seem solvable without re-working / extending the expansion tree solver.  I have some ideas about how this could be done (to handle things like nested UNIONS and OPTIONALs) but wanted to get a working parser in first

Using the parser is simple:

.. sourcecode:: python

    from rdfextras.sparql2sql.bison import Parse
    p = Parse(query,DEBUG)
    print p

p is an instance of :class:`~rdfextras.sparql2sql.bison.Query.Query`

Most of the parsed objects implement a ``__repr__`` function which prints
a representation of the parsed objects.  The functions recurse down
into the lower level objects, so tracing how each ``__repr__`` method is
implemented is a good way to determine how to deconstruct the parsed
SPARQL query object.

These ``__repr__`` methods could probably be re-written to echo the SPARQL
query right back as a way to

* Test round-tripping of SPARQL queries
* Create SPARQL queries by instantiating the :mod:`rdfextras.sparql2sql.bison`.* objects and converting them to strings

It's still a work in progress, but I think it's far enough through the
test cases that it can handle most of the more common syntax.

-- http://www.mail-archive.com/dev@rdflib.net/msg00021.html





Post to Chimezie's blog, 19 May 2006
====================================

This is basically an echo of my recent post to the rdflib mailing list (yes,
we have one now).

I just checked in the most recent version of what had been an experimental,
BisonGen SPARQL parser for RDFLib. It parses a SPARQL query into a set of
Python objects representing the components of the grammar:

The parser itself is a Python/C extension (but the BisonGen grammar could be
extended to incorporate Java callbacks instead), so the setup.py had to be
modified in order to compile it into a Python module. The BisonGen files
themselves are:

* SPARQL.bgen (the main file that includes the others)
* SPARQLTurtleSuperSet.bgen.frag (the second part of the grammar which focuses on the variant of Turtle that SPARQL uses)
* SPARQLTokens.bgen.frag (Token definitions)
* SPARQLLiteralLexerPatterns.bgen.frag (Keywords and 'literal' tokens)
* SPARQLLexerPatterns.bgen.frag (lexer definition)
* SPARQLLexerDefines.bgen.frag (the lexer patterns themselves)
* SPARQLParser.c (the generated parser)

Theoretically, the second part of the grammar dedicated to the Turtle syntax
could be broken out into seperate Turtle/N3 parsers which could be built in to
RDFLib, removing the current dependency on n3p

I also checked in a test harness that's meant to work with the DAWG test cases:

I'm currently stuck on this particular test case, but working through it. For
the most part a majority of the grammar is supported except mathematical
expressions and certain case-insensitive variations on the SPARQL operators.

The test harness only checks for parsing, it doesn't evaluate the parsed query
against the corresponding set of test data, but can be easily be extended to
do so. I'm not sure about the state of those test cases, some have been
'accepted' and some haven't. In addition, I came across a couple that were
illegal according to the most recent SPARQL grammar (the bad tests are noted
in the test harness). Currently the parser is stand-alone, it doesn't invoke
sparql-p for a few reasons:

I wanted to get it through parsing the queries in the test case

Our integrated version of sparql-p is outdated as there is a more recent
version that Ivan has been working on with some improvements that should
probably be considered for integration

Some of the more complex combinations of Graph Patterns don't seem solvable
without re-working / extending the expansion tree solver. I have some ideas
about how this could be done (to handle things like nested UNIONS and
OPTIONALs) but wanted to get a working parser in first

Using the parser is simple:

.. sourcecode:: python

    from rdflib.sparql.bison import Parse
    p = Parse(query,DEBUG)
    print p

p is an instance of rdfextras.sparql2sql.bison.Query.Query

Most of the parsed objects implement a __repr__ function which prints a 'meaningful' representation recursively down the hierarchy to the lower level objects, so tracing how each __repr__ method is implemented is a good way to determine how to deconstruct the parsed SPARQL query object.

These methods could probably be re-written to echo the SPARQL query right back
as a way to

* Test round-tripping of SPARQL queries
* Create SPARQL queries by instantiating the :mod:`rdflib.sparql.bison`.* objects and converting them to strings

It's still a work in progress, but I think it's far enough through the test
cases that it can handle most of the more common syntax.

Working with BisonGen was a good experience for me as I hadn't done any real
work with parser generators since my days at the University of Illinois (class
of '99'). There are plenty of good references online for the Flex pattern
format as well as Bison itself. I also got some good pointers from AndyS and
EricP on #swig.

It also was an excellent way to get familiar with the SPARQL syntax from top
to bottom, since every possible nuance of the grammar that may not be evident
from the specification had to be addressed. It also generated some comments on
inconsistencies in the specification grammar that I've since redirected to
public-rdf-dawg-comments


Martin v. Löwis' description of BisonGen
========================================

(Referenced in Chimezie's `27 May 2006 blog post <http://copia.posterous.com/of-bisongen>`_)

Fourthought Inc has developed the BisonGen framework to implement parsers for
their 4Suite package [Fou01]. The parser is defined using an XML syntax. Until
recently, the build process of a BisonGen parser was as follows:

* BisonGen parses the XML file using PyXML.
* It generates a number of files, including a flex input file for lexical analysis, a bison input file, containing the LALR(1) grammar, a SWIG input file, containing a Python extension module, a Makefile, controlling the build process of all compiled files, and a number of Python wrapper files to expose the parser to Python.
* flex, bison, and SWIG are invoked to generate C code, The C code is compiled to form an extension module.

Recently, this build procedure was completely restructured. Today, BisonGen
implements the LALR(1) algorithm itself, not relying on bison anymore.
Therefore, the build procedure is simplified to:

* BisonGen parses the XML specification of the grammar.
* It generates a C file, containing a C-implemented parser, and a Python module that implements the same parsing algorithm in pure Python.
* If desired, the C code is compiled for improved performance.

To give an impression of how BisonGen code looks, the UnionExpr production is
again presented, as it appears in the 0.11 release of 4Suite.

.. sourcecode:: xml

    <RULE_SET NAME="18">
      <NON_TERMINAL>unionExpr</NON_TERMINAL>
      <RULE>
        <SYMBOL TYPE="s">pathExpr</SYMBOL>
        <CODE>
        </CODE>
      </RULE>
      <RULE>
        <SYMBOL TYPE="s">unionExpr</SYMBOL>
        <SYMBOL TYPE="s">'|'</SYMBOL>
        <SYMBOL TYPE="s">pathExpr</SYMBOL>
        <CODE>
          <VARIABLE TYPE="PyObject*" NAME="right"></VARIABLE>
          <VARIABLE TYPE="PyObject*" NAME="left"></VARIABLE>
          <VARIABLE TYPE="PyObject*" NAME="expr"></VARIABLE>
          <CODE_SNIPPET>
            right = stack_pop();
            left = stack_pop();
            expr = PyObject_CallMethod(ParsedExpr, "ParsedUnionExpr", "OO", left, right);
            decref(right);
            decref(left);
            stack_push(expr);
          </CODE_SNIPPET>
        </CODE>
      </RULE>
    </RULE_SET>

Since the document type for BisonGen varies between releases, we will not
explain all tags used here in detail. In this fragment, two rules are defined,
which are both alternatives of the unionExpr non-terminal. The right-hand-side
of each rule consists of a sequence of symbols; it is just pathExpr for the
first rule, and unionExpr '|' pathExpr for the second.

In the second rule, a specific semantic action is defined, which is a call to
ParsedExpr.ParsedUnionExpr, which in turn is a class of the abstract syntax.
BisonGen will declare three variables in the Bison file, and insert the
specified code snippet into the semantic action.

Even though the build process of BisonGen applications has been dramatically
simplified recently, the grammar specifications still look quite verbose.

Integration with the lexical analysis follows the usual YACC convention: an
yylex function is invoked to return the next token. Token numbers identify
tokens. In addition, the yylval variable carries the semantic value.

Older versions of BisonGen generate flex files from token definitions given
XML; the recent versions generate re-style regular expressions from similar
XML specifications.

Error handling also follows the YACC tradition: an yyerror function is
invoked. Since unwinding out of a bison parser run is not easy, this function
normally only sets a global variable, which is then checked when the parser
returns.

The BisonGen distribution comes with a short overview of the grammar input
language, and a few examples as part of the test suite.

-- http://www.python.org/community/sigs/retired/parser-sig/towards-standard/


