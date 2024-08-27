"""
Cython setup file for vf.pyx

@author = cdeline  12/6/17
http://cython.readthedocs.io/en/latest/src/userguide/source_files_and_compilation.html#compilation

"""

from setuptools import setup
from setuptools import Extension
#from distutils.core import setup
#from distutils.extension import Extension
from Cython.Build import cythonize

try:
    setup(ext_modules=cythonize('vf_fast.pyx')    )
except:
    pass

setup(ext_modules=[Extension("vf_fast", ["vf_fast.c"])]       )

# compile by running from command prompt: python setup.py build_ext --inplace
# if you get a vcvarsall.bat error, install C++ for Python :  https://github.com/cython/cython/wiki/CythonExtensionsOnWindows