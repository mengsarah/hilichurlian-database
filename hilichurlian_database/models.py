from django.db import models
from simple_history.models import HistoricalRecords # for logging changes

# original database diagram: https://drawsql.app/--93/diagrams/hilichurlian-database
# all data will be official data only (stuff that can be found in the game, not speculation from players)

# BULK UPDATABLE FIELDS ARE DEFINED IN admin.py
# need to define __setattr__(self, name, value) when there are non-string bulk updatable fields because there are strings galore in the method in admin

### CONSTANTS ###

# updated for Version 2.4 (January 2022)
def get_version_list():
	VERSIONS_ONE = [ 1 + (x/10.0) for x in range(7) ] # 1.0 through 1.6
	VERSIONS_TWO = [ 2 + (x/10.0) for x in range(9) ] # 2.0 through 2.8
	VERSIONS_THREE = [ 3 + (x/10.0) for x in range(6) ] # 3.0 through 3.5
	VERSIONS_RAW = [ *VERSIONS_ONE, *VERSIONS_TWO, *VERSIONS_THREE ]
	version_list = [("0", "Pre-launch")] 
	# "0" is not for utterances that also appear post-launch
	for version in VERSIONS_RAW:
		version_list.append( ( str(version), "Version " + str(version) ) )
	return version_list


### MODELS ###

##### ABSTRACT MODELS #####

class Entry(models.Model):
	def get_fields_as_dict(self, order=[]):
		# helper function
		def get_value_for_dict(field):
			# TODO: just string and not list for anything other than many-to-many
			value_for_dict = []
			if field.many_to_one:
				# go get the other object
				value_for_dict.append(field.related_model.objects.get(id=field.value_to_string(self)))
			elif field.many_to_many:
				# identify the other objects
				for related_object in getattr(self, field.name).all():
					# go get the other objects
					value_for_dict.append(field.related_model.objects.get(pk=related_object))
			elif field.choices:
				value_for_dict.append(getattr(self, 'get_%s_display' % field.name)())
			else:
				value_for_dict.append(field.value_to_string(self))
			if value_for_dict and not value_for_dict[0]:
				value_for_dict = []
			return value_for_dict
		
		# get fields as dict
		fields_dict = {}
		if order:
			for field_name in order:
				field = self.__class__._meta.get_field(field_name)
				fields_dict[field.verbose_name] = get_value_for_dict(field)
		else:
			for field in self.__class__._meta.get_fields():
				fields_dict[field.verbose_name] = get_value_for_dict(field)
		return fields_dict
	
	class Meta:
		abstract = True

##### CONCRETE MODELS #####

# All concrete models have the following constants:
## FORM_FIELDS
### for which fields should show up in user-facing forms
## SPECIALLY_HANDLED
### a subset of FORM_FIELDS; for which fields' values upon submission via aforementioned forms cannot simply be pasted into the corresponding model fields due to needing to look up a ForeignKey, checking if an object already exists with the value, etc.
## BULK_UPDATABLE
### for which fields can be updated in bulk in the admin site

class Speaker(Entry):
	SPEAKER_TYPES = [
		("hili", "Hilichurl"),
		# ("abys", "Abyss Order"),
		("stud", "Student"),
		("unkn", "Unknown"), # e.g. quest UI
	]

	FORM_FIELDS = ['name', 'type']
	SPECIALLY_HANDLED = [] # form submission needs get_or_create()
	BULK_UPDATABLE = ['type']

	name = models.CharField(
		max_length = 75,
		help_text = "Provide a living being when possible. Non-living entities such as Quest UI are acceptable as a last resort."
	) # db_index=True later?
	type = models.CharField(max_length=4, choices=SPEAKER_TYPES)

	object_history = HistoricalRecords()

	def __str__(self):
		return self.name

