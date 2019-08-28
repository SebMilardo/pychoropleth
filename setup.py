from distutils.core import setup
import setuptools


setup(name='pychoropleth',
    version='0.2.2',
    description='A simple library to create choropleth maps from geopandas dataframes using mplleaflet',
    packages=setuptools.find_packages(),
    author='Sebastiano Milardo',
    author_email='milardo@mit.edu',
    license = 'MIT',
    install_requires = ['mplleaflet','matplotlib','pandas','numpy','geopandas','shapely','osmnx','descartes'],
    url = 'https://github.com/SebMilardo/pychoropleth',
    project_urls={
        'source': 'https://github.com/SebMilardo/pychoropleth/',
    },
    zip_safe=False,
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
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
    )
