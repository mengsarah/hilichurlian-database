from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.contrib import messages
from django.forms import modelform_factory
from .models import CompleteUtterance, Word
import re
import math

### FORM CLASSES ###
# CompleteUtterance: don't show the words field
CompleteUtteranceForm = modelform_factory(CompleteUtterance, fields=['utterance', 'speaker', 'translation', 'translation_source', 'context', 'source'])

### GLOBAL CONSTANTS ###
DEFAULT_PAGE_SIZE = 10

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

def index(request, page=1):
	render_page = "hilichurlian_database/index.html"
	page_size = DEFAULT_PAGE_SIZE
	if request.method == 'GET' and page > 1:
		render_page = "hilichurlian_database/results.html"
	page_size = request.GET.get('pageSize', DEFAULT_PAGE_SIZE)
	paging = Paginator(CompleteUtterance.objects.all(), page_size)
	return render(request, render_page, {
		'db_page': paging.get_page(page),
		'page_range': paging.page_range,
		'current_page': page,
		'page_size': page_size,
	})

def about(request):
	return render(request, "hilichurlian_database/about.html")

def filter_strict(request):
	utterances = None
	if request.method == 'GET' and 'search' in request.GET:
		req = request.GET
		word = req['search'].strip()
		if len(word) == 0:
			utterances = CompleteUtterance.objects.all()
			messages.error(request, "Please enter a word to search.")
		else:
			utterances = CompleteUtterance.objects.filter(words=word)
			if not utterances.exists():
				utterances = CompleteUtterance.objects.all()
				messages.error(request, "No utterances found for " + word + ". Try another word.")
			else:
				messages.success(request, "Found results for " + word + ".")
	else:
		utterances = CompleteUtterance.objects.all()
		messages.error(request, "No data received")
	return render(request, "hilichurlian_database/results.html", {'db': utterances})

# the /submit page
def data_entry(request):
	# blank form
	submit_form = CompleteUtteranceForm()
	return render(request, "hilichurlian_database/submit.html", {'form': submit_form})