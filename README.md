Export [Day One][0] journal entries into html, text, or another format
using a Jinja template.

by Nathan Grigg

# Installation

Download the package and run

    python setup.py install

# Quick start

    dayone_export --output journal.html ~/Dropbox/Apps/Day\ One/Journal.dayone

Adjust the argument to be the path to your Day One journal.

# Usage

    usage: dayone_export [-h] [--template FILE] [--output FILE]
                         [--timezone ZONE] [--reverse] journal

    Export Day One entries using a Jinja template

    positional arguments:
      journal          path to Day One journal package

    optional arguments:
      -h, --help       show this help message and exit
      --template FILE  template file
      --output FILE    output file
      --tags TAGS      export entries with these comma-separated tags.
                       Tag 'any' has a special meaning, it says to export
                       entries with one or more tags.
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

You can use the  `format` filter on a date to control how it is displayed.
For example:

    {{ entry['Date']|format('%Y-%m-%d %H:%M:%S %z') }}

## The markdown filter

If you have python markdown installed, you can pass things through
the markdown filter using a pipe:

    {{ entry['Text'] | markdown }}

This converts the text to html.

## Inlining images with base64 encoding

You can include the images inline with base64 encoding using a custom filter:

    {{ entry['Photo'] | imgbase64 }}

The resulting entry looks like:

    <img class="entry-photo" src="data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0a ... ">

The base64 data can become quite large in size. If you have [PIL][6]
installed, you can resize the images so that the resulting output
remains sufficently small (default maximum size is 400 pixels):

    {{ entry['Photo'] | imgbase64(800) }}

This includes the image inline with a maxium size of 800 pixels.

## More templating information

For more details on Jinja templates, see the
[Jinja template designer documentation][5].

[0]: http://dayoneapp.com
[1]: http://jinja.pocoo.org
[2]: http://pypi.python.org/pypi/times/
[3]: http://freewisdom.org/projects/python-markdown/
[4]: http://www.pip-installer.org/en/latest/index.html
[5]: http://jinja.pocoo.org/docs/templates/
[6]: http://www.pythonware.com/products/pil/
