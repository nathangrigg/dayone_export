{% for entry in journal %}
{{ entry['Date']|format }}
--------------------------

{{ entry['Text'] }}

{% if 'Photo' in entry %}
![Photo for {{entry['Date']|format}}]({{ entry['Photo'] }})
{% endif %}


{% endfor %}
