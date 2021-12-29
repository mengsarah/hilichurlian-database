from django.contrib import admin, messages
from django.urls import path
from django.shortcuts import render, redirect
from django.forms import modelform_factory
from .models import Word, CompleteUtterance

### FORM CLASSES ###
CompleteUtteranceUpdateForm = modelform_factory(CompleteUtterance, fields=['speaker', 'source'])

### MODEL ADMIN CLASSES ###

class CompleteUtteranceAdmin(admin.ModelAdmin):
	def get_urls(self):
		urls = super().get_urls()
		my_urls = [
			# intermediate action page
			path('update_multiple_define', self.admin_site.admin_view(self.update_multiple_utterances_define)),
			# for POST
			path('update_multiple_execute', self.admin_site.admin_view(self.update_multiple_utterances_execute)),
		]
		return my_urls + urls
	
	# Admin UI
	fieldsets = [
		('Content',				{'fields': ['utterance', 'words']}),
		('Context',				{'fields': ['speaker', 'translation', 'translation_source', 'context', 'source']}),
	]
	list_display = ('__str__', 'speaker', 'source')
	actions = ['update_multiple_utterances']

	@admin.action(description='Unify attributes for selected complete utterances')
	def update_multiple_utterances(self, request, queryset):
		selected = queryset.values_list('pk', flat=True)
		return redirect("./update_multiple_define?ids=" + ','.join(str(pk) for pk in selected))
	
	# Views for bulk updating
	model_info = {
		"the_model": CompleteUtterance,
		"name": "CompleteUtterance",
	}
	def update_multiple_utterances_define(self, request):
		return update_multiple_define(self, request, self.model_info)
	
	def update_multiple_utterances_execute(self, request):
		return update_multiple_execute(self, request, self.model_info)


### VIEWS FOR MULTIPLE MODELS ###

def update_multiple_define(self, request, info_on_model):
	request.current_app = self.admin_site.name
	req = request.GET
	id_list = req.get('ids', "").split(",")
	to_update = info_on_model["the_model"].objects.filter(pk__in=id_list)
	context = dict(
		# from doc: common variables for rendering the admin template
		self.admin_site.each_context(request),
		# specific to app
		model_info = info_on_model,
		ids = id_list,
		objects_to_update = to_update,
		form = CompleteUtteranceUpdateForm(),
	)
	return render(request, "admin/specify-bulk-update.html", context)

# TODO
def update_multiple_execute(self, request):
	request.current_app = self.admin_site.name
	req = request.GET
	id_list = req.get('ids', "")
	context = dict(
		# common variables
		self.admin_site.each_context(request),
		# specific to app
		ids=id_list,
	)
	messages.success(request, "Success")
	return redirect("./")


### ADMIN SITE MODEL REGISTRATION ###

admin.site.register(Word)
admin.site.register(CompleteUtterance, CompleteUtteranceAdmin)