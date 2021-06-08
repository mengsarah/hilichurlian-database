from django.shortcuts import render, redirect
from django.contrib import messages
from django.forms import modelform_factory
from .models import CompleteUtterance, Word
import re
import math

### FORM CLASSES ###
# CompleteUtterance: don't show the words field
CompleteUtteranceForm = modelform_factory(CompleteUtterance, fields=['utterance', 'speaker', 'translation', 'translation_source', 'context', 'source'])

### GLOBAL CONSTANTS ###
DEFAULT_PAGE_START = 0
DEFAULT_PAGE_SIZE = 10

### HELPER FUNCTIONS ###

# returns valid page size
def get_valid_page_size(size, request):
	page_size = DEFAULT_PAGE_SIZE
	try:
		page_size = int(size)
	except:
		messages.error(request, "Invalid page size. Page size must be a plain number.")
		page_size = DEFAULT_PAGE_SIZE
	if page_size < 1:
		page_size = 1
	return page_size

# returns a dict with keys 'page_start', 'page_size', and 'num_pages'
def get_pagination(start, size, request):
	page_size = get_valid_page_size(size, request)
	num_pages = math.ceil(CompleteUtterance.objects.count() / page_size)
	# get valid page start
	page_start = DEFAULT_PAGE_START
	try:
		page_start = int(start)
	except:
		messages.error(request, "Invalid page start. Page start must be a plain number.")
		page_start = DEFAULT_PAGE_START
	if page_start < 0:
		page_start = DEFAULT_PAGE_START
	if page_start > num_pages:
		page_start = num_pages
	return {
		'page_start': page_start,
		'page_size': page_size,
		'num_pages': num_pages
	}


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
	db = CompleteUtterance.objects.all()
	page_start = DEFAULT_PAGE_START
	page_size = DEFAULT_PAGE_SIZE
	num_pages = None # definitely will be updated
	# pagination
	if request.method == 'GET' and any(p in request.GET for p in ['page_start', 'page_size']):
		# any() to catch cases where exactly one is given
		req = request.GET
		try:
			valid_pagination_values = get_pagination(req['page_start'], req['page_size'], request)
			page_start = get_pagination['page_start']
			page_size = get_pagination['page_start']
			num_pages = get_pagination['num_pages']
		except:
			messages.error(request, "Something went wrong while trying to view the data you wanted.")
			page_start = DEFAULT_PAGE_START
			page_size = DEFAULT_PAGE_SIZE
		# slice db to "current page"
		db = db[page_start : page_start + page_size]
	if num_pages is None:
		num_pages = math.ceil(CompleteUtterance.objects.count() / page_size)
	current_page = math.ceil(page_start / page_size) + 1
	if current_page > num_pages:
		current_page = num_pages
	return render(request, "hilichurlian_database/index.html", {
		'db': db,
		'page_start': page_start,
		'page_size': page_size,
		'num_pages': range(num_pages),
		'current_page': current_page,
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