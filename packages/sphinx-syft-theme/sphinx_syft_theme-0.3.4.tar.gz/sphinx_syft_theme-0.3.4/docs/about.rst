About the Sphinx Syft Theme
===========================

The Sphinx Syft Theme is a `Sphinx Theme <https://www.sphinx-doc.org/en/master/usage/theming.html>`_
that inherits directly from the `Sphinx Basic Theme <https://www.sphinx-doc.org/en/master/usage/theming.html>`_

This theme derived inspirations from:
- `Pydata Sphinx Theme <https://pydata-sphinx-theme.readthedocs.io/en/latest/>`_
- `Sphinx Book Theme <https://sphinx-book-theme.readthedocs.io/en/latest/>`_
- `Sphinx Pythia Theme <https://sphinx-pythia-theme.readthedocs.io/en/latest/about.html>`_

Top Navigation Bar
------------------

The Sphinx Syft Theme added back the fixed top navigation bar influenced by the PyData Sphinx Theme.
The links on the navigation bar can be set with the ``html_theme_options`` ``navbar_links`` option.
This is a list of dictionaries containing a ``name`` key, ``url`` key, and an ``external`` key.  The
``name`` key can be any string that you want to appear in the navbar.  The ``url`` key is a string
containing the URL that should be associated with the ``name`` in the navbar, and the ``external`` key
is a boolean indicating if the link is *external* or not.  (If *external*, an icon will be displayed
next to the ``name`` in the navbar indicating that clicking the link takes you away from the site).
Additionally, the `external links <https://sphinx-syft-theme.readthedocs.io/en/latest/>`_
(``external_links``) option still works, and these links will be displayed after any links specified by
the ``navbar_links`` option.

.. tab-set-code::

  .. code-block:: python

    html_theme = 'sphinx_syft_theme'
    html_theme_options = {
      'navbar_links': [
        {'name': 'Link1',
          'url': 'https://link1.com/some/link',
          'external': True},
        {'name': 'Link2',
          'url': 'https://link2.com/some/other/link'},
      ]
    }

  .. code-block:: yaml

    sphinx:
      config:
        html_theme: sphinx_pythia_theme
        html_theme_options:
          navbar_links:
            - name: Link1
              url: https://link1.com/some/link
              external: True
            - content: Link2
              url: https://link2.com/some/other/link

.. note::

   The ``url`` value can be a Sphinx document name, in addition to an absolute or relative URL.  In fact,
   using Sphinx document names is the best way of generating the link correctly on different pages.

Footer Bar
----------

In addition to the top navigation bar at the top of each page, the footer
bar at the bottom of every page inherited from the Sphinx Book Theme.

By default, the footer bar only contains copyright and additional information about the Sphinx version (if configured).
Three additional sections can be added to the footer: a *logo bar*, a *bottom navigation menu*, and
an *extras* section.

Footer Logo Bar
^^^^^^^^^^^^^^^

The *logo bar* section can be used to add logo images for various partner or collaboration
institutions, products, or other entities involved with site itself. These are spread out
evenly across the footer in a light-gray full-width box.

To add logo images to the *logo bar* in the footer, use the ``footer_logos`` option of the
``html_theme_options`` and then add it to ``footer_start``.  The name given to each logo is
used as the alternate name of the image in HTML.

.. tab-set-code::

  .. code-block:: python

    html_theme_options = {
      'footer_logos': {
        'name1': '_static/images/logo1.svg',
        'name2': '_static/images/logo2.svg',
      },
      "footer_start": ["footer-logos"]
    }

  .. code-block:: yaml

    sphinx:
      config:
        html_theme_options:
          footer_logos:
            name1: _static/images/logo1.svg
            name2: _static/images/logo2.svg

Footer Navigation Menu
^^^^^^^^^^^^^^^^^^^^^^

The *bottom navigation bar* section of the footer is placed directly above the *info* bar (containing
the copyright information, author, last updated, and Sphinx version).  The contents of the *bottom
navigation bar* can be set with the ``footer_menu`` option of the ``html_theme_options``.  This option
defines a list of *columns* with *titles* and unstyled lists of links or text below each title.  Each
column is a dictionary with a ``title`` key containing text for the title of the column, a ``class``
key containing any CSS classes to add to the HTML column division, and an ``items`` key containing a
list of dictionaries containing ``name``, ``url``, and ``external`` keys (with the same meaning as
the keys in the ``navbar_links`` option above).

.. tab-set-code::

  .. code-block:: python

    html_theme_options = {
      'footer_menu': [
        {
          'title': 'Column A',
          'class': 'col-8 col-sm-4 col-md-3 col-lg-2',
          'items': [
            {
              'name': 'Link 1',
              'url': '#local-link-1',
            },
            {
              'name': 'Link 2',
              'url': 'https://external.link/2',
              'external': True,
            },
          ],
        },
        {
          'title': 'Column B',
          'class': 'col-8 col-sm-4 col-md-3 col-lg-2',
          'items': [
            {
              'name': 'Link 3',
              'url': '#local-link-3',
            },
            {
              'name': 'Link 4',
              'url': 'https://external.link/4',
              'external': True,
            },
          ],
        },
      ],
      "footer_start": ["footer-menu"]
    }

  .. code-block:: yaml

    sphinx:
      config:
        html_theme_options:
          footer_menu:
            - title: Column A
              class: col-8 col-sm-4 col-md-3 col-lg-2
              items:
                - name: Link 1
                  url: '#local-link-1'
                - name: Link 2
                  url: https://external.link/2
                  external: True
            - title: Column B
              class: col-8 col-sm-4 col-md-3 col-lg-2
              items:
                - name: Link 3
                  url: '#local-link-3'
                - name: Link 4
                  url: https://external.link/4
                  external: True

Standalone Pages
^^^^^^^^^^^^^^^^

Standalone pages use the ``page-standalone.html`` template in the same way that the
*banner* pages above use the ``page-banner.html`` template.  Standalone pages have
the same heading and text styling used by banner pages, but they do not have extra
padding nor the ability to declare banner backgrounds to the sections.  The
:doc:`/standalone` page is an example of this layout.

Custom Templates
----------------

The Sphinx Syft Theme uses certain custom templates to define how the content in certain
sections of the page will display.  For the links in the top navigation bar, the ``navbar-menu.html``
template is used.  For how to define *banner* and *standalone* page layouts, the ``page-banner.html``
and the ``page-standalone.html`` templates are used.  For footer content, the ``footer-logos.html``,
``footer-info.html``, ``footer-menu.html``, and the ``footer-extra.html`` templates are used.

Anyone can override these templates by putting their own versions of these templates (i.e.,
using the same template filenames) in a ``_templates`` directory within their Sphinx or Jupyter
Book source (at the same level as their ``conf.py`` file).
