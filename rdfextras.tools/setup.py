#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from distutils.core import setup

from rdfextras.tools import __version__

setup(
    name = 'rdfextras.tools',
    version = __version__,
    description = "The RDFExtras Tools use RDFLib and provide cmdlines etc. for RDF usage.",
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
    packages = ['rdfextras.tools'],
    )

