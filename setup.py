"""
Command line script to transform your journal to html or some other format.

Basic usage::

    dayone_export [--output FILE] [opts] JOURNAL

For more information::

    dayone_export --help

Full documentation is available at http://day-one-export.readthedocs.org.
"""

import sys
try:
    from setuptools import setup
except ImportError:
    sys.exit("""Error: Setuptools is required for installation.
 -> http://pypi.python.org/pypi/setuptools
 or http://pypi.python.org/pypi/distribute""")

extra = {}
if sys.version_info >= (3,):
    extra['use_2to3'] = True

setup(
    name = "dayone_export",
    version = '0.6.1',
    description = "Export Day One journal using Jinja2 templates",
    author = "Nathan Grigg",
    author_email = "nathan@nathanamy.org",
    packages = ["dayone_export"],
    package_data={'dayone_export': ['templates/*']},
    include_package_data = True,
    url = 'https://github.com/nathangrigg/dayone_export/',
    entry_points = {
        'console_scripts': ['dayone_export = dayone_export.cli:run']
    },
    license = "BSD",
    zip_safe = False,
    long_description = __doc__,
    install_requires = ['Jinja2>=2.6',
                        'pytz',
                        'python-dateutil>=2.1',
                        'Markdown>=2.2.0'],
    classifiers = [
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: BSD License",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX",
        "Topic :: Office/Business :: News/Diary",
        "Topic :: Sociology :: History",
        "Topic :: Text Processing :: Markup :: HTML",
        "Topic :: Utilities",
        "Topic :: Text Processing :: General"
        ],
    **extra
)
