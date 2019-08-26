from distutils.core import setup
import setuptools

classifiers = ['Development Status :: 3 - Alpha',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: MIT License',
    'Natural Language :: English',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Programming Language :: Python :: 3']


setup(name='pychoropleth',
    version='0.1',
    description='A simple library to create choropleth maps from geopandas dataframes using mplleaflet',
    author='Sebastiano Milardo',
    author_email='milardo@mit.edu',
    license = 'MIT',
    install_requires = ['mplleaflet','matplotlib','pandas','numpy','geopandas','shapely','osmnx','geopy','descartes','openpyxl'],
    url = 'https://github.com/SebMilardo/pychoropleth',
    zip_safe=False
    )
