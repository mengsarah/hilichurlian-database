from django.db.models import Q
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.contrib import messages
from django.forms import modelform_factory
from .models import Speaker, Source, Word, CompleteUtterance
from .templatetags import describe_url
import re

### FORM CLASSES ###
CompleteUtteranceForm = modelform_factory(CompleteUtterance, fields=CompleteUtterance.FORM_FIELDS)
SourceForm = modelform_factory(Source, fields=Source.FORM_FIELDS)
SpeakerForm = modelform_factory(Speaker, fields=Speaker.FORM_FIELDS)

### GLOBAL CONSTANTS ###
DEFAULT_PAGE_SIZE = 10

### HELPER FUNCTIONS ###

def get_model_class(model_name):
	MODEL_MAPPING = {
		"Speaker": Speaker,
		"Source": Source,
		"Word": Word,
		"CompleteUtterance": CompleteUtterance,
		"Utterance": CompleteUtterance
	}
	return MODEL_MAPPING.get(model_name.capitalize())

def get_forms():
	return [
		{ "form_object": CompleteUtteranceForm(), "name": "utterance", },
		{ "form_object": SourceForm(), "name": "source", },
		{ "form_object": SpeakerForm(), "name": "speaker", }
	]

def remove_duplicates(may_have_duplicates):
	# keep order
	return list(dict.fromkeys(may_have_duplicates))

def make_criteria_message(words_as_string, words_list, speaker, source):
	criteria = []
	if len(words_list) > 0:
		criteria.append(words_as_string)
	if len(speaker) > 0:
		criteria.append(speaker)
	if len(source) > 0:
		criteria.append(source)
	return str(criteria)[1:-1]

# return the context object for the pages when browsing the database
def database_public_view_context(paginator, page_num, page_size, words="", similar = "", speaker="", source=""):
	existing_criteria = "pageSize=" + str(page_size) + "&words=" + words + "&similar=" + similar + "&speaker=" + speaker + "&source=" + source
	return {
		'db_page': paginator.get_page(page_num),
		'page_range': paginator.get_elided_page_range(page_num, on_each_side=2, on_ends=3),
		'page_range2': paginator.get_elided_page_range(page_num, on_each_side=2, on_ends=3),
		'page_size': page_size,
		'criteria': {
			'words': words,
			'similar': similar,
			'speaker': speaker,
			'source': source,
		},
		'existing': existing_criteria,
	}


### VIEWS FOR POST ###

# submit_type is the "name" in the form object in data_entry() (the /submit page)
def add_data(request, submit_type):
	if (request.method == 'POST') and submit_type:
		data = request.POST
		new_entry = submit_type
		if submit_type == "utterance":
			new_entry = CompleteUtterance()
			for label, value in data.items():
				if label in new_entry.SPECIALLY_HANDLED: # find existing ForeignKeys
					(object_for_field, created) = get_model_class(label).objects.get_or_create(id=value)
					setattr(new_entry, label, object_for_field)
				elif label in new_entry.FORM_FIELDS: # valid fields only!
					setattr(new_entry, label, value)
			new_entry.save() # save now for Word ManyToMany
			# get list of words; luckily, simple because no punctuation within words (yet)
			utterance_words = re.findall(r'\w+', data['utterance'].lower())
			for utt_word in utterance_words:
				(word_in_db, created) = Word.objects.get_or_create(word=utt_word)
				new_entry.words.add(word_in_db)
			new_entry.save()
		elif submit_type == "source":
			(source_in_db, created) = Source.objects.get_or_create(
				url = data['url'],
				defaults = { # only use these if source is new
					'name': describe_url.describe_url(data['url']),
					'version': data['version']
				}
			)
			if created:
				new_entry = source_in_db
			else:
				messages.info(request, '"' + str(source_in_db) + '" already exists')
		elif submit_type == "speaker":
			(speaker_in_db, created) = Speaker.objects.get_or_create(
				name = data['name'],
				defaults = { # only use these if speaker is new
					'type': data['type']
				}
			)
			if created:
				new_entry = speaker_in_db
			else:
				messages.info(request, '"' + str(speaker_in_db) + '" already exists')
		else:
			messages.error(request, "No data received")
		if new_entry != submit_type:
			messages.success(request, 'Added "' + str(new_entry) + '"')
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
	return render(
		request,
		render_page,
		database_public_view_context(paging, page, page_size)
	)

