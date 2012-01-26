#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import re

def setup_python3():
    # Taken from "distribute" setup.py
    from distutils.filelist import FileList
    from distutils import dir_util, file_util, util, log
    from os.path import join
  
    tmp_src = join("build", "src")
    log.set_verbosity(1)
    fl = FileList()
    for line in open("MANIFEST.in"):
        if not line.strip():
            continue
        fl.process_template_line(line)
    dir_util.create_tree(tmp_src, fl.files)
    outfiles_2to3 = []
    for f in fl.files:
        outf, copied = file_util.copy_file(f, join(tmp_src, f), update=1)
        if copied and outf.endswith(".py"):
            outfiles_2to3.append(outf)
  
    util.run_2to3(outfiles_2to3)
  
    # arrange setup to use the copy
    sys.path.insert(0, tmp_src)

    return tmp_src

# Find version. We have to do this because we can't import it in Python 3 until
# its been automatically converted in the setup process.
def find_version(filename):
    _version_re = re.compile(r'__version__ = "(.*)"')
    for line in open(filename):
        version_match = _version_re.match(line)
        if version_match:
            return version_match.group(1)

__version__ = find_version('rdfextras/__init__.py')

config = dict(
    name = 'rdfextras',
    version = __version__,
    description = "RDFExtras provide tools, extra stores and such for RDFLib.",
    author = "Niklas Lindström",
    author_email = "lindstream@gmail.com",
    url = "http://code.google.com/p/rdfextras/",
    license = "BSD",
    platforms = ["any"],
    classifiers = ["Programming Language :: Python",
                   "License :: OSI Approved :: BSD License",
                   "Topic :: Software Development :: Libraries :: Python Modules",
                   "Operating System :: OS Independent",
                   ],
    packages = ['rdfextras',
                'rdfextras.parsers',
                'rdfextras.serializers',
                'rdfextras.sparql',
                'rdfextras.sparql.results',
                'rdfextras.store',
                'rdfextras.store.FOPLRelationalModel',
                'rdfextras.tools',
                'rdfextras.utils',
                'rdfextras.web',],
    package_dir = { 'rdfextras.web': 'rdfextras/web' },
    package_data = { 'rdfextras.web': ['templates/*.html','static/*',]}
)

if sys.version_info[0] >= 3:
    from setuptools import setup
    config.update({'use_2to3': True})
    config.update({'src_root': setup_python3()})
else:
    try:
        from setuptools import setup
        config.update({'test_suite' : "nose.collector"})
    except ImportError:
        from distutils.core import setup


install_requires = [
    'rdflib >= 3.2.0',
    'pyparsing'
]

tests_require = install_requires + \
                []
                # ['flask', 'mimeparse']

extras_require = { 
    "WebApp": ["flask","mimeparse"],
    "SPARQLStore": ["SPARQLWrapper"],
    }


config.update(
    entry_points = {
        'console_scripts': [
            'rdfpipe = rdfextras.tools.rdfpipe:main',
            'csv2rdf = rdfextras.tools.csv2rdf:main',
            'rdf2dot = rdfextras.tools.rdf2dot:main',
            'rdfs2dot = rdfextras.tools.rdfs2dot:main',
            'sparqlendpointapp = rdfextras.web.endpoint:main',
            'rdflodapp = rdfextras.web.lod:main',                
        ],
        'nose.plugins': [
            'EARLPlugin = rdfextras.tools.EARLPlugin:EARLPlugin',
        ],
        'rdf.plugins.parser': [
            'rdf-json = rdfextras.parsers.rdfjson:RdfJsonParser',
            'json-ld = rdfextras.parsers.jsonld:JsonLDParser'
        ],
        'rdf.plugins.serializer': [
            'rdf-json = rdfextras.serializers.rdfjson:RdfJsonSerializer',
            'json-ld = rdfextras.serializers.jsonld:JsonLDSerializer',
            'html = rdfextras.sparql.results.htmlresults:HTMLSerializer',
        ],
        'rdf.plugins.queryprocessor': [
            'sparql = rdfextras.sparql.processor:Processor',
        ],
        'rdf.plugins.queryresult': [
            'sparql = rdfextras.sparql.query:SPARQLQueryResult',
        ],
        'rdf.plugins.resultserializer': [
            'html = rdfextras.sparql.results.htmlresults:HTMLResultSerializer',
            'xml = rdfextras.sparql.results.xmlresults:XMLResultSerializer',
            'json = rdfextras.sparql.results.jsonresults:JSONResultSerializer',
        ],
        'rdf.plugins.resultparser': [
            'xml = rdfextras.sparql.results.xmlresults:XMLResultParser',
            'json = rdfextras.sparql.results.jsonresults:JSONResultParser',
        ],
        'rdf.plugins.store': [
            'BerkeleyDB = rdfextras.store.BerkeleyDB:BerkeleyDB',
            'BDBOptimized = rdfextras.store.BDBOptimized:BDBOptimized',
            'MySQL = rdfextras.store.MySQL:MySQL',
            'PostgreSQL = rdfextras.store.PostgreSQL:PostgreSQL',
            'SPARQL = rdfextras.store.SPARQL:SPARQLStore',
            'SQLite = rdfextras.store.SQLite:SQLite',
            'ZODB = rdfextras.store.ZODB:ZODBGraph',
            'KyotoCabinet = rdfextras.store.KyotoCabinet:KyotoCabinet',
        ],

    },
    #namespace_packages = ['rdfextras'], # TODO: really needed?
    install_requires = install_requires,
    tests_require = tests_require,
    extras_require = extras_require 
)
    
setup(**config)

