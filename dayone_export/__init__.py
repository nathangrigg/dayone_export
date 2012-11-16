#! /usr/bin/env python
#
# Copyright (c) 2012, Nathan Grigg
# All rights reserved.
# BSD License

"""Export Day One journal entries using a Jinja template."""

from operator import itemgetter
from functools import partial
from . import filters
import jinja2
import plistlib
import os
import pytz

SUBKEYS = {'Location': ['Locality', 'Country', 'Place Name',
                 'Administrative Area', 'Longitude', 'Latitude'],
               'Weather': ['Fahrenheit', 'Celsius', 'Description', 'IconName']}


class Entry(object):
    """Parse a single journal entry.

    :raises: IOError, KeyError

    Acts like a read-only dictionary.
    The keys are as defined in the plist file by the Day One App, with
    minor exceptions:

    - What Day One calls "Entry Text", we call "Text".
    - The "Location" and "Weather" dictionaries are flattened,
      so that their subkeys are accessible as keys of the main dictionary
    - The "Photo" key is added and should contain the path to attached photo
    - The "Date" key is added and should contain the localized date.

    Note that the "Creation Date" contains a naive date as defined
    by the plist which should correspond to a UTC time.
    """

    def __init__(self, filename):
        try:
            self.data = plistlib.readPlist(filename)
        except Exception as err:
            raise IOError("Can't read {0}\n{1}".format(filename, err))

        # Required fields
        if "Creation Date" not in self.data:
            raise KeyError("Creation Date")

        # aliases and flattening
        self.data['Text'] = self.data.pop('Entry Text', "")
        for key in ['Location', 'Weather']:
            if key in self.data:
                new_keys = ((k, v) for k, v in self.data[key].items()
                            if k not in self.data) # prevent overwrite
                self.data.update(new_keys)

    def set_photo(self, filename):
        """Set the filename of the photo"""
        self.data['Photo'] = filename

    def set_localized_date(self, timezone):
        """Set the localized date (the "Date" key)"""
        try:
            tz = pytz.timezone(timezone)
        except pytz.UnknownTimeZoneError:
            tz = pytz.utc

        self.data["Date"] = tz.localize(self["Creation Date"])

    def set_time_zone(self, timezone):
        """Set the time zone"""
        self.data["Time Zone"] = timezone

    def place(self, levels=4, ignore=None):
        """Format entry's location as string, with places separated by commas.

        :param levels: levels of specificity to include
        :type levels: list of int
        :keyword ignore: locations to ignore
        :type ignore: string or list of strings

        The *levels* parameter should be a list of integers corresponding to
        the following levels of specificity defined by Day One.

        - 0: Place Name
        - 1: Locality (e.g. city)
        - 2: Administrative Area (e.g. state)
        - 3: Country

        Alternately, *levels* can be an integer *n* to specify the *n*
        smallest levels.

        The keyword argument *ignore* directs the method to ignore one
        or more place names. For example, you may want to ignore
        your home country so that only foreign countries are shown.
        """

        # deal with the arguments
        if isinstance(levels, int):
            levels = list(range(levels))
        if ignore is None:
            ignore = []
        if isinstance(ignore, basestring):
            ignore = [ignore]

        # make sure there is a location set
        if not 'Location' in self:
            return "" # fail silently

        # mix up the order
        order = ['Place Name', 'Locality', 'Administrative Area', 'Country']
        try:
            order_keys = [order[n] for n in levels]
        except TypeError:
            raise TypeError("'levels' argument must be an integer or list")

        # extract keys
        names = (self[key] for key in order_keys if key in self)

        # filter
        try:
            names = [name for name in names if len(name) and name not in ignore]
        except TypeError:
            raise TypeError("'ignore' argument must be a string or list")

        return ", ".join(names)

    def __getitem__(self, key):
        return self.data[key]

    def __contains__(self, key):
        return key in self.data

    def keys(self):
        """List all keys."""
        return list(self.data.keys())

    def __repr__(self):
        return "<Entry at {0}>".format(self['Creation Date'])


def parse_journal(foldername):
    """Return a list of Entry objects, sorted by date"""

    journal = dict()
    for filename in os.listdir(os.path.join(foldername, 'entries')):
        if os.path.splitext(filename)[1] == '.doentry':
            try:
                entry = Entry(os.path.join(foldername, 'entries', filename))
            except KeyError as err:
                pass

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
                journal[base].set_photo(os.path.join('photos', filename))
            except KeyError:
                # ignore items in the photos folder with no corresponding entry
                pass

    # make it a list and sort
    journal = journal.values()
    journal.sort(key=itemgetter('Creation Date'))

    # add timezone info
    newest_tz = 'utc'
    for entry in reversed(journal):
        if "Time Zone" in entry:
            newest_tz = entry["Time Zone"]
            break

    tz = newest_tz
    for entry in reversed(journal):
        if "Time Zone" in entry:
            tz = entry["Time Zone"]
        else:
            entry.set_time_zone(tz)

        entry.set_localized_date(tz)

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

def _filter_by_tag(journal, tags):
    """filter by list of tags. tags='any' allows any entry with some tag"""
    if tags == 'any':
        tag_filter = lambda item: 'Tags' in item
    else:
        tag_filter = lambda item: 'Tags' in item and set(item['Tags']).intersection(set(tags))

    return filter(tag_filter, journal)

def _filter_by_after_date(journal, date):
    """return a list of entries after date

    :param date: A naive datetime representing a UTC time"""
    return [item for item in journal if item['Creation Date'] > date]

def dayone_export(dayone_folder, template=None, reverse=False, tags=None,
    after=None, format=None, template_dir=None):
    """Render a template using entries from a Day One journal.

    :param dayone_folder: Name of Day One folder; generally ends in ``.dayone``.
    :type dayone_folder: string
    :param reverse: If true, the entries are formatted in reverse chronological
                    order.
    :type reverse: bool
    :param tags: Only include entries with the given tags.
                 This paramater can also be the literal string ``any``,
                 in which case only entries with tags are included.
                 Tags are interpreted as words at the end of an entry
                 beginning with ``#``.
    :type tags: list of strings
    :param after: Only include entries after the given date.
    :type after: naive datetime
    :param format: The file extension of the default template to use.
    :type format: string
    :param template: Template file name.
                     The program looks for the template first
                     in the  current directory, then the template directory.
    :type template: string
    :param template_dir: Directory containing templates.
                         If not given, the program looks in
                         ``~/.dayone_export`` followed by the
                         dayone_export package.
    :type template_dir: string
    :returns: Filled in template as string.
    """

    # figure out which template to use
    loader, template = _determine_inheritance(template, template_dir, format)
    env = jinja2.Environment(loader=loader, trim_blocks=True)

    # filters
    env.filters['markdown'] = filters.markup
    env.filters['format'] = filters.format
    env.filters['imgbase64'] = partial(filters.imgbase64,
      dayone_folder=dayone_folder)

    # load template
    template = env.get_template(template)

    # parse journal
    j = parse_journal(dayone_folder)

    # filter and manipulate based on options
    if after is not None:
        if after.tzinfo is None:
            # set timezone to mirror last journal entry
            after = j[-1]["Date"].tzinfo.localize(after)
        # convert to UTC
        after.astimezone(pytz.utc)
        # strip timezone info
        after = after.replace(tzinfo=None)
        j = _filter_by_after_date(j, after)
    if tags is not None:
        j = _filter_by_tag(j, tags)
    if reverse:
        j.reverse()

    # may throw an exception if the template is malformed
    # the traceback is helpful, so i'm letting it through
    # it might be nice to clean up the error message, someday
    return template.render(journal=j)