# for searching
def filter(request):
	req = request.GET
	# initialize general parameters
	page = req.get('page', 1)
	page_size = req.get('pageSize', DEFAULT_PAGE_SIZE)
	if int(page_size) < 1:
		page_size = 1
	# initialize parameters to be updated
	utterances = CompleteUtterance.objects.all() # results
	all_variants = {} # word variants
	not_words = [] # from user's search
	# initialize search parameters
	want_grammatical_variants = req.get('grammaticalVariants', "").strip()
	speaker = req.get('speaker', "").strip()
	source = req.get('source', "").strip()
	new_search = req.get('newSearch', "")
	words_as_string = req.get('words', "").strip()
	words_list = re.findall(r'\w+', words_as_string.lower()) # like in add_data()
	# TODO: if wordA's variants_same_word includes wordB and variants_grammatical includes wordC, then wordB's variants_grammatical should also include wordC, but that's not enforced in models.py and views.py
	# get words to be searched for
	words_list = remove_duplicates(words_list)
	original_words_list = list(words_list)
	for word_string in original_words_list:
		word_query = Word.objects.filter(word=word_string)
		if not word_query.exists():
			not_words.append(word_string)
			words_list.remove(word_string)
			continue
		word_object = word_query.get()
		all_variants[word_string] = word_object.variants_same_word.union(Word.objects.filter(word=word_string)) # Words are currently not variants of themselves
		if want_grammatical_variants and word_object.variants_grammatical.exists():
			all_variants[word_string] = all_variants[word_string].union(word_object.variants_grammatical.all())
	# regenerate words_as_string
	words_as_string = ""
	for w in words_list:
		words_as_string = words_as_string + w + " "
	words_as_string = words_as_string[:-1]
	# get utterances within search_set that match speaker and source
	if speaker and Speaker.objects.filter(name=speaker).exists():
		utterances = utterances.filter(speaker__name=speaker)
	if source and Source.objects.filter(url=source).exists():
		utterances = utterances.filter(source__url=source)
	# now that the set is smaller, get utterances that have all of the words
	# TODO: handle case where grammatical variations are specifically specified (e.g. user enters "mi mimi") so that anything the user enters is required
	for w in words_list:
		all_word_utters = CompleteUtterance.objects.filter(words__in=(all_variants[w]))
		utterances = utterances.intersection(all_word_utters)
		if not utterances.exists():
			break
	# add info about search
	if not_words:
		messages.error(request, "The following words are not in the database: " + str(not_words)[1:-1])
	if speaker and not Speaker.objects.filter(name=speaker).exists():
		messages.error(request, speaker + " is not a speaker in the database.")
		speaker = ""
	if source and not Source.objects.filter(url=source).exists():
		messages.error(request, source + " is not a source in the database.")
		source = ""
	criteria_message = make_criteria_message(words_as_string, words_list, speaker, source)
	if len(words_list) == 0 and len(speaker) == 0 and len(source) == 0:
		utterances = CompleteUtterance.objects.all()
		if new_search:
			messages.error(request, "Please enter a word, speaker, or source to search.")
	elif not utterances.exists():
		utterances = CompleteUtterance.objects.all()
		if new_search:
			messages.error(request, "No utterances found that satisfy all of the following criteria: " + criteria_message)
	else: # utterances.exists()
		if new_search:
			messages.success(request, "Successfully found utterances that satisfy all of the following criteria: " + criteria_message)
		else:
			messages.info(request, "Showing utterances that satisfy all of the following criteria: " + criteria_message)
	paging = Paginator(utterances.order_by('source', 'id'), page_size)
	return render(
		request,
		"hilichurlian_database/results.html",
		database_public_view_context(paging, page, page_size, words_as_string, want_grammatical_variants, speaker, source)
	)

# the /select page
def view_all_criteria(request):
	sources = Source.objects.order_by('name')
	speakers = Speaker.objects.order_by('type', 'name')
	words = Word.objects.order_by('word')
	return render(request, "hilichurlian_database/select.html", {
		'sources': sources,
		'speakers': speakers,
		'words': words,
		'speaker_types': [ # use Speaker.SPEAKER_TYPES when we have unknown
			("hili", "Hilichurl"),
			("stud", "Student"),
		]
	})

# the /about page
def about(request):
	return render(request, "hilichurlian_database/about.html")

# the /submit page
def data_entry(request):
	return render(request, "hilichurlian_database/submit.html", {'forms': get_forms()})