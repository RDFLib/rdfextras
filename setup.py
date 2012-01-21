#!/usr/bin/env python
# -*- coding: utf-8 -*-
from rdfextras import __version__

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
                'rdfextras.tools',
                'rdfextras.sparql',
                'rdfextras.sparql.results',
                'rdfextras.store',
		'rdfextras.web',],
    package_dir = { 'rdfextras.web': 'rdfextras/web' },
    package_data={ 'rdfextras.web': [
            'templates/*.html',
            'static/*',
]}

)

install_requires = [
    'rdflib >= 3.2.0',
    'pyparsing'
]
tests_require = install_requires + \
                ['flask', 'mimeparse', 'jinja2']

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
else:
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
            ],
            'rdf.plugins.serializer': [
                'rdf-json = rdfextras.serializers.rdfjson:RdfJsonSerializer',
            ],
        },
        #test_suite = 'nose.collector',
        #namespace_packages = ['rdfextras'], # TODO: really needed?
        install_requires = install_requires,
        tests_require = tests_require,
        extras_require = { 
            "WebApp": ["flask","mimeparse"],
            "SPARQLStore": ["SPARQLWrapper"],
            }
     )
    
setup(**config)

