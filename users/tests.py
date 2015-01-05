from django.test import TestCase, RequestFactory
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from users import views

# Create your tests here.
# Tests for the user authentication/authorization application.
def make_user():
	username="John"
	email="john@gmail.com"
	password="test"
	user = User.objects.create_user(username, email, password, first_name="John", last_name="Doe")
	user.save()
	return user

dict_credentials = {'firstname': 'Joe', 'lastname': 'Montana', 'emailaddress': 'joe@gmail.com', 'username': 'QB', 'password': 'imthebest'}


class UserTests(TestCase):
	def setUp(self):
		# Set up a request factory for the following tests.
		self.factory = RequestFactory()
		self.user = make_user()
	def test_index_view(self):
		# Check that the index view works.
		response = self.client.get(reverse('users:index'))
		self.assertEqual(response.status_code, 200)

	def test_signup_view(self):
		# Check that the signup view works.
		response = self.client.get(reverse('users:signup'))
		self.assertEqual(response.status_code, 200)

	def test_successful_signup(self):
		# Check that a successful signup redirects to welcome page.
		response = self.client.post(reverse('users:processing_signup'), dict_credentials, follow=True)
		self.assertContains(response, 'Welcome', status_code=200)

	def test_failed_signup_with_missing_fields(self):
		# Check that a signup missing fields redirects back to the signup page with an error message.
		missing_creds = dict(dict_credentials)
		missing_creds['firstname'] = ''
		response = self.client.post(reverse('users:processing_signup'), missing_creds, follow=True)
		self.assertContains(response, 'You forgot to fill in some fields.', status_code=200)

	def test_failed_signup_with_taken_username(self):
		# Check that a signup with a taken username redirects back to the signup page with an error message.
		response = self.client.post(reverse('users:processing_signup'), dict_credentials, follow=True)
		response = self.client.post(reverse('users:processing_signup'), dict_credentials, follow=True)
		self.assertContains(response, 'This username is taken.', status_code=200)

	def test_failed_signup_with_taken_email(self):
		# Check that a signup with a taken email redirects back to the signup page with an error message.
		response = self.client.post(reverse('users:processing_signup'), dict_credentials, follow=True)
		taken_email = dict(dict_credentials)
		taken_email['username'] = 'notQB' # so that the error is for a taken email, not username
		response = self.client.post(reverse('users:processing_signup'), taken_email, follow=True)
		self.assertContains(response, 'There is already an account associated with this email.', status_code=200)
