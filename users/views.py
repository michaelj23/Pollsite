from django.shortcuts import get_object_or_404, render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib import messages

#Views for the USERS app.

# Create your views here.
def index(request):
# View for your website's front page; if the user is already logged in, this will redirect to a WELCOME page for the user.
	if request.user.is_authenticated():
		return HttpResponseRedirect(reverse('users:welcome', args=(request.user.id,)))
	return render(request, 'users/index.html')

def signup(request):
# View for website's sign-up page.
	return render(request, 'users/signup.html', {'error_message': False})

def processing_signup(request):
# View for creating a new user who has just signed up; first checks that all fields are filled and that the desired username and email are free,
# then creates a new User object and logs it in. Finally redirects to the user's WELCOME page.
	firstname = request.POST['firstname']
	lastname = request.POST['lastname']
	emailaddress = request.POST['emailaddress']
	username = request.POST['username']
	password = request.POST['password']
	creds = []
	for cred in (firstname, lastname, emailaddress, username, password):
		if cred:
			creds.append(cred)
	if len(creds) != 5:
		error_message = 'You forgot to fill in some fields.'
	elif authenticate(username=username, password=password) is not None:
		error_message = 'This username is taken.'
	elif User.objects.filter(email=emailaddress):
		error_message = 'There is already an account associated with this email.'
	else:
		error_message = False
	if error_message:
		return render(request, 'users/signup.html', {'error_message': error_message})
	user = User.objects.create_user(username, emailaddress, password, first_name=firstname, last_name=lastname)
	user.save()
	user = authenticate(username=username, password=password)
	login(request, user)
	return HttpResponseRedirect(reverse('users:welcome', args=(user.id,)))

def processing_login(request):
# View that authenticates an attempted login. It returns the user back to the INDEX (front) page if credentials are invalid or inactive.
# Otherwise, the user is redirected to his/her WELCOME page.
	username = request.GET['username']
	password = request.GET['password']
	user = authenticate(username=username, password=password)
	if user is not None:
		if user.is_active:
			login(request, user)
			return HttpResponseRedirect(reverse('users:welcome', args=(user.id,)))
		else:
			messages.add_message(request, messages.INFO, 'This account is inactive.')
			return HttpResponseRedirect(reverse('users:index'))
	messages.add_message(request, messages.INFO, 'The username or password you entered is incorrect.')
	return HttpResponseRedirect(reverse('users:index'))

def welcome(request, user_id):
# View for a user's WELCOME page (the user's user_id is in the url pointing to this view). The view first checks that the user who is logged in
# matches the user for which the WELCOME page is intended (so users cannot simply type in the right URL).
	desired_user = get_object_or_404(User, pk=user_id)
	if request.user != desired_user:
		messages.add_message(request, messages.INFO, 'You are not authorized to view this page.')
		if not request.user.is_authenticated():
			return HttpResponseRedirect(reverse('users:index'))
		return HttpResponseRedirect(reverse('polls:polls_page', args=(request.user.id,)))
	return render(request, 'users/welcome.html', {'user': desired_user})

def processing_logout(request):
# View to log out the current session's user and return to the website's front page.
	logout(request)
	return HttpResponseRedirect(reverse('users:index'))
