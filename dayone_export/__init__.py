#! /usr/bin/env python
#
# Copyright (c) 2012, Nathan Grigg
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
# * Neither the name of this package nor the
#   names of its contributors may be used to endorse or promote products
#   derived from this software without specific prior written permission.
#
# This software is provided by the copyright holders and contributors "as
# is" and any express or implied warranties, including, but not limited
# to, the implied warranties of merchantability and fitness for a
# particular purpose are disclaimed. In no event shall Nathan Grigg be
# liable for any direct, indirect, incidental, special, exemplary, or
# consequential damages (including, but not limited to, procurement of
# substitute goods or services; loss of use, data, or profits; or business
# interruption) however caused and on any theory of liability, whether in
# contract, strict liability, or tort (including negligence or otherwise)
# arising in any way out of the use of this software, even if advised of
# the possibility of such damage.
#
# (also known as the New BSD License)

"""Export Day One journal entries using a Jinja template.

The function dayone_export fills in a template. This function
can also be called using a command line interface. Run the script
with the --help argument for more information.

The Entry object represents a single journal entry.

The parse_journal function parses the journal into a list of
Entry objects.
"""

from operator import itemgetter
from functools import partial
from . import filters
import jinja2
import plistlib
import sys
import os
import times

SUBKEYS = {'Location': ['Locality', 'Country', 'Place Name',
                 'Administrative Area', 'Longitude', 'Latitude'],
               'Weather': ['Fahrenheit', 'Celsius', 'Description', 'IconName']}

class Entry(object):
    """Represents a single entry in the Day One journal

    Acts like a read-only dictionary with the following keys:

    - Creation Date (alias Date)
    - Entry Text (alias Text)
    - Starred
    - UUID
    - Location
    - Weather

    The Location and Weather keys point to second level dictionaries.
    The subkeys are in the SUBKEYS constant, and can be accessed
    directly, that is, entry['Location']['Longitude'] == entry['Longitude']

    The place function provides a flexible way to combine the location
    data.
    """

    def __init__(self, filename):
        try:
            self.data = plistlib.readPlist(filename)
        except Exception as err:
            raise IOError("Can't read {}\n{}".format(filename, err))

        if "Creation Date" not in self.data:
            raise KeyError("{} is missing Creation Date".format(filename))
        if "Entry Text" not in self.data:
            raise KeyError("{} is missing Entry Text".format(filename))

        words = self.data['Entry Text'].split()
        tags = []
        for word in reversed(words):
            if not word.startswith('#'):
                break
            tags.append(word[1:])

        self.data['Tags'] = tags

    def add_photo(self, filename):
        self.data['Photo'] = filename

    def place(self, *args, **kwargs):
        """Return comma-separated list of places, from smallest to largest

        Day one provides 4 levels of specificity:

        0: Place Name
        1: Locality (e.g. city)
        2: Administrative Area (e.g. state)
        3: Country

        place([n1, n2, ...]) returns any subset of the levels
        place(n) returns the first n levels [== place(range(n))]
        place(n, m) returns levels between n and m [== place(range(n, m))]

        place allows a single keyword argument: ignore
        ignore is a list of strings to ignore, e.g., your home country
        """

        # deal with the arguments
        if len(args) == 0:
            return self.place(range(4), **kwargs)
        if type(args[0]) is int:
            return self.place(range(*args), **kwargs)
        ignore = []
        for k, v in kwargs.items():
            if k == 'ignore':
                ignore = v if type(v) is list else [v]
            else:
                raise TypeError(
            "'{}' is an invalid keyword argument for this function".format(k))

        # make sure there is a location set
        if not 'Location' in self:
            raise KeyError('Location')

        # down to business
        order= ['Place Name', 'Locality', 'Administrative Area', 'Country']
        names = []
        for n in args[0]:
            if order[n] in self:
                value = self[order[n]]
                if len(value) and value not in ignore:
                    names.append(value)

        return ", ".join(names)

    def __getitem__(self, key):
        if key in self.data:
            return self.data[key]

        if key == "Text":
            return self.data['Entry Text']

        if key == "Date":
            return self.data['Creation Date']

        # flatten the dictionary a bit
        for superkey, subkeys in SUBKEYS.items():
            if key in subkeys:
                return self.data[superkey][key]

        raise KeyError(key)

    def __contains__(self, key):
        if key in self.data or key in ["Text", "Date"]:
            return True

        for superkey, subkeys in SUBKEYS.items():
            if key in subkeys:
                return superkey in self.data and key in self.data[superkey]

        return False

    def keys(self):
        out = self.data.keys() + ["Text", "Date"]
        for superkey, subkeys in SUBKEYS.items():
            if superkey in self:
                out.extend([k for k in subkeys if k in self])

        return out

    def __repr__(self):
        return "<Entry at {}>".format(self['Date'])

