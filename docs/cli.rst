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


Change the default template
---------------------------


Filter by tag
-------------


Limit export to recent entries
------------------------------


Link to or embed photos
-----------------------

