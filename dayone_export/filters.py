# Copyright (c) 2012, Nathan Grigg
# All rights reserved.
# BSD License

import os
import re
import sys
import base64
import pytz
import markdown
from io import BytesIO

MARKER = 'zpoqjd_marker_zpoqjd'
RE_PERCENT_MINUS = re.compile(r'(?<!%)%-')
RE_REMOVE_MARKER = re.compile(MARKER + '0*')

class WarnOnce(object):
    """Issue a warning only one time.

    >>> warn_once = WarnOnce({'foo': 'bar'})
    >>> warn_once('foo')
    (print to stderr) bar

    >>> warn_once('foo')
    (nothing happens)
    """
    def __init__(self, warnings):
        self.warnings = warnings
        self.issued = dict((k, False) for k in warnings)

    def __call__(self, warning):
        if not self.issued[warning]:
            self.issued[warning] = True
            sys.stderr.write(self.warnings[warning] + '\n')

warn_once = WarnOnce({
'imgbase64': 'Warning: Cannot load Python Imaging Library. Encoding full-size images.'
})

#############################
# Markdown
#############################

def markdown_filter(autobold=False, nl2br=False):
    """Returns a markdown filter"""
    extensions = ['footnotes',
                  'tables',
                  'smart_strong',
                  'fenced_code',
                  'attr_list',
                  'def_list',
                  'abbr',
                  'dayone_export.mdx_hashtag',
                  'dayone_export.mdx_urlize',
                 ]

    if autobold:
        extensions.append('dayone_export.mdx_autobold')

    if nl2br:
        extensions.append('nl2br')

    md = markdown.Markdown(extensions=extensions,
      extension_configs={'footnotes': [('UNIQUE_IDS', True)]},
      output_format='html5')

    def markup(text, *args, **kwargs):
        md.reset()
        return md.convert(text)

    return markup


#############################
# Date formatting
#############################
def format(value, fmt='%A, %b %-d, %Y', tz=None):
    """Format a date or time."""

    if tz:
        value = value.astimezone(pytz.timezone(tz))
    try:
        return value.strftime(fmt)
    except ValueError:
        return _strftime_portable(value, fmt)

def _strftime_portable(value, fmt='%A, %b %-d, %Y'):
    marked = value.strftime(RE_PERCENT_MINUS.sub(MARKER + "%", fmt))
    return RE_REMOVE_MARKER.sub("", marked)


#############################
# Escape Latex (http://flask.pocoo.org/snippets/55/)
#############################
LATEX_SUBS = (
    (re.compile(r'\\'), r'\\textbackslashzzz'),
    (re.compile(r'([{}_#%&$])'), r'\\\1'),
    (re.compile(r'~'), r'\\textasciitilde{}'),
    (re.compile(r'\^'), r'\\textasciicircum{}'),
    (re.compile(r'"'), r"''"),
    (re.compile(r'\.\.\.+'), r'\\ldots'),
    (re.compile(r'\\textbackslashzzz'), r'\\textbackslash{}'),
)

def escape_tex(value):
    newval = value
    for pattern, replacement in LATEX_SUBS:
        newval = pattern.sub(replacement, newval)
    return newval


#############################
# Base64 encode images
#############################
try:
    from PIL import Image
except ImportError:
    # if we don't have PIL available, include the image in its
    # original size
    def imgbase64(infile, max_size=None, dayone_folder=None):
        warn_once('imgbase64')
        filename, ext = os.path.splitext(infile)
        with open(dayone_folder + "/" + infile, "rb") as image_file:
            base64data = base64.b64encode(image_file.read())
            return "data:image/%s;base64,%s" % (ext[1:], base64data)
else:
    # if we have PIL, resize the image
    def imgbase64(infile, max_size=400, dayone_folder=None):
        size = max_size, max_size
        filename, ext = os.path.splitext(infile)
        im = Image.open(dayone_folder + "/" + infile)
        im.thumbnail(size, Image.ANTIALIAS)
        output = BytesIO()
        im.save(output, "jpeg")  # we assume that we get best compressions with jpeg
        base64data = output.getvalue().encode("base64")
        return "data:image/jpeg;base64,%s" % (base64data)
