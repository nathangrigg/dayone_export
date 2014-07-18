.. highlight:: none

.. _templates:

Create your own template
========================

Templates are written using Jinja2 syntax.
You can learn a lot from their excellent
`Template Designer Documentation`__

__ http://jinja.pocoo.org/docs/templates/

When making your own template, a great place to start from is one of
Day One Export's `built-in templates`__.

__ https://github.com/nathangrigg/dayone_export/tree/master/dayone_export/templates

The journal variable
--------------------

The most important variable that the program passes to the template is named
``journal``. This is a list of Entry_ objects, each of which
represents a single journal entry.

Generally, a template will loop over elements of the journal variable,
like this::

    ... Document header, title, etc ...

    {% for entry in journal %}

        ... Code for a single entry ...

    {% endfor %}

    ... End of document stuff, etc ...


Other variables
---------------

    - ``today``: The current date.


.. _Entry:

The Entry object
----------------

An Entry object behaves a lot like a Python dictionary,
which means you can access the data fields by name.
For example, you use ``entry['Text']`` to get the text of
an entry.

Jinja uses double braces to insert a variable into the document,
so to insert the entry's text at a certain point in the document, you
would include the following line in your template::

    {{ entry['Text'] }}


Here are some keys that an entry may have:

- Basic information:
    - ``Date``
    - ``Text``
    - ``Starred`` (boolean)
    - ``UUID``
    - ``Activity``: Description of motion activity, e.g. "Stationary"
    - ``Step Count``: Number of steps from the motion sensor
    - ``Photo`` (the relative path of the corresponding photo, if it exists)
- Information about the location:
    - ``Place Name`` (e.g. Boom Noodle)
    - ``Locality`` (e.g. Seattle)
    - ``Administrative Area`` (e.g. Washington)
    - ``Country`` (e.g. United States)
    - ``Longitude``
    - ``Latitude``
- Information about the currently-playing music:
    - ``Album``
    - ``Artist``
    - ``Track``
- Information about weather:
    - ``Fahrenheit``
    - ``Celsius``
    - ``Description``
    - ``IconName``
    - ``Sunrise Date``: The date and time of sunrise
    - ``Sunset Date``: The date and time of sunset
    - ``Visibility KM``
    - ``Relative Humidity``
    - ``Pressure MB``
    - ``Wind Bearing``
    - ``Wind Chill Celsius``
    - ``Wind Speed KPH``
- Information about the creation device:
    - ``Device Agent``
    - ``Host Name``
    - ``OS Agent``
    - ``Software Agent``

Jinja will just leave a blank space if you try to access a nonexistent key.
So if an entry has no location information, ``{{ entry['Latitude'] }}``
will have no effect.

For more information, see the documentation for :ref:`Entry`.


Places
------

You may want to combine the place information into a single string.
You can do this with the ``place`` method.

With no arguments, ``entry.place()`` inserts the place names in order from
smallest to largest, separated by commas.

With a single integer argument, ``entry.place(n)`` inserts the place names
from smallest to largest, but only uses the *n* smallest places. For example,
``entry.place(3)`` will always leave off the country.

If you want to get more specific, you can use a list as an argument.
So ``entry.place([1, 3])`` will put the *Locality* and *Country*, but leave
off the *Place Name* and *Administrative Area*.

Finally, you can use an ``ignore`` keyword argument to ignore a specific
string. For example, ``entry.place(ignore="United States")`` will print
the full location information, but leave off the country if it is
"United States".

Don't forget that to insert any of this into the document, you need to put it
inside double braces.

More information is available in the documentation for :ref:`Entry`.


Weather
------

You may want to combine the weather into a single string.
You can do this with the ``weather`` method.

The ``weather`` method takes one parameter to display the temperature as celcius
or fahrenheit. For example, ``entry.weather('F')`` will display the temperature
in fahrenheit. The same can be done for celsius but with ``entry.weather('C')``.

Don't forget that to insert any of this into the document, you need to put it
inside double braces.

More information is available in the documentation for :ref:`Entry`.


Jinja Filters
-------------

Jinja allows you to transform a variable before inserting it into the document,
using a filter which is denoted by a ``|``.

For example, ``{{ entry['Country'] | default("Unknown") }}``
pass the Country through the ``default`` filter, which in turn changes
it to the string ``Unknown`` if the country does not exist.

Since the ``default`` filter can be particularly useful, I will point out
that it may happen that Day One has defined the country to be the
empty string, in which case, the ``default`` filter will let it remain
empty. If you want the filter to be more aggressive (you probably do),
you can use ``{{ entry['Country'] | default("Unknown", true) }}``

There are several `built-in Jinja filters`__ available.

__ http://jinja.pocoo.org/docs/templates/#builtin-filters


Format dates
------------

This program defines a custom filter called ``format`` which formats
dates.

For example::

    {{ entry['Date'] | format('%Y-%m-%d %H:%M:%S %z') }}

The ``format`` filter also accepts an optional timezone argument, which
overrides the native timezone of every entry. For example::

    {{ entry['Date'] | format('%-I:%M %p %Z', tz='America/Los_Angeles') }}

displays the date in US Pacific time, regardless of the timezone where
the entry was recorded.

Convert to Markdown
-------------------

This program defines a custom filter called ``markdown`` which converts
markdown text to html::

    {{ entry['Text'] | markdown }}

Latex Templates
---------------

The standard Jinja template syntax clashes with many Latex control characters.
If you create a Latex template, you will need to use different syntax.

In a Latex template, you use ``\CMD{...}`` instead of ``{% ... %}`` for
block statements and ``\VAR{...}`` instead of ``{{ ... }}`` to insert
variables. For example::

    \CMD{for entry in journal}
    \section{\VAR{entry['Date'] | format}}
    \CMD{endfor}

You will also find the ``escape_tex`` filter useful, which escapes
Latex control characters::

    \VAR{entry['Text'] | escape_tex}

Note that the ``markdown`` filter outputs HTML so should not be used.
There is currently no support for converting markdown input
to formatted Latex output.

Latex templates must end with the ``.tex`` extension.


Inline images with base64 encoding
----------------------------------

You can include the images inline with base64 encoding using a custom filter::

    {{ entry['Photo'] | imgbase64 }}

The resulting entry looks like::

    <img class="entry-photo" src="data:image/jpeg;base64,/9j/4AAQSkZJRgABA... ">

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
