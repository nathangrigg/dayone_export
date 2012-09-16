"""
Command line script to transform your journal to html or some other format.

Basic usage::

    dayone_export [opts] [--timezone ZONE] JOURNAL

For more information::

    dayone_export --help
"""

from setuptools import setup

setup(
    name = "dayone_export",
    version = "0.1.0",
    description = "Export Day One journal using Jinja2 template",
    author = "Nathan Grigg",
    author_email = "nathan@nathanamy.org",
    packages = ["dayone_export"],
    package_data={'dayone_export': ['templates/*']},
    scripts = ['bin/dayone_export'],
    license = "BSD",
    zip_safe = False,
    long_description = __doc__,
    install_requires = ['Jinja2>=2.6', 'times==0.5', 'Markdown>=2.2.0'],
    classifiers = [
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: BSD License",
        "Environment :: Console"
        ]
)
