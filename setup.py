from __future__ import print_function
import os
import sys

# Work around Setuptools' broken (Cython-unaware) monkeypatching
# to support Pyrex. I don't want to use Setuptools in this file, but it
# is used automatically (and automatically monkeypatches) if we're
# installed, for example, with pip.
try:
    import setuptools.dist
    import setuptools.extension
except ImportError:
    pass
else:
    setuptools.extension.Extension.__init__ = \
        setuptools.dist._get_unpatched(setuptools.extension.Extension).__init__

from setuptools import setup
from distutils.command import sdist
from distutils.extension import Extension

# Import and use Cython if available.
try:
    from Cython.Distutils import build_ext as build_pyx
    HAVE_CYTHON = True
except ImportError:
    HAVE_CYTHON = False

def _read(fn):
    path = os.path.join(os.path.dirname(__file__), fn)
    return open(path).read()

# Search far and wide for the dependencies.
INC_DIRS = ['/opt/local/include', os.path.expanduser('~/.brew/include')]

ext = Extension(
    "lastfp._fplib",
    [
        "fplib.pyx",
        "fplib/src/Filter.cpp",
        "fplib/src/FingerprintExtractor.cpp",
        "fplib/src/OptFFT.cpp",
    ],
    language="c++",
    include_dirs=['fplib/include'] + INC_DIRS,
    libraries=["stdc++", "samplerate", "fftw3f"],
)

# If we don't have Cython, build from *.cpp instead of the Cython
# source. Also, if we do have Cython, make sure we use its build
# command.
cmdclass = {}
if HAVE_CYTHON:
    cmdclass['build_ext'] = build_pyx
else:
    ext.sources[0] = 'fplib.cpp'

# This silly hack, inspired by the pymt setup.py, runs Cython if we're
# doing a source distribution. The MANIFEST.in file ensures that the
# C++ source is included in the tarball also.
if 'sdist' in sys.argv:
    if not HAVE_CYTHON:
        print('We need Cython to build a source distribution.')
        sys.exit(1)
    from Cython.Compiler import Main
    source = ext.sources[0] # hacky!
    Main.compile(
        source,
        cplus = True,
        full_module_name = ext.name,
    )

setup(
    name = 'pylastfp',
    version = '0.6',
    description = "bindings for Last.fm's acoustic fingerprinting (fplib)",
    author = 'Adrian Sampson',
    author_email = 'adrian@radbox.org',
    url = 'http://github.com/sampsyo/pylastfp/',
    license = 'LGPL',
    platforms = 'ALL',
    long_description = _read('README.rst'),
    classifiers = [
        'Topic :: Multimedia :: Sound/Audio :: Analysis',
        'License :: OSI Approved :: GNU Library or Lesser General '
        'Public License (LGPL)',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
    ],

    install_requires = ['audioread'],

    cmdclass = cmdclass,
    ext_modules = [ext],
    
    packages = ['lastfp'],
    scripts = ['lastmatch.py'],
)
