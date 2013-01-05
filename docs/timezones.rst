Time Zone Information
=====================

The Day One apps store all dates in UTC. Newer versions of Day One
also include the time zone where each journal entry was entered.

Entries without time zone information
-------------------------------------

Older versions of Day One did not record the current time zone in
the journal entry. For these entries, ``dayone_export`` makes a guess
based on the time zone in other entries.

If you would like to manually set the time zone in a journal entry which was
recorded with an older version of Day One, insert the following section
directly into the entry's plist file::

	<key>Time Zone</key>
	<string>America/Los_Angeles</string>

This should be a key in the top-level dictionary. For more guidance
on where to place it, look at an entry created by a current version
of Day One.

Time Zone Names
---------------

A list of time zone names can be found at
http://en.wikipedia.org/wiki/List_of_tz_database_time_zones.

