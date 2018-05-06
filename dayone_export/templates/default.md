{% for entry in journal %}
{{ entry.localDate|format }}
--------------------------

{{ entry.text }}

{% for photo in entry.photos %}
![Photo for {{entry.localDate|format}}]({{ photo.identifier }})
{% endif %}


{% endfor %}
