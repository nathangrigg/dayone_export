#! /usr/bin/env python
#
# Copyright (c) 2012, Nathan Grigg
# All rights reserved.
# BSD License

"""Export Day One journal entries using a Jinja template."""

from __future__ import division

from collections import defaultdict
from datetime import datetime
from functools import partial
from operator import itemgetter
import json
import os
import pytz

from . import compat
from . import filters
from .version import VERSION
import jinja2

class ReadError(Exception):
    pass


class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


def format_place(entry, levels=4, ignore=None):
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
    if isinstance(ignore, compat.string_types):
        ignore = [ignore]

    # make sure there is a location set
    try:
        location = entry["location"]
    except KeyError:
        return "" # fail silently

    # mix up the order
    order = ['placeName', 'localityName', 'administrativeArea', 'country']
    try:
        order_keys = [order[n] for n in levels]
    except TypeError:
        raise TypeError("'levels' argument must be an integer or list")

    # extract keys
    names = (location[key] for key in order_keys if key in location)

    # filter
    try:
        names = [name for name in names if len(name) and name not in ignore]
    except TypeError:
        raise TypeError("'ignore' argument must be a string or list")

    return ", ".join(names)

def format_weather(entry, temperature_type, degree="&deg;"):
    try:
        temp_c = int(entry["weather"]["temperatureCelsius"])
        desc = entry["weather"]["conditionsDescription"]
    except (KeyError, ValueError):
        return ""

    if temperature_type.lower() in {'fahrenheit', 'f'}:
        temp = temp_c * 9/5 + 32
    else:
        temp = temp_c

    return "{0}{1} {2}".format(temp, degree, desc)


def parse_journal(journal_folder):
    """Return a list of journal entries parsed from json file.

    Each journal entry is encoded as a nested AttrDict as parsed from the json
    file, with a few additions:

        - `timeZone` is inferred for entries that are missing `timeZone`.
        - `creationDate` is converted to a `datetime` object.
        - `localDate` is added, which is `creationDate` localized to `timeZone`.
    """

    json_file_name = os.path.join(journal_folder, 'Journal.json')

    with open(json_file_name, "r", encoding="utf-8") as fh:
        parsed = json.load(fh, object_hook=AttrDict)

    try:
        journal = parsed["entries"]
    except KeyError:
        raise Exception(
            "Cannot understand {} as a Day One json dump: missing 'entries' "
            "object".format(json_file_name))

    if len(journal) == 0:
        raise Exception("No journal entries found in {}".format(json_file_name))

    # add timezone info
    newest_tz = "utc"
    for entry in reversed(journal):
        if "timeZone" in entry:
            newest_tz = entry["timeZone"]
            break

    tz_name = newest_tz
    for entry in reversed(journal):
        if "timeZone" in entry:
            tz_name = entry["timeZone"]
        else:
            entry["timeZone"] = tz_name

        try:
            tz = pytz.timezone(tz_name)
        except pytz.UnknownTimeZoneError:
            tz = pytz.utc

        date = datetime.strptime(
                entry["creationDate"], "%Y-%m-%dT%H:%M:%SZ")
        entry["creationDate"] = date
        localized_utc = pytz.utc.localize(date)
        entry["localDate"] = localized_utc.astimezone(tz)

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
        tag_filter = lambda item: 'tags' in item
    else:
        tags = frozenset(tags)
        tag_filter = lambda item: 'tags' in item and tags.intersection(
                item['tags'])

    return filter(tag_filter, journal)


def _exclude_tags(journal, tags):
    """remain only entries without specified tags"""

    tags = frozenset(tags)
    remain_filter = lambda item: 'tags' not in item or not tags.intersection(
            item['tags'])

    return filter(remain_filter, journal)


def _filter_by_date(journal, after, before):
    """return a list of entries after date

    :param before: A naive datetime representing a UTC time.
    :param after: A naive datetime representing a UTC time
    """
    if after is None and before is None:
        return journal
    return [item for item in journal
            if (after is None or item['creationDate'] >= after) and
               (before is None or item['creationDate'] < before)]


def _convert_to_utc(date, default_tz):
    """Convert date to UTC, using default_tz if no time zone is set."""
    if date is None:
        return date
    if date.tzinfo is None:
        date = default_tz.localize(date)
    date.astimezone(pytz.utc)
    # strip timezone info
    return date.replace(tzinfo=None)


def dayone_export(dayone_folder, template=None, reverse=False, tags=None,
    exclude=None, before=None, after=None, format=None, template_dir=None, autobold=False,
    nl2br=False, filename_template=""):
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
    :param exclude: Exclude all entries with given tags.
    :type exclude: list of strings
    :param before: Only include entries on before the given date.
    :type before: naive datetime
    :param after: Only include entries on or after the given date.
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
    :param autobold: Specifies that the first line of each post should be
                     a heading
    :type autobold: bool
    :param nl2br:  Specifies that new lines should be translated in to <br>s
    :type nl2br: bool
    :type filename_template: string
    :param filename_template: An eventual filename, which can include strftime formatting codes.
                Each time the result of formatting an entry's timestamp with this changes,
                a new result will be returned.
    :returns: Iterator yielding (filename, filled_in_template) as strings on each iteration.
    """

    # figure out which template to use
    loader, template = _determine_inheritance(template, template_dir, format)

    # custom latex template syntax
    custom_syntax = {}
    if os.path.splitext(template)[1] == ".tex":
        custom_syntax = {'block_start_string': r'\CMD{',
                         'block_end_string': '}',
                         'variable_start_string': r'\VAR{',
                         'variable_end_string': '}',
                         }
    # define jinja environment
    env = jinja2.Environment(loader=loader, trim_blocks=True, **custom_syntax)

    # filters
    env.filters['markdown'] = filters.markdown_filter(autobold=autobold)
    env.filters['format'] = filters.format
    env.filters['escape_tex'] = filters.escape_tex
    env.filters['imgbase64'] = partial(filters.imgbase64,
      dayone_folder=dayone_folder)


    # load template
    template = env.get_template(template)

    # parse journal
    j = parse_journal(dayone_folder)

    # filter and manipulate based on options
    default_tz = j[-1]["localDate"].tzinfo
    after = _convert_to_utc(after, default_tz)
    before = _convert_to_utc(before, default_tz)
    j = _filter_by_date(j, after=after, before=before)
    if tags is not None:
        j = _filter_by_tag(j, tags)
    if exclude is not None:
        j = _exclude_tags(j, exclude)
    if reverse:
        j.reverse()


    # Split into groups, possibly of length one
    # Generate a new output for each time the 'filename_template' changes.
    # Yield the resulting filename_template plus the output.
    # If the filename_template is an empty string (the default), we'll get
    # an empty grouper plus the rendering of the full list of entries.
    # This may throw an exception if the template is malformed.
    # The traceback is helpful, so I'm letting it through
    # it might be nice to clean up the error message, someday

    output_groups = defaultdict(list)
    for e in j:
        output_groups[e['localDate'].strftime(filename_template)].append(e)

    today = datetime.today()
    for k in output_groups:
        yield k, template.render(
                journal=output_groups[k],
                format_place=format_place,
                format_weather=format_weather,
                today=today)
