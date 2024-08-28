from setuptools import setup
from setuptools.glob import glob
from mypyc.build import mypycify

files = glob('src/**/*.py', recursive=True)
setup(ext_modules=mypycify(files))
