from django.db.models import Q
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

### HELPER FUNCTIONS ###

def make_criteria_message(words_as_string, words_list, speaker, source):
	criteria = []
	if len(words_list) > 0:
		criteria.append(words_as_string)
	if len(speaker) > 0:
		criteria.append(speaker)
	if len(source) > 0:
		criteria.append(source)
	return str(criteria)[1:-1]


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
		'page_range': paging.get_elided_page_range(page, on_each_side=2, on_ends=3),
		'page_range2': paging.get_elided_page_range(page, on_each_side=2, on_ends=3),
		'page_size': page_size,
		'criteria': {
			'words': "",
			'speaker': "",
			'source': "",
		},
	})

# for searching
def filter_strict(request):
	req = request.GET
	# initialize general parameters
	utterances = CompleteUtterance.objects.all() # to be updated
	page = req.get('page', 1)
	page_size = req.get('pageSize', DEFAULT_PAGE_SIZE)
	if int(page_size) < 1:
		page_size = 1
	# initialize search parameters:
	# text from user: searchWords (multiple), searchSpeaker (1), searchSource (1)
	# and searchSet is either searchAll (default) or searchSubset
	words_as_string = req.get('searchWords', "").strip()
	words_list = re.findall(r'\w+', words_as_string.lower()) # like in add_data()
	speaker = req.get('searchSpeaker', "").strip()
	source = req.get('searchSource', "").strip()
	search_set = req.get('searchSet', "all")
	# get utterances within search_set that match speaker and source
	if speaker != "":
		utterances = utterances.filter(speaker=speaker)
	if source != "":
		utterances = utterances.filter(source=source)
	# now that the set is smaller, get utterances that have all of the words
	for w in words_list:
		utterances = utterances.filter(words=w)
	# add success/fail message if this is a new search (rather than pagination)
	if req.get('newSearch', "no") == "yes":
		criteria_message = make_criteria_message(words_as_string, words_list, speaker, source)
	if len(words_list) == 0 and len(speaker) == 0 and len(source) == 0:
		utterances = CompleteUtterance.objects.all()
		if req.get('newSearch', "no") == "yes":
			messages.error(request, "Please enter a word, speaker, or source to search.")
	elif not utterances.exists():
		utterances = CompleteUtterance.objects.all()
		if req.get('newSearch', "no") == "yes":
			messages.error(request, "No utterances found that satisfy all of the following criteria: " + criteria_message)
	else: # utterances.exists() is True
		if req.get('newSearch', "no") == "yes":
			messages.success(request, "Successfully found utterances that satisfy all of the following criteria: " + criteria_message)
	paging = Paginator(utterances.order_by('source', 'id'), page_size)
	return render(request, "hilichurlian_database/results.html", {
		'db_page': paging.get_page(page),
		'page_range': paging.get_elided_page_range(page, on_each_side=2, on_ends=3),
		'page_range2': paging.get_elided_page_range(page, on_each_side=2, on_ends=3),
		'page_size': page_size,
		'criteria': {
			'words': words_as_string,
			'speaker': speaker,
			'source': source,
		},
	})

def about(request):
	return render(request, "hilichurlian_database/about.html")

# the /submit page
def data_entry(request):
	# blank form
	submit_form = CompleteUtteranceForm()
	return render(request, "hilichurlian_database/submit.html", {'form': submit_form})