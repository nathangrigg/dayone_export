.. highlight:: none

Use the command line tool
=========================


Basic Usage
-----------

::

    usage: dayone_export [--output FILE] [opts] journal

    Export Day One entries using a Jinja template

    positional arguments:
    journal             path to Day One journal package

    optional arguments:
    -h, --help          show this help message and exit
    --output FILE       file to write (default print to stdout). Using strftime
                        syntax will produce multiple output files with entries
                        grouped by date.
    --format FMT        output format (default guess from output file extension)
    --template NAME     name or file of template to use
    --template-dir DIR  location of templates (default ~/.dayone_export)
    --tags TAGS         export entries with these comma-separated tags. Tag
                        'any' has a special meaning.
    --exclude TAGS      exclude entries with these comma-separated tags
    --after DATE        export entries published after this date
    --reverse           display in reverse chronological order
    --autobold          autobold first lines (titles) of posts
    --nl2br             convert each new line to a <br>
    --version           show program's version number and exit

    If the Day One package has photos, you may need to copy the "photos" folder
    from the package into the same directory as the output file.

Use a custom template
---------------------

Use the ``--template`` option to specify a custom template.

For information on how to create templates, see :ref:`templates`.


Change the default template
---------------------------

You can override the default template by creating a ``default.html`` file
and placing it in the folder ``~/.dayone_export``.

You can also create default templates of other types in a similar manner.
For example, ``default.tex`` would be a default LaTeX template.
The default markdown template should be called `default.md`.

The program uses the extension of the output file to determine which
default template to use. If there is no output file, use the
``--format`` option to specify the format.

If you wish to use a directory other than ``~/.dayone_export``, as the
location for default templates, you can use the ``--template-dir`` option.

Filter by tag
-------------

Use the ``--tags`` option with a comma-separated list of tags to include.

If you use the option ``--tags any``, then any entry with at least one tag
will be included.

Also, you can exclude entries with specified tags, by using the ``--exclude``
option.

Limit export to recent entries
------------------------------

Use the ``--after`` option to only export entries after a certain date.

For best results, use some kind of
standard form for the date (e.g. ``2012-03-04``).

Markdown options
----------------

The ``--autobold`` option will convert the first line of each post into a heading,
as long as it is relatively short (similar to the way Day One optionally can)

The ``--nl2br`` option will insert a ``<br>`` tag after each new line.


Link to or embed photos
-----------------------

The default html template refers to photos by their relative names.
To show the photos in the output file, you will need to copy the ``photos``
directory from inside the `Journal.dayone` package into the same directory
as the output html file.

There is an alternate template which embeds photos directly into the html
file as base64-encoded images. To use this template, use the option
``--template imgbase64.html``.

Template filenames and grouping
-------------------------------

The ``--output`` option specifies the output filename if you
want something other than stdout.

It also has another feature: you can include strftime-style_ formatting codes,
in which case multiple files will be produced, each containing the journal
entries with timestamps that result in the same filename.

Examples:

  ``--output journal_%Y_%m.md`` will produces monthly files named
  journal_2013_02.md etc.

  ``--output diary_%a.html`` will produce a separate file for each weekday.

Note that if you want a literal ``%`` in your output filename, you will need
to escape it as ``%%``.

.. _strftime-style: http://docs.python.org/2/library/datetime.html#strftime-strptime-behavior
