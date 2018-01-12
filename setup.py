from setuptools import setup, find_packages
from codecs import open
from os import path

# Utility function to read the README file.
# Used for the long_description.
def read(fname):
    return open(path.join(path.dirname(__file__), fname)).read()

setup(
    name='arc_utils',
    version='0.6',
    description="Python utilities for use with Esri ArcGIS Desktop software",
    long_description=read('README.md'),
    url='https://github.com/gdherbert/arc_utils',
    author='Grant Herbert',
    author_email='gdherbert@gmail.com',
    keywords='esri arcpy arcgis',
    packages=find_packages()
    )