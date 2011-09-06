r"""
======
apigen
======

This extension automatically generates API documentation.  To use it:

1) Include `'mmf.sphinx.ext.apigen'` in the `extensions` list in your
   :file:`conf.py` file.

   .. note:: This extension must be installed *before* the
      :ext:`sphinx.ext.autosummary` extension.

2) Set the configuration option :confval:`apigen_packages` to a list
   of packages for which you would like to generate.  These must be
   importable.
3) Specify :confval:`apigen_outdir` as the output directory.  The
   default is in the `doctreedir/_generated/api` but it is probably
   better if you set this explicitly.
4) Include the :file:`index_*` files in a :rst:dir:`toctree`
   directive::

   .. toctree::
      :maxdepth: 2
      :glob:

      _build/_generated/api/index_*

   This will generate the full API.

The following config values control the generation of the API
documentation.

.. confval:: apigen_packages
   
   This should be a list of importable package names.  The API
   documentation will be generated for these.

.. confval:: apigen_outdir
   
   The documentation will be placed in this directory (default is the
   `$(doctreedir)/_generated/api` directory.)

.. confval:: apigen_package_skip_patterns
   
   None or sequence of {strings, regexps}. Sequence of strings giving
   URIs of packages to be excluded.  Operates on the package path,
   starting at (including) the first dot in the package path, after
   *package_name* - so, if *package_name* is ``sphinx``, then
   ``sphinx.util`` will result in ``.util`` being passed for searching by these
   regexps.  If is None, gives default. Default is: ``['\.tests$']``

.. confval:: apigen_module_skip_patterns

   None or sequence. Sequence of strings giving URIs of modules to be
   excluded Operates on the module name including preceding URI path,
   back to the first dot after *package_name*.  For example
   ``sphinx.util.console`` results in the string to search of
   ``.util.console`` If is None, gives default. Default is:
   ``['\.setup$', '\._']``

.. confval:: apigen_label
   If `True`, then section labels "Modules", "Classes", "Functions"
   etc. will be generated, otherwise, the type can be inferred from
   the name: Modules will have a "."  prepended, interfaces start with
   "I", classes have nothing, and functions end in "()".

.. confval:: apigen_autosummary
   If `True`, then an :ext:`sphinx.ext.autosummary` table will be
   generated at the start of each module summarizing the contents.

.. confval:: apigen_headings
   If `True`, then each function, class, interface, and module will
   appear as a heading so that the structure appears in the table of
   contents.  This is somewhat redundant though.

.. confval:: apigen_inherited_members
   If `True`, then inherited members of each class will be included, otherwise,
   the user must follow the links to the base class.  Default is `False`.

.. todo:: We presently exclude extension modules.

   To include extension modules, first identify them as valid in the
   ``_uri2path`` method, then handle them in the ``_parse_module``
   script.

We get functions and classes by parsing the text of `.py` files.
Alternatively we could import the modules for discovery, and we'd have
to do that for extension modules.  This would involve changing the
``_parse_module`` method to work via import and introspection, and
might involve changing ``discover_modules`` (which determines which
files are modules, and therefore which module URIs will be passed to
``_parse_module``).

.. note:: This is a modified version of a script originally shipped
   with NIPY which in tern was a modified version of a script
   originally shipped with the PyMVPA project.  PyMVPA is an
   MIT-licensed project.

.. warning:: We monkey-patch autodoc.py a bit to get things working.  See
   :class:`MonkeypatchAutodoc`.

"""
import sys
import os
import re
import inspect
import logging
import traceback

from sphinx.errors import ExtensionError

try:
    import zope.interface
    def isinterface(obj):
        return isinstance(obj,
                          zope.interface.interface.InterfaceClass)
except ImportError:
    def isinterface(obj):
        return False

try:
    _d = OrderedDict()
except:
    from mmf.contrib.odict import odict as OrderedDict

def isclass(obj):
    return inspect.isclass(obj) and not isinterface(obj)

