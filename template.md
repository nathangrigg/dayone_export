{% for entry in journal %}
{{ entry['Date']|format }}
--------------------------
* {{ entry['Text'] }}

{% endfor %}
