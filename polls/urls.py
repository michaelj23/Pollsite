from django.conf.urls import patterns, url
from polls import views
# URL patterns specific to the POLLS app for Pollsite.
urlpatterns = patterns('',
	url(r'^(?P<user_id>\d+)/polls_page/$', views.polls_page, name='polls_page'),
	url(r'^(?P<user_id>\d+)/make_poll/$', views.make_poll, name='make_poll'),
	url(r'^(?P<user_id>\d+)/creating_poll/$', views.creating_poll, name='creating_poll'),
	url(r'^(?P<question_id>\d+)/(?P<user_id>\d+)/process_remove/$', views.process_remove, name='process_remove'),
	url(r'^(?P<question_id>\d+)/vote_poll/$', views.vote_poll, name='vote_poll'),
	url(r'^(?P<question_id>\d+)/processing_vote/$', views.processing_vote, name='processing_vote'),
)
