# -*- coding: utf-8 -*-
'''
Created on 2014/3/11

@author: Hung-Hsin Chen
python setup.py build_ext --inplace

'''
from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize
import numpy as np


extensions = [
    Extension("HKW", ["HKW.pyx"],
              include_dirs = [np.get_include()]
            ),
]

setup(
  name = 'HKW',
  ext_modules = cythonize(extensions),
) 