class Source(Entry):
	VERSIONS = get_version_list()

	FORM_FIELDS = ['url', 'version']
	SPECIALLY_HANDLED = [] # form submission needs get_or_create()
	# auto-populated fields: name
	# manually populated fields: related_sources
	BULK_UPDATABLE = ['version']

	name = models.CharField(
		max_length = 200,
		help_text = "Name of the source. E.g., a quest name, an item name. (This is not the name of a website or other host of a source.)"
	)
	url = models.CharField(
		verbose_name = "URL",
		max_length = 200,
		help_text = "The URL of an online resource documenting the utterance and its translation if provided."
	)
	version = models.CharField(
		max_length = 3,
		choices = VERSIONS,
		help_text = 'The first live version of Genshin Impact in which this source appeared. Select "Pre-launch" only if the source is a pre-launch post from miHoYo or was never released after Genshin Impact launched.'
	)
	related_sources = models.ManyToManyField(
		"self",
		blank = True, # there may not be any related sources
	)

	object_history = HistoricalRecords()
	
	def __str__(self):
		return self.name

class Word(Entry):
	FORM_FIELDS = []
	# auto-populated fields: word
	# manually populated fields: variants_same_word, variants_grammatical
	BULK_UPDATABLE = []

	word = models.CharField(
		max_length = 25,
		primary_key = True,
		help_text = "Must be a word that can be found in an utterance."
	)
	# TODO: if wordA's variants_same_word includes wordB and variants_grammatical includes wordC, then wordB's variants_grammatical should also include wordC, right?
	variants_same_word = models.ManyToManyField(
		"self",
		verbose_name = "other written forms of this word",
		blank = True, # there may not be variants in the database yet
		help_text = "Words that are exactly the same as this word. For example, 'yaaaa' is exactly the same word as 'ya' and is only elongated."
	)
	variants_grammatical = models.ManyToManyField(
		"self",
		verbose_name = "related words",
		blank = True, # there may not be variants in the database yet
		help_text = "Different words that are likely grammatical variants of this word. For example, 'mi' and 'mimi' are likely grammatical variants of each other."
	)

	object_history = HistoricalRecords()

	def __str__(self):
		return self.word

class CompleteUtterance(Entry):
	FORM_FIELDS = ['utterance', 'speaker', 'translation', 'translation_source', 'context', 'source']
	SPECIALLY_HANDLED = ['speaker', 'source']
	# auto-populated fields: words
	BULK_UPDATABLE = ['speaker', 'source']

	# making the autofield explicit as a reminder
	id = models.AutoField(primary_key=True)
	# because utterances do not have to be unique!
	utterance = models.CharField(
		max_length = 200,
		help_text = "The full Hilichurlian sentence or phrase that was spoken or written. Individual words acceptable if said as a single sentence, such as in a one-word exclamation."
	)
	words = models.ManyToManyField(Word) # auto assign based on utterance
	speaker = models.ForeignKey(Speaker, on_delete=models.PROTECT) # prevent speaker deletion because it should never happen; if it does, then it needs to be manually handled (e.g. retcon)
	translation = models.CharField(
		max_length = 200,
		blank = True,
		help_text = 'The translation for this exact utterance, if available. Unofficial translations are not allowed, regardless of how well-researched they are. Alterations acceptable to match utterance (e.g., "He said he wants to eat meat." can be "[I want to eat meat.]"); use brackets. Indirect translations acceptable, including inference from game mechanics (e.g., item submission); use parentheses.'
	)
	translation_source = models.CharField(
		max_length = 75,
		blank = True,
		help_text = "Required if a translation is provided. Provide an in-game item when possible. Parentheses should be used if the source is a game mechanic, such as item submission."
	)
	context = models.TextField(
		blank = True,
		help_text = "Official material when possible. Include as much as needed."
	)
	source = models.ForeignKey(Source, on_delete=models.PROTECT) # prevent source deletion because it should never happen; if it does, then it needs to be manually handled (e.g. retcon)
	
	object_history = HistoricalRecords()

	def __str__(self):
		return self.utterance