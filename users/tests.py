from django.test import TestCase, RequestFactory
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from users import views

# Create your tests here.
# Tests for the user authentication/authorization application.

# Credentials used for tests
username = 'QB'
email = 'joe@gmail.com'
password = 'imthebest'
firstname = 'Joe'
lastname = 'Montana'

def make_user(is_active):
	# Helper function used to create a sample user, whose is_active attribute is determined by the function argument.
	user = User.objects.create_user(username, email, password, first_name=firstname, last_name=lastname)
	user.is_active = is_active
	user.save()
	return user

# Credentials in dictionary form for signing up.
signup_creds = {'firstname': firstname, 'lastname': lastname, 'emailaddress': email, 'username': username, 'password': password}

# Credentials for logging in.
login_creds = {'username': username, 'password': password}

def attempt_signup(testcase, creds):
	# Helper function to simulate signing up.
	return testcase.client.post(reverse('users:processing_signup'), creds, follow=True)

def attempt_login(testcase, creds):
	# Helper function to simulate logging in.
	return testcase.client.get(reverse('users:processing_login'), creds, follow=True)


class UserTests(TestCase):
	def setUp(self):
		# Set up a request factory for the following tests. Note that setUp is called before EVERY test.
		self.factory = RequestFactory()
		self.user = make_user(True)
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
		another_user = dict(signup_creds)
		another_user['username'] = 'anotherQB'
		another_user['emailaddress'] = 'anotherjoe@gmail.com'
		response = attempt_signup(self, another_user)
		self.assertContains(response, 'Welcome, anotherQB!', status_code=200)

	def test_failed_signup_with_missing_fields(self):
		# Check that a signup missing fields redirects back to the signup page with an error message.
		missing_creds = dict(signup_creds)
		missing_creds['firstname'] = ''
		response = attempt_signup(self, missing_creds)
		self.assertContains(response, 'You forgot to fill in some fields.', status_code=200)

	def test_failed_signup_with_taken_username(self):
		# Check that a signup with a taken username redirects back to the signup page with an error message.
		response = attempt_signup(self, signup_creds)
		self.assertContains(response, 'This username is taken.', status_code=200)

	def test_failed_signup_with_taken_email(self):
		# Check that a signup with a taken email redirects back to the signup page with an error message.
		taken_email = dict(signup_creds)
		taken_email['username'] = 'notQB' # so that the error is for a taken email, not username
		response = attempt_signup(self, taken_email)
		self.assertContains(response, 'There is already an account associated with this email.', status_code=200)

	def test_successful_log_in(self):
		# Check that a log in with good credentials leads to the welcome page.
		response = attempt_login(self, login_creds)
		self.assertContains(response, 'Welcome, QB!', status_code=200)

	def test_log_in_with_bad_credentials(self):
		# Check that a log in with non-existing credentials leads back to the index page with an error message.
		response = attempt_login(self, {'username': 'Bad', 'password': 'Credentials'})
		self.assertContains(response, 'The username or password you entered is incorrect.', status_code=200)

	def test_log_in_with_inactive_acccount(self):
		# Check that a log in with an inactive account leads back to the index page with an error message.
		self.user.delete()
		self.user = make_user(False)
		response = attempt_login(self, login_creds)
		self.assertContains(response, 'This account is inactive.', status_code=200)

	def test_unauthorized_welcome_as_nonmember(self):
		# Check that trying to access another user's welcome page as a non-member leads back to the index with an error message.
		response = self.client.get(reverse('users:welcome', args=(self.user.id,)), follow=True)
		self.assertContains(response, 'Welcome to Pollsite', status_code=200)
		self.assertContains(response, 'You are not authorized to view this page.', status_code=200)

	def test_unauthorized_welcome_as_member(self):
		# Check that trying to access another user's welcome page as a registered member leads back to your own polls page with an error message.
		# Note that this test depends on the app with which this users app is coupled (in this case a polls app for Pollsite).
		another_user = dict(signup_creds)
		another_user['username'] = 'notherQb'
		another_user['emailaddress'] = 'notherjoe@gmail.com'
		attempt_signup(self, another_user)
		attempt_login(self, {'username': 'notherQb', 'password': 'imthebest'})
		response = self.client.get(reverse('users:welcome', args=(self.user.id,)), follow=True)
		self.assertContains(response, "notherQb's Polls", status_code=200)
		self.assertContains(response, 'You are not authorized to view this page.', status_code=200)

	def test_index_as_logged_in(self):
		# Check that trying to access the index page when you are logged in redirects you to your welcome page.
		attempt_login(self, login_creds)
		response = self.client.get(reverse('users:index'), follow=True)
		self.assertContains(response, 'Welcome, QB!', status_code=200)

	def test_logout(self):
		# Check that the logging out returns the previous user to the index page.
		attempt_login(self, login_creds)
		response = self.client.get(reverse('users:processing_logout'), follow=True)
		self.assertContains(response, 'Welcome to Pollsite', status_code=200)

	def test_successful_search(self):
		# Check that successfully finding a user by username redirects to their polls page.
		# This test also depends on the coupled app for the redirection.
		another_user = dict(signup_creds)
		another_user['username'] = 'notherQb'
		another_user['emailaddress'] = 'notherjoe@gmail.com'
		attempt_signup(self, another_user)
		attempt_login(self, login_creds)
		url = reverse('users:process_search', args=(self.user.id,))
		response = self.client.get(url, {'search': 'notherQb'}, follow=True)
		self.assertContains(response, "notherQb's Polls", status_code=200)


