from django.conf.urls import patterns, url
from users import views
# URL patterns for the user authentication app.
urlpatterns = patterns('', 
	url(r'^$', views.index, name='index'),
	url(r'^/signup/$', views.signup, name='signup'),
	url(r'^/processingsignup/$', views.processing_signup, name='processing_signup'),
	url(r'^/processinglogin/$', views.processing_login, name='processing_login'),
	url(r'^/welcome/(?P<user_id>\d+)/$', views.welcome, name='welcome'),
	url(r'^/processinglogout/$', views.processing_logout, name='processing_logout'),
	url(r'^/process_search/from/(?P<user_id>\d+)/$', views.process_search, name='process_search'),
)