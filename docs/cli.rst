.. highlight:: none

Use the command line tool
=========================


Basic Usage
-----------

::

    usage: dayone_export [--output FILE] [--timezone ZONE] [opts] journal

    Export Day One entries using a Jinja template

    positional arguments:
      journal             path to Day One journal package

    optional arguments:
      -h, --help          show this help message and exit
      --output FILE       file to write (default print to terminal)
      --timezone ZONE     time zone name. (--timezone "?" for more info)
      --format FMT        output format (default guess from output file extension)
      --template NAME     name or file of template to use
      --template-dir DIR  location of templates (default ~/.dayone_export)
      --tags TAGS         export entries with these comma-separated tags. Tag
                          'any' has a special meaning.
      --after DATE        export entries published after this date
      --reverse           display in reverse chronological order

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

Limit export to recent entries
------------------------------

Use the ``--after`` option to only export entries after a certain date.

For best results, use some kind of
standard form for the date (e.g. ``2012-03-04``).



Link to or embed photos
-----------------------

The default html template refers to photos by their relative names.
To show the photos in the output file, you will need to copy the ``photos``
directory from inside the `Journal.dayone` package into the same directory
as the output html file.

There is an alternate template which embeds photos directly into the html
file as base64-encoded images. To use this template, use the option
``--template imgbase64``.

