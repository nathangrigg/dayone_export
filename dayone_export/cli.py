#!/usr/bin/env python
#
# Command line interface to dayone_export
#
# For help, run `dayone_export --help`

from . import dayone_export, VERSION, compat
import dateutil.parser
import jinja2
import argparse
import codecs
import locale
import os
import sys


def template_not_found_message(template):
    message = ["Template not found: {0}".format(template),
            "Use the `--template` option to specify a template."]
    try:
        from pkg_resources import resource_listdir
        message.extend(["The following templates are built-in:"] +
                resource_listdir('dayone_export', 'templates'))
    except ImportError:
        pass
    return '\n'.join(message)


def parse_args(args=None):
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
      description="Export Day One entries using a Jinja template",
      usage="%(prog)s [--output FILE] [opts] journal",
      epilog="""If the Day One package has photos, you may need to copy
        the "photos" folder from the package into the same directory
        as the output file.""")
    parser.add_argument('journal', help="path to Day One journal package")
    parser.add_argument('--output', metavar="FILE", default="",
      help="file to write (default print to stdout). "
            "Using strftime syntax will produce multiple "
            "output files with entries grouped by date.")
    parser.add_argument('--format', metavar="FMT",
      help="output format (default guess from output file extension)")
    parser.add_argument('--template', metavar="NAME",
      help="name or file of template to use")
    parser.add_argument('--template-dir', metavar="DIR",
      help='location of templates (default ~/.dayone_export)')
    parser.add_argument('--tags',
      help='export entries with these comma-separated tags. Tag \'any\' has a special meaning.')
    parser.add_argument('--exclude',
      help='exclude entries with these comma-separated tags')
    parser.add_argument('--after', metavar='DATE',
      help='export entries published on or after this date')
    parser.add_argument('--before', metavar='DATE',
      help='export entries published before this date')
    parser.add_argument('--reverse', action="store_true",
      help="display in reverse chronological order")
    parser.add_argument('--autobold', action="store_true",
      help="autobold first lines (titles) of posts")
    parser.add_argument('--nl2br', action="store_true",
      help="convert each new line to a <br>")

    parser.add_argument('--version', action='version', version=VERSION)
    return parser.parse_args(args)

# command line interface
def run(args=None):
    locale.setlocale(locale.LC_ALL, '')
    args = parse_args(args)

    # determine output format
    if args.format is None:
        args.format = os.path.splitext(args.output)[1][1:] if args.output \
                      else 'html'
    if args.format.lower() in ['md', 'markdown', 'mdown', 'mkdn']:
        args.format = 'md'

    # Check journal files exist
    args.journal = os.path.expanduser(args.journal)
    if not os.path.exists(args.journal):
        return "File not found: " + args.journal
    if not os.path.exists(os.path.join(args.journal, 'entries')):
        return "Not a valid Day One package: " + args.journal

    # tags
    tags = args.tags
    if tags is not None:
        if tags != 'any':
            tags = [tag.strip() for tag in tags.split(',')]

    # excluded tags
    excluded_tags = args.exclude
    if excluded_tags is not None:
        excluded_tags = [tag.strip() for tag in excluded_tags.split(',')]

    # parse before and after date
    dates = [args.before, args.after]
    for i, date in enumerate(dates):
        if date:
            try:
                dates[i] = dateutil.parser.parse(date)
            except (ValueError, OverflowError):
                return "Unable to parse date '{0}'".format(date)
    before, after = dates

    generator = dayone_export(
            args.journal,
            template=args.template,
            reverse=args.reverse,
            tags=tags,
            exclude=excluded_tags,
            before=before,
            after=after,
            format=args.format,
            template_dir=args.template_dir,
            autobold=args.autobold,
            nl2br=args.nl2br,
            filename_template=args.output)

    try:

        # Output is a generator returning each file's name and contents one at a time
        for filename, output in generator:
            if args.output:
                with codecs.open(filename, 'w', encoding='utf-8') as f:
                    f.write(output)
            else:
                compat.print_bytes(output.encode('utf-8'))
                compat.print_bytes("\n".encode('utf-8'))

    except jinja2.TemplateNotFound as err:
        return template_not_found_message(err)
    except IOError as err:
        return str(err)


if __name__ == "__main__":
    sys.exit(run())