# Functions and classes
class _ApiDocWriter(object):
    ''' Class for automatic detection and parsing of API docs
    to Sphinx-parsable reST format.  This is the original version, and it does
    not import the modules.  Instead, it parses the files, looking for the
    relevant material.'''

    # only separating first two levels
    rst_section_levels = ['*', '=', '-', '~', '^']

    def __init__(self,
                 package_name,
                 rst_extension='.rst',
                 package_skip_patterns=None,
                 module_skip_patterns=None,
                 labels=False,
                 autosummary=True,
                 inherited_members=False,
                 headings=False,
                 ):
        ''' Initialize package for parsing

        Parameters
        ----------
        package_name : string
            Name of the top-level package.  *package_name* must be the
            name of an importable package
        rst_extension : string, optional
            Extension for reST files, default '.rst'
        package_skip_patterns : None or sequence of {strings, regexps}
            Sequence of strings giving URIs of packages to be excluded
            Operates on the package path, starting at (including) the
            first dot in the package path, after *package_name* - so,
            if *package_name* is ``sphinx``, then ``sphinx.util`` will
            result in ``.util`` being passed for searching by these
            regexps.  If is None, gives default. Default is:
            ['\.tests$']
        module_skip_patterns : None or sequence
            Sequence of strings giving URIs of modules to be excluded
            Operates on the module name including preceding URI path,
            back to the first dot after *package_name*.  For example
            ``sphinx.util.console`` results in the string to search of
            ``.util.console``
            If is None, gives default. Default is:
            ['\.setup$', '\._']
        labels : bool
            If `True`, then section labels "Modules", "Classes",
            "Functions" etc. will be generated, otherwise, the type
            can be inferred from the name: Modules will have a "."
            prepended, interfaces start with "I", classes have
            nothing, and functions end in "()".
        autosummary : bool
            If `True`, then an :ext:`sphinx.ext.autosummary` table
            will be generated at the start of each module summarizing
            the contents.
        inherited_members : bool
            If `True`, then inherited members of each class will be included,
            otherwise, the user must follow the links to the base class.
            Default is `False`.
        headings : bool
            If `True`, then each function, class, interface, and
            module will appear as a heading so that the structure
            appears in the table of contents.  This is somewhat
            redundant though.
        '''
        if package_skip_patterns is None:
            package_skip_patterns = ['\\.tests$']
        if module_skip_patterns is None:
            module_skip_patterns = ['\\.setup$', '\\._']
        self.package_name = package_name
        self.rst_extension = rst_extension
        self.package_skip_patterns = package_skip_patterns
        self.module_skip_patterns = module_skip_patterns
        self.labels = labels
        self.autosummary = autosummary
        self.inherited_members = inherited_members
        self.headings = headings

    def get_package_name(self):
        return self._package_name

    def set_package_name(self, package_name):
        r""" Set package_name

        >>> docwriter = ApiDocWriter('sphinx')
        >>> import sphinx
        >>> docwriter.root_path == sphinx.__path__[0]
        True
        >>> docwriter.package_name = 'docutils'
        >>> import docutils
        >>> docwriter.root_path == docutils.__path__[0]
        True
        """
        # It's also possible to imagine caching the module parsing here
        self._package_name = package_name
        self.root_module = __import__(package_name)
        if hasattr(self.root_module, '__path__'):
            self.root_path = self.root_module.__path__[0]
        else:
            self.root_path = self.root_module.__file__
        self.written_modules = None

    package_name = property(get_package_name, set_package_name, None,
                            'get/set package_name')

    def _get_object_name(self, line):
        ''' Get second token in line
        >>> docwriter = ApiDocWriter('sphinx')
        >>> docwriter._get_object_name("  def func():  ")
        'func'
        >>> docwriter._get_object_name("  class Klass(object):  ")
        'Klass'
        >>> docwriter._get_object_name("  class Klass:  ")
        'Klass'
        '''
        name = line.split()[1].split('(')[0].strip()
        # in case we have classes which are not derived from object
        # ie. old style classes
        return name.rstrip(':')

    def _uri2path(self, uri):
        ''' Convert uri to absolute filepath

        Parameters
        ----------
        uri : string
            URI of python module to return path for

        Returns
        -------
        path : None or string
            Returns None if there is no valid path for this URI
            Otherwise returns absolute file system path for URI

        Examples
        --------
        >>> docwriter = ApiDocWriter('sphinx')
        >>> import sphinx
        >>> modpath = sphinx.__path__[0]
        >>> res = docwriter._uri2path('sphinx.builder')
        >>> res == os.path.join(modpath, 'builder.py')
        True
        >>> res = docwriter._uri2path('sphinx')
        >>> res == os.path.join(modpath, '__init__.py')
        True
        >>> docwriter._uri2path('sphinx.does_not_exist')

        '''
        if uri == self.package_name:
            return os.path.join(self.root_path, '__init__.py')
        path = uri.replace('.', os.path.sep)
        path = path.replace(self.package_name + os.path.sep, '')
        path = os.path.join(self.root_path, path)
        # XXX maybe check for extensions as well?
        if os.path.exists(path + '.py'): # file
            path += '.py'
        elif os.path.exists(os.path.join(path, '__init__.py')):
            path = os.path.join(path, '__init__.py')
        else:
            return None
        return path

    def _path2uri(self, dirpath):
        ''' Convert directory path to uri '''
        relpath = dirpath.replace(self.root_path, self.package_name)
        if relpath.startswith(os.path.sep):
            relpath = relpath[1:]
        return relpath.replace(os.path.sep, '.')

    def _parse_module(self, uri):
        ''' Parse module defined in *uri* '''
        filename = self._uri2path(uri)
        if filename is None:
            # nothing that we could handle here.
            return ([],[],OrderedDict(),OrderedDict(),[])
        f = open(filename, 'rt')
        modules, functions, classes, interfaces, others = self._parse_lines(f)
        f.close()
        return modules, functions, classes, interfaces, others
    
    def _parse_lines(self, linesource):
        r""" Parse lines of text for modules, functions, classes, and
        interfaces."""
        modules = []
        functions = []
        private_functions = []
        classes = []
        private_classes = []
        interfaces = []
        for line in linesource:
            if line.startswith('def ') and line.count('('):
                # exclude private stuff
                name = self._get_object_name(line)
                if name.startswith('_'):
                    private_functions.append(name)
                else:
                    functions.append(name)
            elif line.startswith('class '):
                # exclude private stuff
                name = self._get_object_name(line)
                if name.startswith('_'):
                    private_classes.append(name)
                elif name.startswith('I') and name[1].isupper():
                    interfaces.append(name)
                else:
                    classes.append(name)
            else:
                pass
        private_functions.sort()
        functions.sort()
        functions.extend(private_functions)
        private_classes.sort()
        classes.sort()
        classes.extend(private_classes)
        interfaces.sort()
        classes = OrderedDict([(_k, None) for _k in classes])
        interfaces = OrderedDict([(_k, None) for _k in interfaces])
        return modules, functions, classes, interfaces

    def generate_api_doc(self, uri):
        '''Make autodoc documentation template string for a module

        Parameters
        ----------
        uri : string
            python location of module - e.g 'sphinx.builder'

        Returns
        -------
        S : string
            Contents of API doc
        '''
        logger = logging.getLogger("mmf.sphinx.ext.apigen")

        # get the names of all classes and functions
        (modules, functions, classes, interfaces,
         others) = self._parse_module(uri)
        if not (len(modules) + len(functions) + len(classes) +
                len(interfaces)):
            logger.warning("Empty api - '%s'" % uri)

        # Make a shorter version of the uri that omits the package name for
        # titles 
        uri_short = re.sub(r'^%s\.' % self.package_name,'',uri)
        
        ad = '.. AUTO-GENERATED FILE -- DO NOT EDIT!\n\n'

        if False:
            # Old code
            chap_title = uri_short
            ad += (chap_title+'\n'+ self.rst_section_levels[1] * len(chap_title)
                   + '\n\n')

            # Set the chapter title to read 'module' for all modules
            # except for the main packages
            if '.' in uri:
                title = 'Module: :mod:`' + uri + '`'
            else:
                title = ':mod:`' + uri + '`'
            ad += title + '\n' + self.rst_section_levels[2] * len(title)
        else:
            title = ':mod:`' + uri + '`'
            ad += title + '\n' + self.rst_section_levels[1] * len(title)
        
        ad += '\n\n.. currentmodule:: ' + uri + '\n\n'

        if self.autosummary and len(modules + functions 
                                    + classes.keys() + interfaces.keys()):
            ad += "\n.. autosummary::\n"
            ad += "\n"
            ad += "\n".join(
                ["\n".join("   " + _f for _f in modules)] +
                ["\n".join("   " + _f for _f in interfaces)] +
                ["\n".join("   " + _f for _f in classes)] +
                ["\n".join("   " + _f for _f in functions)])
            ad += "\n"

        has_inheritance = False
        for _c in classes.values() + interfaces.values():
            for _b in _c.__bases__:
                if _b is object:
                    continue
                else:
                    has_inheritance = True
                    break

        if has_inheritance:
            ad += '\nInheritance diagram for ``%s``:\n\n' % uri
            ad += '.. inheritance-diagram:: %s \n' % uri
            ad += '   :parts: 3\n'

        ad += '\n.. automodule:: ' + uri + '\n'

        if self.labels and modules:
            ad += '\n' + 'Modules' + '\n' + \
                  self.rst_section_levels[2] * 7 + '\n'

        for m in modules:
            if self.labels:
                m = "~" + ".".join([uri, m])
            else:
                m = ".%s<%s>" % (m, ".".join([uri, m]))
            if self.headings:
                ad += '\n:mod:`' + m + '`\n' \
                    + self.rst_section_levels[self.labels + 2] * \
                    (len(m) + 7) + '\n\n'

        if self.labels and interfaces:
            ad += '\n' + 'Interfaces' + '\n' + \
                  self.rst_section_levels[2] * 10 + '\n'

        for i in interfaces:
            if self.headings:
                ad += '\n:class:`' + i + '`\n' \
                    + self.rst_section_levels[self.labels + 2] * \
                    (len(i) + 9) + '\n\n'
            ad += '\n.. autointerface:: ' + i + '\n'
            # must NOT exclude from index to keep cross-refs working
            ad += '  :members:\n' \
                  '  :undoc-members:\n' \
                  '  :show-inheritance:\n'

            if self.inherited_members:
                ad += '  :inherited-members:\n'

        if self.labels and classes:
            ad += '\n' + 'Classes' + '\n' + \
                  self.rst_section_levels[2] * 7 + '\n'

        for c in classes:
            if self.headings:
                ad += '\n:class:`' + c + '`\n' \
                    + self.rst_section_levels[self.labels + 2] * \
                    (len(c) + 9) + '\n\n'
            ad += '\n.. autoclass:: ' + c + '\n'
            # must NOT exclude from index to keep cross-refs working
            ad += '  :members:\n' \
                  '  :undoc-members:\n' \
                  '  :show-inheritance:\n'
            if self.inherited_members:
                ad += '  :inherited-members:\n'

            if isinstance(classes[c], type):
                # New style class
                ad += '\n' \
                      '  .. automethod:: __init__\n'

        if self.labels and functions:
            ad += '\n' + 'Functions' + '\n' + \
                  self.rst_section_levels[2] * 9 + '\n\n'

        for f in functions:
            if self.headings:
                ad += '\n:func:`' + f + '`\n' \
                    + self.rst_section_levels[self.labels + 2] * \
                    (len(f) + 8) + '\n\n'
            # must NOT exclude from index to keep cross-refs working
            ad += '\n.. autofunction:: ' + uri + '.' + f + '\n\n'
        return ad

    def _survives_exclude(self, matchstr, match_type):
        ''' Returns True if *matchstr* does not match patterns

        ``self.package_name`` removed from front of string if present

        Examples
        --------
        >>> dw = ApiDocWriter('sphinx')
        >>> dw._survives_exclude('sphinx.okpkg', 'package')
        True
        >>> dw.package_skip_patterns.append('^\\.badpkg$')
        >>> dw._survives_exclude('sphinx.badpkg', 'package')
        False
        >>> dw._survives_exclude('sphinx.badpkg', 'module')
        True
        >>> dw._survives_exclude('sphinx.badmod', 'module')
        True
        >>> dw.module_skip_patterns.append('^\\.badmod$')
        >>> dw._survives_exclude('sphinx.badmod', 'module')
        False
        '''
        if match_type == 'module':
            patterns = self.module_skip_patterns
        elif match_type == 'package':
            patterns = self.package_skip_patterns
        else:
            raise ValueError('Cannot interpret match type "%s"' 
                             % match_type)
        # Match to URI without package name
        L = len(self.package_name)
        if matchstr[:L] == self.package_name:
            matchstr = matchstr[L:]
        for pat in patterns:
            try:
                pat.search
            except AttributeError:
                pat = re.compile(pat)
            if pat.search(matchstr):
                return False
        return True

    def discover_modules(self):
        ''' Return module sequence discovered from ``self.package_name`` 


        Parameters
        ----------
        None

        Returns
        -------
        mods : sequence
            Sequence of module names within ``self.package_name``

        Examples
        --------
        >>> dw = ApiDocWriter('sphinx')
        >>> mods = dw.discover_modules()
        >>> 'sphinx.util' in mods
        True
        >>> dw.package_skip_patterns.append('\.util$')
        >>> 'sphinx.util' in dw.discover_modules()
        False
        >>> 
        '''
        modules = [self.package_name]
        # raw directory parsing
        for dirpath, dirnames, filenames in os.walk(self.root_path):
            # Check directory names for packages
            root_uri = self._path2uri(os.path.join(self.root_path,
                                                   dirpath))
            for dirname in dirnames[:]: # copy list - we modify inplace
                package_uri = '.'.join((root_uri, dirname))
                if (self._uri2path(package_uri) and
                    self._survives_exclude(package_uri, 'package')):
                    modules.append(package_uri)
                else:
                    dirnames.remove(dirname)
            # Check filenames for modules
            for filename in filenames:
                if not filename.endswith(".py"):
                    continue
                module_name = filename[:-3]
                module_uri = '.'.join((root_uri, module_name))
                if (self._uri2path(module_uri) and
                    self._survives_exclude(module_uri, 'module')):
                    modules.append(module_uri)
        return sorted(modules)
    
    def write_modules_api(self, modules, outdir):
        # write the list
        written_modules = []
        for m in modules:
            api_str = self.generate_api_doc(m)
            if not api_str:
                continue

            outfile = os.path.join(outdir, m + self.rst_extension)
            self.write_if_changed(outfile, api_str)

            written_modules.append(m)
        self.written_modules = written_modules

    def write_api_docs(self, outdir):
        """Generate API reST files.

        Parameters
        ----------
        outdir : string
            Directory name in which to store files
            We create automatic filenames for each module
            
        Returns
        -------
        None

        Notes
        -----
        Sets self.written_modules to list of written modules
        """
        if not os.path.exists(outdir):
            os.makedirs(outdir)
        # compose list of modules
        modules = self.discover_modules()
        self.write_modules_api(modules,outdir)
        
    def write_index(self, outdir, froot='gen', relative_to=None):
        """Make a reST API index file from written files

        Parameters
        ----------
        path : string
            Filename to write index to
        outdir : string
            Directory to which to write generated index file
        froot : string, optional
            root (filename without extension) of filename to write to
            Defaults to 'gen'.  We add ``self.rst_extension``.
        relative_to : string
            path to which written filenames are relative.  This
            component of the written file path will be removed from
            outdir, in the generated index.  Default is None, meaning,
            leave path as it is.
        """
        if self.written_modules is None:
            raise ValueError('No modules written')

        # Get full filename path
        index_file_name = os.path.join(outdir, froot+self.rst_extension)
        
        # Path written into index is relative to rootpath
        if relative_to is not None:
            relative_to = relative_to.rstrip(os.path.sep)
            outdir = outdir.rstrip(os.path.sep) + os.path.sep
            relpath = outdir.replace(relative_to + os.path.sep, '')
        else:
            relpath = outdir
        
        lines = []
        w = lines.append
        w('.. AUTO-GENERATED FILE -- DO NOT EDIT!\n')
        w('*****************************')
        w(' Generated API Documentation')
        w('*****************************\n')
        w('.. toctree::\n')
        for f in self.written_modules:
            w('   %s' % os.path.join(relpath, f))
        
        self.write_if_changed(index_file_name, 
                              "\n".join(lines) + "\n")

    def write_if_changed(self, filename, contents):
        r"""Write the contents to file if they have changed, otherwise
        leave the file alone so as not to trigger a reformatting of
        the documentation."""
    
        # First check if outfile exists:
        old_contents = ""
        file = None
        try:
            file = open(filename, 'r')
            old_contents = file.read()
        except IOError:
            pass
        finally:
            if file:
                file.close()
                
        if old_contents != contents:
            # Only modify the file if something has changed to
            # prevent forcing the documentation to be re-typeset.
            file = open(filename, 'wt')
            file.write(contents)
            file.close()
        else:
            pass

