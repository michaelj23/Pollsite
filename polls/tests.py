from django.test import TestCase, RequestFactory
from users.tests import username, email, password, firstname, lastname, make_user, signup_creds, login_creds, attempt_signup, attempt_login
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, AnonymousUser
from django.contrib.auth import authenticate, login, logout
from polls.models import Question, Choice, DictforQuestion
from django.utils import timezone

# Create your tests here.
# Tests for the polls application for Pollsite.

# Credentials for another Pollsite member besides the one imported from the users app's tests.
another_signup_creds = dict(signup_creds)
another_signup_creds['username'] += 'another'
another_signup_creds['emailaddress'] += 'another'
another_login_creds = {'username': another_signup_creds['username'], 'password': another_signup_creds['password']}

def check_nonmember_unauthorized(testcase, url):
	# General helper function to check that non-members trying to access confidential pages of members are redirected to the index page of the site.
	response = testcase.client.get(url, follow=True)
	testcase.assertContains(response, 'Welcome to Pollsite', status_code=200)
	testcase.assertContains(response, 'You are not authorized to view this page.')

def check_member_unauthorized(testcase, url):
	# General helper function to check the members trying to access confidential pages of other members are redirected to their own polls page.
	attempt_signup(testcase, another_signup_creds)
	attempt_login(testcase, another_login_creds)
	response = testcase.client.get(url, follow=True)
	testcase.assertContains(response, another_signup_creds['username']+"'s Polls", status_code=200)
	testcase.assertContains(response, 'You are not authorized to view this page.')

# Sample question used in tests.
sample_question_1 = {'question': 'How are you?', 'selection': '3', 'choice1': 'Good', 'choice2': 'Okay', 'choice3': 'Bad'}

def create_poll(testcase, question):
	# Helper function for creating a poll with QUESTION credentials.
	return testcase.client.post(reverse('polls:creating_poll', args=(testcase.user.id,)), question, follow=True)

def create_poll_and_return_question(testcase, question):
	# Helper function for creating a poll with QUESTION credentials and returning that poll so that tests can use its id.
	result = testcase.user.question_set.create(text=question['question'], date_published=timezone.now(), total_votes=0)
	for i in range(int(question['selection'])):
			result.choice_set.create(choice_text=sample_question_1['choice'+str(i+1)], votes=0)
	dictionary = DictforQuestion(question=result)
	dictionary.save()
	return result

def vote(testcase, question_id, choice_id):
	return testcase.client.post(reverse('polls:processing_vote', args=(question_id,)), {'choice': choice_id}, follow=True)

