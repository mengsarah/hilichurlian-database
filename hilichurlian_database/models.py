from django.db import models

# database diagram: https://drawsql.app/--93/diagrams/hilichurlian-database

# all data will be official data only (stuff that can be found in the game, not speculation from players)

class Word(models.Model):
	word = models.CharField(max_length=25, primary_key=True)
	translation = models.CharField(max_length=100, blank=True)
	def __str__(self):
		return self.word

class CompleteUtterance(models.Model):
	# making the autofield explicit as a reminder
	id = models.AutoField(primary_key=True)
	# utterances do not have to be unique!
	utterance = models.CharField(max_length=200)
	words = models.ManyToManyField(Word) # auto assign based on utterance
	speaker = models.CharField(max_length=75) # db_index=True later?
	translation = models.CharField(max_length=200, blank=True)
	translation_source = models.CharField(max_length=75, blank=True)
	context = models.TextField(blank=True)
	source = models.CharField(max_length=200) # URL
	def __str__(self):
		return self.utterance