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
                'rdfextras.tools',
                'rdfextras.sparql',
                ],
)

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
else:
    config.update(
        entry_points = {
            'console_scripts': [
                'rdfpipe = rdfextras.tools.rdfpipe:main',
            ],
            'nose.plugins': [
                'EARLPlugin = rdfextras.tools.EARLPlugin:EARLPlugin',
            ]
        },
        #test_suite = 'nose.collector',
        #namespace_packages = ['rdfextras'], # TODO: really needed?
        #install_requires = [
        #    'rdflib >= 3.0',
        #    'pyparsing'
        #],
    )

setup(**config)

