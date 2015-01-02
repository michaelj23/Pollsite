from django.conf.urls import patterns, include, url
from django.contrib import admin

#The pollsite consists of two apps: a user authentication/authorization (USER) system and a voting system (POLLS).
urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'pollsite.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^', include('users.urls', namespace='users')),
    url(r'^polls/', include('polls.urls', namespace='polls')),
    url(r'^admin/', include(admin.site.urls)),
)