def parse_journal(foldername, reverse=False):
    """Return a list of Entry objects, sorted by date"""

    journal = dict()
    for filename in os.listdir(os.path.join(foldername, 'entries')):
        if os.path.splitext(filename)[1] == '.doentry':
            entry = Entry(os.path.join(foldername, 'entries', filename))
            journal[entry['UUID']] = entry

    if len(journal) == 0:
        raise Exception("No journal entries found in " + foldername)

    try:
        photos = os.listdir(os.path.join(foldername, 'photos'))
    except OSError:
        pass
    else:
        for filename in photos:
            base = os.path.splitext(filename)[0]
            try:
                journal[base].add_photo(os.path.join('photos', filename))
            except KeyError:
                # ignore items in the photos folder with no corresponding entry
                pass

    # make it a list and sort
    journal = journal.values()
    journal.sort(key=itemgetter('Creation Date'), reverse=reverse)
    return journal

def _determine_inheritance(template, template_dir, format):
    """Determines where to look for template based on user options"""

    # explicit path to template => only load that template
    if template is not None:
        path, base = os.path.split(template)
        if path:
            return jinja2.FileSystemLoader(path), base

    # template directory given => look there only
    if template_dir is not None:
        loader = jinja2.FileSystemLoader(template_dir)

    else:
        template_dir = os.path.expanduser('~/.dayone_export')
        # template is given => look in current directory, then defaults
        if template is not None:
            template_search_path = ['.', template_dir]
        # no template is given => don't look in current directory
        else:
            template_search_path = [template_dir]

        loader = jinja2.ChoiceLoader([
          jinja2.FileSystemLoader(template_search_path),
          jinja2.PackageLoader('dayone_export')
        ])

    # determine template if none is given
    if template is None:
        template = ("default." + format) if format else "default.html"

    return loader, template

def dayone_export(dayone_folder, template=None, timezone='utc',
  reverse=False, tags=None, after=None, format=None, template_dir=None):
    """Combines dayone data using the template

    If no template is given, searches for default template from the
    templates folder of the package.
    """

    # figure out which template to use
    loader, template = _determine_inheritance(template, template_dir, format)
    env = jinja2.Environment(loader=loader, trim_blocks=True)

    # filters
    env.filters['markdown'] = filters.markup
    env.filters['format'] = partial(filters.format, tz=timezone)
    env.filters['imgbase64'] = partial(filters.imgbase64, dayone_folder=dayone_folder)

    # load template
    template = env.get_template(template)

    # parse journal
    j = parse_journal(dayone_folder, reverse=reverse)

    if after is not None:
        after = times.to_universal(after, timezone=timezone)
        j = [item for item in j if item['Date'] > after]

    if tags:
        if tags == 'any':
            tag_filter = lambda item: item['Tags']
        else:
            tag_filter = lambda item: set(item['Tags']).intersection(set(tags))

        j = filter(tag_filter, j)

    # may throw an exception if the template is malformed
    # the traceback is helpful, so i'm letting it through
    # it might be nice to clean up the error message, someday
    return template.render(journal=j)
