from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

ext = Extension(
    "fplib",
    ["fplib.pyx"],
    language="c++",
    include_dirs=['../fplib/include'],
    libraries=["stdc++", "samplerate", "fftw3f"],
    extra_objects=["../fplib/liblastfmfp_static.a"],
)

setup(
    name = 'pyfplib',
    cmdclass = {'build_ext': build_ext},
    ext_modules = [ext],
)
