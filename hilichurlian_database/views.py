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

# keep order
def remove_duplicates(may_have_duplicates):
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
	utterances = CompleteUtterance.objects.all() # to be updated
	same_variants = {} # to be updated
	grammatical_variants = {} # to be updated
	all_variants = {}
	# initialize search parameters
	want_grammatical_variants = req.get('grammaticalVariants', "").strip()
	speaker = req.get('speaker', "").strip()
	source = req.get('source', "").strip()
	new_search = req.get('newSearch', "")
	# get entered words
	words_as_string = req.get('words', "").strip()
	words_list = re.findall(r'\w+', words_as_string.lower()) # like in add_data()
	words_list = remove_duplicates(words_list)
	# get utterances within search_set that match speaker and source
	if speaker:
		utterances = utterances.filter(speaker__name=speaker)
	if source:
		utterances = utterances.filter(source__url=source)
	# now that the set is smaller, get utterances that have all of the words
	# TODO: use boolean for whether grammatical variants exist?
	# TODO: if wordA's variants_same_word includes wordB and variants_grammatical includes wordC, then wordB's variants_grammatical should also include wordC, but it's not enforced right now
	original_words_list = remove_duplicates(words_list)
	if want_grammatical_variants:
		for w in original_words_list:
			try:
				grammatical_variants[w] = Word.objects.get(word=w).variants_grammatical.all()
			except Word.DoesNotExist:
				words_list.remove(w) # TODO: display user's search criteria that aren't found in the DB
			if grammatical_variants[w] == Word.objects.none():
				grammatical_variants.pop(w)
	original_words_list = remove_duplicates(words_list)
	for w in original_words_list:
		try:
			same_variants[w] = Word.objects.get(word=w).variants_same_word.all()
			if same_variants[w] == Word.objects.none():
				same_variants.pop(w)
		except Word.DoesNotExist:
			words_list.remove(w) # TODO: display user's search criteria that aren't found in the DB
	all_variants = same_variants
	for word, vars in grammatical_variants.items():
		if same_variants[word]:
			all_variants[word] = grammatical_variants[word].union(same_variants[word])
		else:
			all_variants[word] = grammatical_variants[word]
	if all_variants:
		# TODO: handle case where word variations are specifically specified? should they both be required or should they be handled as if only one were entered?
		for w in words_list:
			all_word_utters = CompleteUtterance.objects.filter(words__in=(all_variants[w].union(Word.objects.filter(word=w))))
			utterances = utterances.intersection(all_word_utters)
			if not utterances.exists():
				break
	else:
		# could be optimized, maybe similar to if similar block (ha)
		for w in words_list:
			utterances = utterances.filter(words=w)
			if not utterances.exists():
				break
	# regenerate words_as_string
	words_as_string = ""
	for w in words_list:
		words_as_string = words_as_string + w + " "
	words_as_string = words_as_string[:-1]
	# add info about search
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