class ApiDocWriter(_ApiDocWriter):
    r"""My version that actually imports the modules."""
    def _parse_module(self, uri):
        """Parse module defined in *uri*"""
        modules = []
        functions = []
        classes = OrderedDict()
        interfaces = OrderedDict()
        others = []
        
        __all__defined = False
        try:
            module = __import__(uri)
            _names = uri.split('.')[:0:-1]
            while _names:
                # __import__ returns the top level module.
                module = getattr(module, _names.pop())
           
            if hasattr(module, '__all__'):
                __all__ = getattr(module, '__all__')
                __all__defined = True
            else:
                __all__ = []
                logger = logging.getLogger("mmf.sphinx.ext.apigen")
                logger.warning(
                    "Module %s does not define '__all__': " % uri +
                    "(Generated docs will included all imported objects too!)")
            __dict__ = getattr(module, '__dict__', {})
        except Exception, err:
            logger = logging.getLogger("mmf.sphinx.ext.apigen")
            logger.warning("Could not import - " + uri)
            exc_type, exc_value, exc_traceback = sys.exc_info()
            logger.debug("\n".join(traceback.format_exception(
                        exc_type, exc_value, exc_traceback, limit=1)))
            logger.warning("\n".join(traceback.format_exception_only(
                        type(err), err)))

            __all__ = []
            __dict__ = {}
        
        if not __all__:
            # Respect __all__ but if not defined then get non-private
            # keys from dict.
            __all__ = [_k for _k in __dict__ if not _k.startswith('_')]

        for name in __all__:
            obj = getattr(module, name, NotImplemented)
            if obj is NotImplemented:
                try:            # Maybe it is a delayed module.  Try importing
                    obj = __import__(".".join([uri, name]))
                except:
                    pass

            if (obj is not NotImplemented 
                and (__all__defined 
                     or (getattr(obj, '__module__', module.__name__) 
                         == module.__name__))):
                # The last condition is that, unless __all__ is defined, we only
                # document object defined in the current module (as specified by
                # __module___.  Data members (things without __module__) are
                # always included.
                if inspect.ismodule(obj):
                    # Modules don't have __module__.  We check the name instead
                    # to see if it starts with module.__name__
                    if (__all__defined 
                        or obj.__name__.startswith(module.__name__)):
                        modules.append(name)
                elif inspect.isfunction(obj):
                    functions.append(name)
                elif isclass(obj):
                    classes[name] = obj
                elif isinterface(obj):
                    interfaces[name] = obj
                else:
                    others.append(name)

        return modules, functions, classes, interfaces, others        

