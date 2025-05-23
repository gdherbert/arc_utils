from setuptools import setup, find_packages
from codecs import open
from pathlib import Path

# Utility function to read the README file.
# Used for the long_description.
this_directory = Path(__file__).parent.resolve()
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name='arc_utils',
    version='1.1',
    description="Python utilities for use with Esri ArcGIS Desktop, ArcGIS Pro software",
    license='License:: MIT',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/gdherbert/arc_utils',
    author='Grant Herbert',
    author_email='gdherbert@gmail.com',
    keywords='esri arcpy arcgis',
    download_url = 'https://github.com/gdherbert/arc_utils/tree/1.0',
    classifiers=[
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/ArcGIS Pro',
        'Programming Language :: Python',
        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',
        'Environment :: Win64 (MS Windows)',
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.6'
    ],
    packages=find_packages()
    )