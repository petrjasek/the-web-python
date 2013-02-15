from __future__ import unicode_literals
from django.conf.urls import patterns, include, url

urlpatterns = patterns('superdesk.views',
    url(r'^$', 'home', name='home'),
    url(r'^i/(?P<item_id>.+)$', 'item', name='item'),
)