def generate_api(app):
    r"""This function actually generates the API documentation."""
    base_path = app.srcdir

    logger = logging.getLogger("mmf.sphinx.ext.apigen")
    
    if app.config.apigen_outdir:
        outdir = app.config.apigen_outdir
        if not outdir.startswith(os.path.sep):
            outdir = os.path.join(base_path, outdir)
    else:
        outdir = os.path.join(app.doctreedir, '_generated', 'api')

    if app.config.apigen_packages:
        for package in app.config.apigen_packages:
            logger.info(
                "Generating documentation for package '%s'" % package)
            docwriter = ApiDocWriter(
                package,
                package_skip_patterns=app.config.apigen_package_skip_patterns,
                module_skip_patterns=app.config.apigen_module_skip_patterns,
                rst_extension=app.config.source_suffix,
                inherited_members=app.config.apigen_inherited_members
                )
            docwriter.write_api_docs(outdir)
            docwriter.write_index(outdir, 'index_' + package, 
                                  relative_to=outdir)
            app.info('[apigen] %d files written for package %s' 
                     % (len(docwriter.written_modules), package))
    else:
        app.warn("[apigen] No packages specified in `conf.py`.\n" +
                 "Please specify the list of packages `apigen_packages`")


import sphinx.ext.autodoc
class MonkeypatchAutodoc:
    r"""This fixes some behaviour in :mod:`sphinx.ext.autodoc` that causes our
    generated documentation to fail.  In particular:

    1) Some :meth:`sphinx.ext.autodoc.Documenter.can_document_member` instances
       treat `parent` as a :class:`sphinx.ext.autodoc.Documenter` whereas
       :mod:`sphinx.ext.autosummary` typically passes objects (such as
       modules).  Thus, functions in a module attempt to be documented by
       :class:`sphinx.ext.autodoc.MethodDocumenter` rather than 
       :class:`sphinx.ext.autodoc.FunctionDocumenter`.  This is fixed by
       :class:`MyDataDocumenter` and :class:`MyMethodDocumenter`
    2) :class:`sphinx.ext.autodoc.ModuleDocumenter` cannot document submodules
       for some reason (changed in sphinx revision 02f38aa14aaf).  I need this
       functionality, so I restore it in :class:`MyModuleDocumenter`.

       .. note:: As far as generating documentation, this is not needed if the
          sub-module is in `__all__`.  However, if it is not included, then in
          some other places I have had problems.  For example, module
          documentation will sometimes be passed to :mod:`numpydoc` with as an
          attribute or class, so :mod:`numpydoc` tries to parse it and complains
          about Unknown sections (object docstrings must have a specific set of
          sections, but module docstrings can have anything).
    """
    class MyModuleDocumenter(sphinx.ext.autodoc.ModuleDocumenter):
        @classmethod
        def can_document_member(cls, member, membername, isattr, parent):
            # Do document submodules!
            return inspect.ismodule(member)

    class MyAttributeDocumenter(sphinx.ext.autodoc.AttributeDocumenter):
        @classmethod
        def can_document_member(cls, member, membername, isattr, parent):
            # Do not allow Attribute Documenter to document modules.
            isdatadesc = sphinx.ext.autodoc.isdescriptor(member) and not \
                isinstance(member, cls.method_types)
            return isdatadesc or (not inspect.ismodule(parent)
                                  and not inspect.isroutine(member)
                                  and not inspect.ismodule(member)
                                  and not isinstance(
                    member, sphinx.ext.autodoc.class_types))

    class MyDataDocumenter(sphinx.ext.autodoc.DataDocumenter):
        @classmethod
        def can_document_member(cls, member, membername, isattr, parent):
            return inspect.ismodule(member) and isattr        

    class MyMethodDocumenter(sphinx.ext.autodoc.MethodDocumenter):
        @classmethod
        def can_document_member(cls, member, membername, isattr, parent):
            return (sphinx.ext.autodoc.MethodDocumenter.can_document_member(
                    member, membername, isattr, parent)
                    and not inspect.ismodule(parent))

