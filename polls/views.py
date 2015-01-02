from django.shortcuts import get_object_or_404, render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib import messages
from polls.models import Question, Choice, DictforQuestion, Keyvalue
from django.utils import timezone

#Views for the POLLS app for Pollsite.

def verify_authenticated(request, user_id):
	# Helper function for the following views. It makes sure that the current session's user matches the user to which the desired page belongs.
	# This way, users are unable to make/remove polls for other users. If the users don't match, the view redirects either to Pollsite's front INDEX
	# page (if the current session viewer is not signed up) or to the current session user's polls page with a warning.
	desired_user = get_object_or_404(User, pk=user_id)
	if request.user != desired_user:
		messages.add_message(request, messages.INFO, 'You are not authorized to view this page.')
		if not request.user.is_authenticated():
			return HttpResponseRedirect(reverse('users:index'))
		return HttpResponseRedirect(reverse('polls:polls_page', args=(request.user.id,)))
	raise Exception()

def polls_page(request, user_id):
	# View for the polls page of the user with USER_ID(in the URL). It sets the proper permissions (explained in POLLS_PAGE template) for the
	# session user. It also orders the polls of the polls page owner by publication date.
	desired_user = get_object_or_404(User, pk=user_id)
	can_create, can_vote = True, True
	if request.user != desired_user:
		can_create = False
		if not request.user.is_authenticated():
			can_vote = False
	questions_list = desired_user.question_set.order_by('-date_published')
	return render(request, 'polls/polls_page.html', {'can_create': can_create, 'can_vote': can_vote, 'user': desired_user, 'questions_list': questions_list})

def make_poll(request, user_id):
	# View for the poll creation page of Pollsite.
	try:
		return verify_authenticated(request, user_id)
	except Exception:
		return render(request, 'polls/make_poll.html', {'user': request.user})

def creating_poll(request, user_id):
	# View that processes user input from the MAKE_POLL page. It first makes sure that all fields have been filled by the user and redirects
	# the user back to MAKE_POLL with an error message if this is not the case. Otherwise, it creates a Question object with a Choice set of
	# choices set by the user. It also creates a DictforQuestion object for that question (to eventually store a history of users who have
	# already voted for the question/poll). Finally, it redirects the user to his/her polls page, which should show the new poll.
	try:
		return verify_authenticated(request, user_id)
	except Exception:
		question_text = request.POST['question']
		if not question_text:
			error_message = 'You forgot to fill in some fields.'
			return render(request, 'polls/make_poll.html', {'user': request.user, 'error_message': error_message})
		num_choices = request.POST['selection']
		question = request.user.question_set.create(text=question_text, date_published=timezone.now(), total_votes=0)
		for i in range(int(num_choices)):
			text = request.POST['choice' + str(i+1)]
			if not text:
				question.delete()
				error_message = 'You forgot to fill in some fields.'
				return render(request, 'polls/make_poll.html', {'user': request.user, 'error_message': error_message})
			question.choice_set.create(choice_text=request.POST['choice' + str(i+1)], votes=0)
		dictionary = DictforQuestion(question=question)
		dictionary.save()
		return HttpResponseRedirect(reverse('polls:polls_page', args=(request.user.id,)))

def process_remove(request, question_id, user_id):
	# View that processes the user's request to remove a poll corresponding to QUESTION_ID and belonging to USER_ID. It deletes the poll 
	# or question and then returns to the current session user's polls page AFTER calling VERIFY_AUTHENTICATED.
	try:
		return verify_authenticated(request, user_id)
	except Exception:
		question = get_object_or_404(Question, pk=question_id)
		question.delete()
		return HttpResponseRedirect(reverse('polls:polls_page', args=(request.user.id,)))

