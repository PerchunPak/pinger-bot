API Reference
=============

This page contains auto-generated API reference documentation.

.. warning::
    Currently, API Reference is only available `in English <https://pinger-bot.readthedocs.io/en/latest/>`_\ .

.. toctree::
   :titlesonly:

   {% for page in pages %}
   {% if page.top_level_object and page.display %}
   {{ page.include_path }}
   {% endif %}
   {% endfor %}
