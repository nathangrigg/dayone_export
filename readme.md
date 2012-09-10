Export [Day One][0] journal entries into html, text, or another format
using a Jinja template.

by Nathan Grigg

# Requirements

- [jinja2][1] for templating
- [times][2] for time zone support.
- [markdown][3] (optional) to convert entries to html.

If you have [pip][4] installed, you can run

    pip install jinja2 times markdown

and you are ready to go.

# Quick start

After you have installed the dependencies and downloaded the script,
`cd` into the `dayone_export` directory and run

    ./dayone_export.py ~/Dropbox/Apps/"Day One"/Journal.dayone

Adjust the argument to be the path to your Day One journal.

# Usage

    usage: dayone_export.py [-h] [--template FILE] [--output FILE]
                            [--timezone ZONE] [--reverse] journal

    Export Day One entries using a Jinja template

    positional arguments:
      journal          path to Day One journal package

    optional arguments:
      -h, --help       show this help message and exit
      --template FILE  template file
      --output FILE    output file
      --after DATETIME export only entries after the date
      --timezone ZONE  time zone name. Use --timezone "?" for more info
      --reverse        Display in reverse chronological order

    Photos are not copied from the Day One package. If it has photos you will
    need to copy the "photos" folder from inside the Day One package into the
    same directory as the output file.

# Templates

## Basic template example

    Journal Entries
    ===============
    {% for entry in journal %}
    Date: {{ times.format(entry['Date'], timezone, '%A, %b %e, %Y') }}

    {{ entry['Text'] }}

    {% endfor %}

## The journal variable

Templates receive a single variable: `journal`, which is a list of entries.
So your template will probably look something like this:

    ... document header, title, etc ...
    {% for entry in journal %}
    ... code for a single entry ...
    {% endfor %}
    ... end of document stuff, etc ...

## The Entry object

Each entry has the following keys:

- Date
- Text
- Starred
- UUID
- Photo (the path of the corresponding photo, if it exists)
- Place Name (e.g. Boom Noodle)
- Locality (e.g. Seattle)
- Administrative Area (e.g. Washington)
- Country (e.g. United States)
- Longitude
- Latitude
- Fahrenheit
- Celsius
- Description (this refers to the weather)
- IconName (also refers to weather)

You insert one of these into your document using double brackets, e.g.

    {{ entry['Place Name'] }}

Jinja will just leave a blank space if you try to access a nonexistent key.
If you want to test if a key exists, you can always do

    {% if Longitude in entry %}
    ... conditional code
    {% endif %}

## Places

Each entry also has a `place` convenience function. You can use `entry.place()`
or `entry.place(4)` to get a comma-separated list of all the places in order.
If you use `entry.place(3)`, it will only show the first three levels and leave
off the country. Or `entry.place(1,4)` will leave off the "Place Name" and just
show city, state, country. You can get more complicated; for details,
see the code.

## Dates

You can call `times.format` on the date to format it from internal UTC into
desired timezone. A `timezone` context variable refers to a timezone, specified
with `--timezone` option, which is `UTC` by default. For example:

    {{ times.format(entry['Date'], timezone, '%Y-%m-%d %H:%M:%S %z') }}

## The markdown filter

If you have python markdown installed, you can pass things through
the markdown filter using a pipe:

    {{ entry['Text'] | markdown }}

This converts the text to html.

## More templating information

For more details on Jinja templates, see the
[Jinja template designer documentation][5].

[0]: http://dayoneapp.com
[1]: http://jinja.pocoo.org
[2]: http://pypi.python.org/pypi/times/
[3]: http://freewisdom.org/projects/python-markdown/
[4]: http://www.pip-installer.org/en/latest/index.html
[5]: http://jinja.pocoo.org/docs/templates/
