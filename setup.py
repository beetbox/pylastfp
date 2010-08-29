from distutils.core import setup
from distutils.command import sdist
from distutils.extension import Extension
import os
import sys

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
INC_DIRS = ['/opt/local/include']

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
        print 'We need Cython to build a source distribution.'
        sys.exit(1)
    from Cython.Compiler import Main
    Main.compile(
        [s for s in ext.sources if s.endswith('.pyx')],
        cplus = True,
    )

setup(
    name = 'pylastfp',
    version = '0.1',
    description = "bindings for Last.fm's acoustic fingerprinting (fplib)",
    author = 'Adrian Sampson',
    author_email = 'adrian@radbox.org',
    url = 'http://beets.radbox.org/pylastfp/',
    license = 'LGPL',
    platforms = 'ALL',
    long_description = _read('README.rst'),

    cmdclass = cmdclass,
    ext_modules = [ext],
    
    packages = ['lastfp'],
)
