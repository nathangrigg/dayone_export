Create your own template
========================

The package comes with some basic templates. If you do not specify a template,
it will use one of these.

If you want to create your own template to use by default, you should name it ``~/.dayone_export/default.html``.

You can also specify a specific template using the ``--template`` option.

Basic template example
----------------------

::

    Journal Entries
    ===============
    {% for entry in journal %}
    Date: {{ times.format(entry['Date'], timezone, '%A, %b %e, %Y') }}

    {{ entry['Text'] }}

    {% endfor %}

The journal variable
--------------------

Templates receive a single variable: ``journal``, which is a list of entries.
So your template will probably look something like this::

    ... document header, title, etc ...
    {% for entry in journal %}
    ... code for a single entry ...
    {% endfor %}
    ... end of document stuff, etc ...

The Entry object
----------------

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

You insert one of these into your document using double brackets, e.g. ::

    {{ entry['Place Name'] }}

Jinja will just leave a blank space if you try to access a nonexistent key.
If you want to test if a key exists, you can always do ::

    {% if Longitude in entry %}
    ... conditional code
    {% endif %}

Places
------

Each entry also has a ``place`` convenience function. You can use ``entry.place()``
or ``entry.place(4)`` to get a comma-separated list of all the places in order.
If you use ``entry.place(3)``, it will only show the first three levels and leave
off the country. Or ``entry.place(1,4)`` will leave off the "Place Name" and just
show city, state, country. You can get more complicated; for details,
see the code.

Filters
-------

You can use a pipe (``|``) to apply filters in your template.

Formatting dates
~~~~~~~~~~~~~~~~

You can use the  ``format`` filter on a date to control how it is displayed.
For example::

    {{ entry['Date'] | format('%Y-%m-%d %H:%M:%S %z') }}

Markdown
~~~~~~~~

This converts the markdown to html::

    {{ entry['Text'] | markdown }}


Inline images with base64 encoding
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can include the images inline with base64 encoding using a custom filter::

    {{ entry['Photo'] | imgbase64 }}

The resulting entry looks like::

    <img class="entry-photo" src="data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0a ... ">

The base64 data can become quite large in size. If you have the
`Python imaging library`__
installed, you can resize the images so that the resulting output
remains sufficiently small (default maximum size is 400 pixels)::

    {{ entry['Photo'] | imgbase64(800) }}

This includes the image inline with a maxium size of 800 pixels.

__ http://www.pythonware.com/products/pil/

More templating information
---------------------------

For more details on Jinja templates, see the
`Jinja template designer documentation`__.

__ http://jinja.pocoo.org/docs/templates/

