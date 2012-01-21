This harness is meant to work against the DAWG test cases:

http://www.w3.org/2001/sw/DataAccess/tests/r2

Uncompress the contents in a convenient place and move the directory "data-r2"
to <rdfextras/test/data-r2> and then create a soft link to it in this 
directory:

$ cd rdfextras/test/test_sparql/DAWG
$ ln -s ../../data-r2 .

The file `test.py` should be run from the command line. It checks the SPARQL 
parsing against the results of evaluating the parsed expression.

Similar soft links can be established in the DAWG subdirectories of 

rdfexras/test/test_sparql2sql and rdfextras/test/test_ccfsparql