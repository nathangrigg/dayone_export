# Notice

This tool is not compatible with the Day One 2.0 journal format.

# Introduction

Export [Day One][0] journal entries into html, text, or another format
using a Jinja template.

by Nathan Grigg

[![Build status][statusimage]][statuslink]

[statusimage]: https://api.travis-ci.org/nathangrigg/dayone_export.png?branch=master
[statuslink]: https://travis-ci.org/nathangrigg/dayone_export

# Installation

Use [pip][4]:

    pip install dayone_export

You can also use easy install
(`easy_install dayone_export`)
or download the source and install
(`python setup.py install`).


Depending on how your Python installation is configured, you may
need extra permissions to install packages. If so, prefix the
installation command by `sudo` and a space.

Any of these methods will also install the dependencies
[Jinja2][1], [pytz][2], [python-dateutil][6], and  [Markdown][3].

# Quick start

Export your entire journal with

    dayone_export --output journal.html /path/to/Journal.dayone

To see available options, run

    dayone_export --help

# Custom templates and advanced options

You can specify a custom template using the command line option `--template`.

You can permanently override the default template by creating a new template named `default.html` and saving it in the folder `~/.dayone_export`.

Full documentation and information about creating new templates is available at [Read the Docs][5].


[0]: http://dayoneapp.com
[1]: http://jinja.pocoo.org
[2]: http://pytz.sourceforge.net
[3]: http://freewisdom.org/projects/python-markdown/
[4]: http://www.pip-installer.org/en/latest/index.html
[5]: http://day-one-export.readthedocs.org/
[6]: http://labix.org/python-dateutil
