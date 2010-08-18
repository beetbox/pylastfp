from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
import os

def _read(fn):
    path = os.path.join(os.path.dirname(__file__), fn)
    return open(path).read()

ext = Extension(
    "_fplib",
    ["fplib.pyx"],
    language="c++",
    include_dirs=['../fplib/include'],
    libraries=["stdc++", "samplerate", "fftw3f"],
    extra_objects=["../fplib/liblastfmfp_static.a"],
)

setup(
    name = 'pylastfp',
    version = '0.1',
    description = "bindings for Last.fm's acoustic fingerprinting (fplib)",
    author = 'Adrian Sampson',
    author_email = 'adrian@radbox.org',
    url = 'http://beets.radbox.org/pylastfp/',
    license = 'MIT',
    platforms = 'ALL',
    long_description = _read('README.rst'),

    cmdclass = {'build_ext': build_ext},
    ext_modules = [ext],
    
    py_modules = ['lastfp'],
)
