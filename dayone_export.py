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

The module also makes the timezone function from pytz available.
"""

from jinja2 import Environment, FileSystemLoader
from pytz import timezone, utc, UnknownTimeZoneError
from operator import itemgetter
import plistlib
import datetime
import codecs
import sys
import os

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

    def __init__(self, filename, timezone=utc):
        try:
            self.data = plistlib.readPlist(filename)
        except Exception as err:
            raise IOError("Can't read {}\n{}".format(filename, err))

        if "Creation Date" not in self.data:
            raise KeyError("{} is missing Creation Date".format(filename))
        if "Entry Text" not in self.data:
            raise KeyError("{} is missing Entry Text".format(filename))
        self.data['Creation Date'] = utc.localize(
            self.data['Creation Date']).astimezone(timezone)

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
        return "<Entry at {}>".format(self['Date'].strftime(
          "%Y-%m-%dT%H:%M:%S%z"))

def parse_journal(foldername, timezone=utc, reverse=False):
    """Return a list of Entry objects, sorted by date"""

    journal = dict()
    for filename in os.listdir(os.path.join(foldername, 'entries')):
        if os.path.splitext(filename)[1] == '.doentry':
            entry = Entry(os.path.join(foldername, 'entries', filename),
              timezone=timezone)
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

def dayone_export(dayone_folder, template="template.html", timezone=utc,
  reverse=False):
    """Combines dayone data using the template"""

    #setup jinja2
    path, base = os.path.split(template)
    env = Environment(loader=FileSystemLoader(path), trim_blocks=True)

    # markdown
    try:
        import markdown
    except:
        global need_markdown_warning
        need_markdown_warning = True
        def markup(text, *args, **kwargs):
            global need_markdown_warning
            if need_markdown_warning:
                need_markdown_warning = False
                print "Warning: cannot load markdown module"
            return text
    else:
        def markup(text, *args, **kwargs):
            return markdown.markdown(text, *args, **kwargs)
    env.filters['markdown'] = markup

    # load template
    template = env.get_template(base)

    # parse journal
    j = parse_journal(dayone_folder, timezone=timezone, reverse=reverse)

    # may throw an exception if the template is malformed
    # the traceback is helpful, so i'm letting it through
    # it might be nice to clean up the error message, someday
    return template.render(journal=j)

def parse_args():
    """Parse command line arguments"""
    import argparse
    parser = argparse.ArgumentParser(
      description="Export Day One entries using a Jinja template",
      usage="""%(prog)s [-h] [--template FILE] [--output FILE]
                 [--timezone ZONE] [--reverse] journal""",
      epilog="""Photos are not copied from the Day One package.
        If it has photos you will need to copy the "photos" folder from
        inside the Day One package into the same directory as the output file.
        """)
    parser.add_argument('--template', metavar="FILE",
      default="template.html", help="template file")
    parser.add_argument('--output', metavar="FILE", help="output file")
    parser.add_argument('--timezone', metavar="ZONE",
      help='time zone name. Use --timezone "?" for more info')
    parser.add_argument('--reverse', action="store_true",
      help="Display in reverse chronological order")
    parser.add_argument('journal', help="path to Day One journal package",
      nargs="?")
    return parser.parse_args()

def timezone_help(s):
    """Display help on time zone and exit"""
    import pytz
    if s == '?':
        title, zones = "Common time zones:", pytz.common_timezones
    elif s == "??":
        title, zones = "All possible time zones:", pytz.all_timezones
    elif len(s) == 3:
        title = "Time zones for country: " + s[1:]
        try: zones = pytz.country_timezones(s[1:])
        except KeyError:
            title = "Unrecognized country code: " + s[1:]
            zones = []
    else:
        title = "Unrecognized option: --timezone " + s
        zones = []

    print title
    for i, z in enumerate(zones):
        if i % 2 or not sys.stdout.isatty():
            print z
        else:
            print "{: <34}".format(z),
    if not i % 2 and sys.stdout.isatty():
        print

    print """\
For information about time zone choices use one of the following options:
    --timezone "?"   print common time zones
    --timezone "??"  print all time zones
    --timezone "?XX" all time zones in country with two-letter code XX"""

    sys.exit()

# command line interface
if __name__ == "__main__":
    args = parse_args()

    # auto generate output file name if necessary
    if args.output is None:
        base, ext = os.path.splitext(args.template)
        args.output = "journal" + ("-output" if base == "journal" else "") + ext

    if args.timezone is None or len(args.timezone) == 0:
        tz = utc
    elif args.timezone[0] == "?":
        timezone_help(args.timezone)
    else:
        try:
            tz = timezone(args.timezone)
        except UnknownTimeZoneError:
            sys.exit("Unknown time zone: " + args.timezone)

    # Make sure there is a journal
    if args.journal is None:
        sys.exit("Error: too few arguments")

    # Check files exist
    args.journal = os.path.expanduser(args.journal)
    if not os.path.exists(args.journal):
        sys.exit("File not found: " + args.journal)
    if not os.path.exists(os.path.join(args.journal, 'entries')):
        sys.exit("Not a valid Day One package: " + args.journal)
    if not os.path.exists(args.template):
        sys.exit("File not found: " + args.template)


    try:
        output = dayone_export(args.journal, template=args.template,
          timezone=tz, reverse=args.reverse)
    except IOError as err:
        sys.exit(err)

    try:
        with codecs.open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
    except IOError as err:
        sys.exit(err)

    print "Output written to {}".format(args.output)