class PollsTests(TestCase):
	def setUp(self):
		# Set up a request factory for the following tests. Note that setUp is called before EVERY test.
		self.factory = RequestFactory()
		self.user = make_user(True)

	def test_polls_page_as_page_owner(self):
		# Check that visiting your own polls page gives you the option to create and remove your own polls and log out.
		# Also check that the text "No polls yet!" shows when no polls have been made.
		attempt_login(self, login_creds)
		response = self.client.get(reverse('polls:polls_page', args=(self.user.id,)), follow=True)
		self.assertContains(response, username+"'s Polls", status_code=200)
		self.assertContains(response, 'Create a new poll')
		self.assertContains(response, 'Remove a poll')
		self.assertContains(response, 'Logout')
		self.assertContains(response, 'No polls yet!')

	def test_polls_page_as_another_member(self):
		# Check that visiting another member's polls page gives you the option to log out but not to create/remove polls.
		attempt_signup(self, another_signup_creds)
		attempt_login(self, another_login_creds)
		response = self.client.get(reverse('polls:polls_page', args=(self.user.id,)), follow=True)
		self.assertContains(response, 'Logout', status_code=200)
		self.assertContains(response, username+"'s Polls")
		self.assertNotContains(response, 'Create a new poll')
		self.assertNotContains(response, 'Remove a poll')
		self.assertContains(response, 'No polls yet!')

	def test_polls_page_as_nonmember(self):
		# Check that visiting a Pollsite member's poll page as a nonmember does not let you log out, create, or remove polls.
		response = self.client.get(reverse('polls:polls_page', args=(self.user.id,)), follow=True)
		self.assertContains(response, username+"'s Polls", status_code=200)
		self.assertNotContains(response, 'Logout')
		self.assertNotContains(response, 'Create a new poll')
		self.assertNotContains(response, 'Remove a poll')
		self.assertContains(response, 'No polls yet!')

	def test_make_poll_page(self):
		# Check that the make_poll page does not result in a 404, and that other members/non-members can't access your make_poll page
		# and make polls for you.
		url = reverse('polls:make_poll', args=(self.user.id,))
		check_nonmember_unauthorized(self, url)
		check_member_unauthorized(self, url)
		attempt_login(self, login_creds)
		response = self.client.get(url, follow=True)
		self.assertContains(response, 'Make your own poll!', status_code=200)

	def test_create_successful_poll(self):
		# Check that creating a poll successfully redirects the user to his/her polls page, which should have the new question with 0 votes.
		url = reverse('polls:creating_poll', args=(self.user.id,))
		check_nonmember_unauthorized(self, url)
		check_member_unauthorized(self, url)
		attempt_login(self, login_creds)
		response = create_poll(self, sample_question_1)
		self.assertContains(response, username+"'s Polls", status_code=200)
		self.assertContains(response, sample_question_1['question'])
		self.assertNotContains(response, 'No polls yet!')
		self.assertContains(response, '<td>0</td>', html=True) # check that the created poll has 0 total votes.

	def test_create_poll_with_missing_fields(self):
		# Check that creating a poll without filling in all fields redirects the user back to the make poll page without making a poll.
		attempt_login(self, login_creds)
		missing_question = dict(sample_question_1)
		missing_choice = dict(sample_question_1)
		missing_question['question'] = ''
		missing_choice['choice1'] = ''
		response_missing_question = create_poll(self, missing_question)
		response_missing_choice = create_poll(self, missing_choice)
		response_polls_page = self.client.get(reverse('polls:polls_page', args=(self.user.id,)), follow=True)
		self.assertContains(response_missing_question, 'Make your own poll!', status_code=200)
		self.assertContains(response_missing_question, 'You forgot to fill in some fields.')
		self.assertContains(response_missing_choice, 'Make your own poll!', status_code=200)
		self.assertContains(response_missing_choice, 'You forgot to fill in some fields.')
		self.assertContains(response_polls_page, 'No polls yet!')

	def test_remove_poll(self):
		# Check that removing a poll from the user's polls page is successful.
		question = create_poll_and_return_question(self, sample_question_1)
		url = reverse('polls:process_remove', args=(question.id, self.user.id,))
		check_nonmember_unauthorized(self, url)
		check_member_unauthorized(self, url)
		attempt_login(self, login_creds)
		response = self.client.delete(url, follow=True)
		self.assertContains(response, username+"'s Polls", status_code=200)
		self.assertContains(response, 'No polls yet!')

	def test_new_voter_no_checked_choice(self):
		# Check that a new user to a poll has no initially checked choice.
		question = create_poll_and_return_question(self, sample_question_1)
		url = reverse('polls:vote_poll', args=(question.id,))
		check_nonmember_unauthorized(self, url)
		attempt_login(self, login_creds)
		response = self.client.get(url, follow=True)
		self.assertNotContains(response, 'checked', html=True)

	def test_successful_processing_vote_of_new_voter(self):
		# Check that a new voter voting results in 4 things:
		# 1) the voter is redirected to his/her own polls page.
		# 2) the total votes of that poll increments by 1.
		# 3) the votes of the selected choice increments by 1.
		# 4) the voter is no longer new and will see his previous choice checked when revisiting the vote page for that poll.
		question = create_poll_and_return_question(self, sample_question_1)
		id_selected_choice = question.choice_set.get(choice_text=sample_question_1['choice1']).id
		url = reverse('polls:processing_vote', args=(question.id,))
		check_nonmember_unauthorized(self, url)
		attempt_signup(self, another_signup_creds)
		attempt_login(self, another_login_creds)
		response = vote(self, question.id, id_selected_choice)
		self.assertContains(response, another_signup_creds['username']+"'s Polls", status_code=200)
		self.assertContains(response, 'Thanks! Your response has been recorded.')
		response = self.client.get(reverse('polls:vote_poll', args=(question.id,)), follow=True)
		self.assertContains(response, \
			'<input class="choices" type="radio" name="choice" value="'+str(id_selected_choice)+'" checked/>', \
			status_code=200, html=True
			)
		self.assertContains(response, \
			'<div class="progress-bar progress-bar-striped active" role="progressbar" aria-valuenow="1" aria-valuemin="0" aria-valuemax="1" \
				style="width: 100%" id="'+str(id_selected_choice)+'">1</div>', \
			html=True
			)

	def test_successful_processing_vote_of_old_voter(self):
		# Check that an old voter voting results in 4 things:
		# 1) the voter is redirected to his/her own polls page.
		# 2) the total votes of the voted poll remains the same.
		# 3) the votes of the voter's new choice increments by 1 and is selected/checked.
		# 4) the votes of the voter's old choice decrements by 1.
		question = create_poll_and_return_question(self, sample_question_1)
		id_old_choice = question.choice_set.get(choice_text=sample_question_1['choice1']).id
		id_new_choice = question.choice_set.get(choice_text=sample_question_1['choice2']).id
		attempt_login(self, login_creds)
		vote(self, question.id, id_old_choice)
		response = vote(self, question.id, id_new_choice)
		self.assertContains(response, username+"'s Polls", status_code=200)
		self.assertContains(response, 'Thanks! Your response has been recorded.')
		response = self.client.get(reverse('polls:vote_poll', args=(question.id,)), follow=True)
		self.assertContains(response, \
			'<input class="choices" type="radio" name="choice" value="'+str(id_new_choice)+'" checked/>', \
			status_code=200, html=True
			)
		self.assertNotContains(response, \
			'<input class="choices" type="radio" name="choice" value="'+str(id_old_choice)+'" checked/>', \
			status_code=200, html=True
			)
		self.assertContains(response, \
			'<div class="progress-bar progress-bar-striped active" role="progressbar" aria-valuenow="1" aria-valuemin="0" aria-valuemax="1" \
				style="width: 100%" id="'+str(id_new_choice)+'">1</div>', \
			html=True
			)
		self.assertContains(response, \
			'<div class="progress-bar progress-bar-striped active" role="progressbar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="1" \
				style="width: 0%" id="'+str(id_old_choice)+'">0</div>', \
			html=True
			)

	def test_unsuccessful_processing_vote(self):
		# Check that not selecting a choice for a poll will redirect back to the voting page with an error message.
		# Also check that no vote is actually processed.
		question = create_poll_and_return_question(self, sample_question_1)
		attempt_signup(self, another_signup_creds)
		attempt_login(self, another_login_creds)
		response = self.client.post(reverse('polls:processing_vote', args=(question.id,)), follow=True) # no choice selected
		self.assertContains(response, 'Poll Voting', status_code=200)
		self.assertContains(response, 'You did not select an available choice.')
		response = self.client.get(reverse('polls:polls_page', args=(self.user.id,)), follow=True)
		self.assertContains(response, '<td>0</td>', html=True) # Poll still has 0 total votes




