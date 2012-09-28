# Copyright (c) 2012, Nathan Grigg
# All rights reserved.
# BSD License

import os
import sys
import base64
import pytz
from StringIO import StringIO

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
'markdown': 'Warning: Cannot load markdown module. Leaving text as it is.',
'imgbase64': 'Warning: Cannot load Python Imaging Library. Encoding full-size images.'
})

#############################
# Markdown
#############################
try:
    import markdown
except ImportError:
    def markup(text, *args, **kwargs):
        warn_once('markdown')
        return text
else:
    def markup(text, *args, **kwargs):
        return markdown.markdown(text, *args, **kwargs)


#############################
# Date formatting
#############################
def format(value, fmt='%A, %b %e, %Y', tz=None):
    if tz:
        value = value.astimezone(pytz.timezone(tz))
    return value.strftime(fmt)

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
        output = StringIO.StringIO()
        im.save(output, "jpeg")  # we assume that we get best compressions with jpeg
        base64data = output.getvalue().encode("base64")
        return "data:image/jpeg;base64,%s" % (base64data)
