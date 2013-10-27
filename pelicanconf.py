#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = u'Andrey Devyatkin'
SITENAME = u'Andrey\'s blog a.k.a. Brain Dump Point'
SITEURL = 'https://www.andreydevyatkin.com'
TIMEZONE = 'Sweden/Stockholm'

DEFAULT_LANG = u'en'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None

# Social widget
SOCIAL = (('twitter', 'https://twitter.com/Andrey9kin'),
          ('facebook', 'https://www.facebook.com/andrey.devyatkin'),
          ('github', 'https://github.com/andrey9kin'),
          ('linkedin', 'http://www.linkedin.com/in/andreydevyatkin'),
          ('google-plus', 'https://plus.google.com/111714255902550264848'),
          )

DEFAULT_PAGINATION = 10

THEME = 'Just-Read'

TWITTER_USERNAME = 'Andrey9kin'

ARTICLE_URL = 'archives/{slug}/'
ARTICLE_SAVE_AS = 'archives/{slug}/index.html'

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True
