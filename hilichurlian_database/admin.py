from django.contrib import admin
from .models import Word, CompleteUtterance

class CompleteUtteranceAdmin(admin.ModelAdmin):
	fieldsets = [
		('Content',				{'fields': ['utterance', 'words']}),
		('Context',				{'fields': ['speaker', 'translation', 'translation_source', 'context', 'source']}),
	]
	list_display = ('__str__', 'speaker', 'source')

admin.site.register(Word)
admin.site.register(CompleteUtterance, CompleteUtteranceAdmin)