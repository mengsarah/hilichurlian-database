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

def index(request):
	req = request.GET
	# initialize parameters
	render_page = "hilichurlian_database/index.html"
	page = req.get('page', 1)
	page_size = req.get('pageSize', DEFAULT_PAGE_SIZE)
	if int(page_size) < 1:
		page_size = 1
	if int(page) > 1:
		# go away, big home page blurb
		render_page = "hilichurlian_database/results.html"
	paging = Paginator(CompleteUtterance.objects.order_by('source', 'id'), page_size)
	return render(request, render_page, {
		'db_page': paging.get_page(page),
		'page_range': paging.page_range,
		'page_size': page_size,
	})

def about(request):
	return render(request, "hilichurlian_database/about.html")

def filter_strict(request, word=""):
	req = request.GET
	# initialize parameters
	utterances = None # to be updated
	page = req.get('page', 1)
	page_size = req.get('pageSize', DEFAULT_PAGE_SIZE)
	if int(page_size) < 1:
		page_size = 1
	# get utterances from word; check URL for word first
	if len(word) > 0:
		utterances = CompleteUtterance.objects.filter(words=word)
	elif 'search' in req:
		word = req['search']
		utterances = CompleteUtterance.objects.filter(words=word)
	else:
		utterances = CompleteUtterance.objects.all()
		messages.error(request, "Please enter a word to search.")
	# add message and update utterances if applicable
	if not utterances.exists():
		utterances = CompleteUtterance.objects.all()
		messages.error(request, "No utterances found for " + word + ". Try another word.")
	elif 'search' in req: # utterances.exists() is True
		messages.success(request, "Found results for " + word + ".")
	# else utterance.exists() is True and word was from URL, not the search field
	# so no message
	paging = Paginator(utterances.order_by('source', 'id'), page_size)
	return render(request, "hilichurlian_database/results.html", {
		'db_page': paging.get_page(page),
		'page_range': paging.page_range,
		'page_size': page_size,
		'word': word,
	})

# the /submit page
def data_entry(request):
	# blank form
	submit_form = CompleteUtteranceForm()
	return render(request, "hilichurlian_database/submit.html", {'form': submit_form})