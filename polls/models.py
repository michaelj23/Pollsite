from django.db import models
from django.contrib.auth.models import User

# Create your models here.
# Models for the POLLS app: a Question with a corresponding set of Choices and a dictionary, or DictforQuestion, that has a set of Keyvalue objects.
# Each Keyvalue will have a KEY corresponding to the id of a user who has voted for the corresponding Question and a VALUE corresponding to the id
# of the Choice for which the KEY most recently voted.
class Question(models.Model):
	user = models.ForeignKey(User)
	text = models.CharField(max_length=200)
	date_published = models.DateTimeField()
	total_votes = models.IntegerField(default=0)
	def __str__(self):
		return self.text

class DictforQuestion(models.Model):
	question = models.OneToOneField(Question, primary_key=True)

class Keyvalue(models.Model):
	dictionary = models.ForeignKey(DictforQuestion)
	key = models.IntegerField()
	value = models.IntegerField()


class Choice(models.Model):
	question = models.ForeignKey(Question)
	choice_text = models.CharField(max_length=200)
	votes = models.IntegerField(default=0)
	def __str__(self):
		return self.choice_text