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
	VERSIONS_TWO = [ 2 + (x/10.0) for x in range(5) ] # 2.0 through 2.4
	VERSIONS_RAW = [ *VERSIONS_ONE, *VERSIONS_TWO ]
	version_list = [("0", "Pre-launch")] 
	# "0" is not for utterances that also appear post-launch
	for version in VERSIONS_RAW:
		version_list.append( ( str(version), "Version " + str(version) ) )
	return version_list


### MODELS ###

class Speaker(models.Model):
	SPEAKER_TYPES = [
		("hili", "Hilichurl"),
		("abys", "Abyss Order"),
		("stud", "Student"),
		("unkn", "Unknown"), # e.g. quest UI
	]

	FORM_FIELDS = ['name']
	BULK_UPDATABLE = ['type']

	name = models.CharField(
		max_length = 75,
		help_text = "Provide a living being when possible. Non-living entities such as Quest UI are acceptable as a last resort."
	) # db_index=True later?
	type = models.CharField(max_length=4, choices=SPEAKER_TYPES)

	object_history = HistoricalRecords()

	def __str__(self):
		return self.name

class Source(models.Model):
	VERSIONS = get_version_list()

	FORM_FIELDS = ['url', 'version']
	# auto-populated fields: name
	# manually populated fields: related_sources
	BULK_UPDATABLE = ['version']

	name = models.CharField(
		max_length = 200,
		help_text = "Please enter the name of the source, such as a quest name or item name. (This is not the name of a website or other host of a source.)"
	)
	url = models.CharField(
		max_length = 200,
		help_text = "Must be the URL of an online resource documenting the utterance and its translation if provided."
	)
	version = models.CharField(
		max_length = 3,
		choices = VERSIONS,
		help_text = 'Please select the first live version of Genshin Impact in which this source appeared. Select "Pre-launch" only if this source is a pre-launch post from miHoYo or was never released after Genshin Impact launched.'
	)
	related_sources = models.ManyToManyField(
		"self",
		blank = True, # there may not be any related sources
	)

	object_history = HistoricalRecords()
	
	def __str__(self):
		return self.name

class Word(models.Model):
	FORM_FIELDS = []
	# auto-populated fields: word
	# manually populated fields: variants_same_word, variants_grammatical
	BULK_UPDATABLE = []

	word = models.CharField(
		max_length = 25,
		primary_key = True,
		help_text = "Must be a word that can be found in an utterance."
	)
	variants_same_word = models.ManyToManyField(
		"self",
		verbose_name = "other written forms of this word",
		blank = True, # there may not be variants in the database yet
		help_text = "Select words that are exactly the same as this word and are only elongated, shortened, or otherwise similarly altered. For example, 'yaaaa' is an elongated version of 'ya' and is otherwise the exact same word."
	)
	variants_grammatical = models.ManyToManyField(
		"self",
		verbose_name = "related words",
		blank = True, # there may not be variants in the database yet
		help_text = "Select words that are grammatical variants of this word. These words must not be the same words. For example, 'mi' and 'mimi' are grammatical variants of each other."
	)

	object_history = HistoricalRecords()

	def __str__(self):
		return self.word

class CompleteUtterance(models.Model):
	FORM_FIELDS = ['utterance', 'speaker', 'translation', 'translation_source', 'context', 'source']
	# auto-populated fields: words
	BULK_UPDATABLE = ['speaker', 'source']

	# making the autofield explicit as a reminder
	id = models.AutoField(primary_key=True)
	# because utterances do not have to be unique!
	utterance = models.CharField(
		max_length = 200,
		help_text = "Please enter the full Hilichurlian sentence or phrase that was spoken or written. Individual words are acceptable if they were said as if they were a single sentence, such as in a one-word exclamation."
	)
	words = models.ManyToManyField(Word) # auto assign based on utterance
	speaker = models.ForeignKey(Speaker, on_delete=models.PROTECT) # prevent speaker deletion because it should never happen; if it does, then it needs to be manually handled (e.g. retcon)
	translation = models.CharField(
		max_length = 200,
		blank = True,
		help_text = "If there was a translation given in-game for this specific Hilichurlian sentence or phrase, enter the translation here. Unofficial translations are not allowed, regardless of how well-researched they are. Parentheses can be used for indirect translations, including inference from game mechanics such as successful item turn-in."
	)
	translation_source = models.CharField(
		max_length = 75,
		blank = True,
		help_text = "Required if a translation is provided. Provide an in-game item when possible. Parentheses should be used if the source is a game mechanic, such as successful item turn-in."
	)
	context = models.TextField(
		blank = True,
		help_text = "Should be official material when possible. Include as much as needed."
	)
	source = models.ForeignKey(Source, on_delete=models.PROTECT) # prevent source deletion because it should never happen; if it does, then it needs to be manually handled (e.g. retcon)
	
	object_history = HistoricalRecords()

	def __str__(self):
		return self.utterance