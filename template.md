{% for entry in journal %}
{{ times.format(entry['Date'], timezone, '%A, %b %e, %Y') }}
--------------------------
* {{ entry['Text'] }}

{% endfor %}
