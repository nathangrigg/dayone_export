{% for entry in journal %}
{{ entry.localDate|format }}
--------------------------

{{ entry.text }}

{% endfor %}