def vote_poll(request, question_id):
	# View for the VOTE_POLL page (not for viewers who are not Pollsite users). The view finds the DictforQuestion (see POLLS app's models)
	# corresponding to the Question with QUESTION_ID(in the URL) and checks to see whether the current session user is in the keys of the
	# DictforQuestion's Keyvalue set(i.e. whether or not the user has voted on the Question before). If so, it sets SELECTED_CHOICE_ID to
	# the id of the user's most recent CHOICE in the poll. Otherwise, SELECTED_CHOICE_ID is set to None. Read more about SELECTED_CHOICE_ID's
	# purpose in the VOTE_POLL template.
	if not request.user.is_authenticated():
		messages.add_message(request, messages.INFO, 'You are not authorized to view this page.')
		return HttpResponseRedirect(reverse('users:index'))
	question = get_object_or_404(Question, pk=question_id)
	try:
		selected_choice_id = DictforQuestion.objects.get(question=question).keyvalue_set.get(key=request.user.id).value
	except Keyvalue.DoesNotExist:
		selected_choice_id = None
	return render(request, 'polls/vote_poll.html', {'question': question, 'selected_choice_id': selected_choice_id})

def processing_vote(request, question_id):
	# View that processes a user's vote input for a poll corresponding to QUESTION_ID(in the URL). This is not available for unregistered
	# users. The view first checks that a Choice of the poll was selected; it otherwise redirects the user to VOTE_POLL with an error message.
	# If the user has not previously voted in the poll, the view increments both the poll/question's total votes and the SELECTED_CHOICE's votes 
	# by 1 and stores the user with his/her inpt as a Keyvalue object in the poll's DictforQuestion. If the user HAS previously voted, the view
	# decrements the user's previous Choice by 1, increments his/her new Choice by 1, and updates the Keyvalue corresponding to the user with
	# the id of his/her new choice. Note that in this case, the poll/question's total votes stays the same. The view finally redirects the user
	# back to his/her own polls page with a success message verifying his/her submission.
	if not request.user.is_authenticated():
		messages.add_message(request, messages.INFO, 'You are not authorized to view this page.')
		return HttpResponseRedirect(reverse('users:index'))
	question = get_object_or_404(Question, pk=question_id)
	try:
		selected_choice = question.choice_set.get(pk=request.POST['choice'])
	except (KeyError, Choice.DoesNotExist):
		return render(request, 'polls/vote_poll.html', {'question': question, 'selected_choice_id': None, 'error_message': "You didn't select an available choice."})
	keyvalues = DictforQuestion.objects.get(question=question).keyvalue_set
	if request.user.id not in [keyvalue.key for keyvalue in keyvalues.all()]:
		question.total_votes += 1
		question.save()
		selected_choice.votes += 1
		selected_choice.save()
		keyvalues.create(key=request.user.id, value=selected_choice.id)
	else:
		target = keyvalues.get(key=request.user.id)
		previous_choice = question.choice_set.get(pk=target.value)
		if previous_choice != selected_choice:
			previous_choice.votes -= 1
			previous_choice.save()
			selected_choice.votes += 1
			selected_choice.save()
		target.value = selected_choice.id
		target.save()
	messages.add_message(request, messages.SUCCESS, 'Thanks! Your response has been recorded.')
	return HttpResponseRedirect(reverse('polls:polls_page', args=(request.user.id,)))

def process_search(request, user_id):
	# View for processing a search query (search bar in a user's polls page). If the query matches an existing user's username or full name,
	# the view redirects to THAT user's polls page. Otherwise, it redirects to the current session user's polls page with an error message.
	search_query = request.GET['search']
	try:
		user = User.objects.get(username=search_query)
	except User.DoesNotExist:
		names = [user.first_name + ' ' + user.last_name for user in User.objects.all()]
		if search_query not in names:
			messages.add_message(request, messages.INFO, "The user you're looking for could not be found.")
			return HttpResponseRedirect(reverse('polls:polls_page', args=(user_id,)))
		search_query = search_query.split()
		user = User.objects.get(first_name=search_query[0], last_name=search_query[1])
	return HttpResponseRedirect(reverse('polls:polls_page', args=(user.id,)))