def setup(app):
    r"""The guts of the extension. """
    if 'sphinx.ext.autosummary' in app._extensions:
        raise ExtensionError(
            "The 'mmf.sphinx.ext.apigen' extensions must be setup " +
            "*before* the 'sphinx.ext.autosummary' extension.\n" +
            "Please ensure that 'mmf.sphinx.ext.apigen' appears " +
            "earlier in the list of extensions.")

    logging.basicConfig(level=logging.INFO)
    app.add_config_value('apigen_packages', [], 'env')
    app.add_config_value('apigen_outdir', "", 'env')
    app.add_config_value('apigen_package_skip_patterns', None, 'env')
    app.add_config_value('apigen_module_skip_patterns', None, 'env')
    app.add_config_value('apigen_label', False, 'env')
    app.add_config_value('apigen_autosummary', True, 'env')
    app.add_config_value('apigen_inherited_members', False, 'env')
    app.add_config_value('apigen_headings', False, 'env')

    app.connect('builder-inited', generate_api)

    # I need autosummary loaded *after*
    app.setup_extension('sphinx.ext.autosummary')

    # My fixes to autodoc.
    app.setup_extension('sphinx.ext.autodoc')
    app.add_autodocumenter(MonkeypatchAutodoc.MyModuleDocumenter)
    app.add_autodocumenter(MonkeypatchAutodoc.MyMethodDocumenter)
    app.add_autodocumenter(MonkeypatchAutodoc.MyAttributeDocumenter)
    app.add_autodocumenter(MonkeypatchAutodoc.MyDataDocumenter)
