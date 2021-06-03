from django.shortcuts import render, redirect
from django.contrib import messages
from django.forms import modelform_factory
from .models import CompleteUtterance, Word

import re

### FORM CLASSES ###
# CompleteUtterance: don't show the words field
CompleteUtteranceForm = modelform_factory(CompleteUtterance, fields=['utterance', 'speaker', 'translation', 'translation_source', 'context', 'source'])

### VIEWS FOR POST ###
def add_data(request):
	if request.method == 'POST':
		data = request.POST
		new_utterance = CompleteUtterance()
		new_utterance.utterance = data['utterance']
		new_utterance.speaker = data['speaker']
		new_utterance.translation = data['translation']
		new_utterance.translation_source = data['translation_source']
		new_utterance.context = data['context']
		new_utterance.source = data['source']
		new_utterance.save()
		# get list of words; luckily, transcribed Hilichurlian is relatively simple
		# (currently don't have to account for punctuation within words)
		utterance_words = re.findall(r'\w+', data['utterance'].lower())
		for utt_word in utterance_words:
			(word_in_db, created) = Word.objects.get_or_create(word=utt_word)
			new_utterance.words.add(word_in_db)
		new_utterance.save()
		messages.success(request, 'Added "' + data['utterance'] + '"')
	else:
		messages.error(request, "No data received")
	return redirect("hilichurlian_database:data_entry")

### VIEWS FOR USERS ###

def index(request):
	return render(request, "hilichurlian_database/index.html", {'db': CompleteUtterance.objects.all()})

# the /submit page
def data_entry(request):
	# blank form
	submit_form = CompleteUtteranceForm()
	return render(request, "hilichurlian_database/submit.html", {'form': submit_form})