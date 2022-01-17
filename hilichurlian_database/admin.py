from django.contrib import admin, messages
from django.urls import path
from django.shortcuts import render, redirect
from django.forms import ModelForm
from .models import Speaker, Source, Word, CompleteUtterance

# for logging updates
from simple_history.admin import SimpleHistoryAdmin
from simple_history.utils import bulk_update_with_history

### FORM CLASSES ###
# CompleteUtteranceUpdateForm = modelform_factory(
# 	CompleteUtterance,
# 	fields = CompleteUtterance.BULK_UPDATABLE
# )

class CompleteUtteranceUpdateForm(ModelForm):
	class Meta:
		model = CompleteUtterance
		fields = CompleteUtterance.BULK_UPDATABLE

	def __init__(self, *args, **kwargs):
		super(CompleteUtteranceUpdateForm, self).__init__(*args, **kwargs)
		# this is only an update form, not an instantiation form
		for field in self.fields:
			self.fields[field].required = False



### MODEL ADMIN CLASSES ###

class CompleteUtteranceAdmin(SimpleHistoryAdmin):
	# for use when I have a CompleteUtteranceAdmin instance
	MODEL_CLASS = CompleteUtterance
	MODEL_NAME = "CompleteUtterance"

	# admin-only views 
	def get_urls(self):
		urls = super().get_urls()
		my_urls = [
			# intermediate action page
			path('update_multiple_define', self.admin_site.admin_view(self.update_multiple_utterances_define)),
			# for POST
			path('update_multiple_execute', self.admin_site.admin_view(self.update_multiple_utterances_execute), name='update_multiple_execute'),
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
	
	# Views (wrappers) for bulk updating
	def update_multiple_utterances_define(self, request):
		return update_multiple_define(self, request)
	
	def update_multiple_utterances_execute(self, request):
		return update_multiple_execute(self, request)


### VIEWS FOR MULTIPLE MODELS ###

# admin user-facing
def update_multiple_define(model_admin_instance, request):
	request.current_app = model_admin_instance.admin_site.name
	req = request.GET
	id_list = req.get('ids', "").split(",")
	ids_string = ','.join(str(pk) for pk in id_list)
	to_update = model_admin_instance.MODEL_CLASS.objects.filter(pk__in=id_list) # QuerySet
	context = dict(
		# from doc: common variables for rendering the admin template
		model_admin_instance.admin_site.each_context(request),
		# specific to app
		model_name = model_admin_instance.MODEL_NAME,
		id_list = id_list,
		ids_string = ids_string,
		objects_to_update = to_update,
		form = CompleteUtteranceUpdateForm(),
	)
	return render(request, "admin/specify-bulk-update.html", context)

# POST only
def update_multiple_execute(model_admin_instance, request):
	admin_reverse = "admin:hilichurlian_database_" + model_admin_instance.MODEL_NAME.lower() + "_changelist"
	if request.method == 'POST':
		# initialize parameters
		model_class = model_admin_instance.MODEL_CLASS
		data = request.POST
		ids = data["ids"].split(",")
		field_values_to_update = {} # will have strings galore
		objects_to_update_set = model_class.objects.filter(pk__in=ids) # QuerySet
		objects_to_update_list = []

		# check for only the bulk updatable fields
		for field_name in model_class.BULK_UPDATABLE:
			if field_name + "-checked" in data and field_name in data:
				field_values_to_update[field_name] = data[field_name]
		if not field_values_to_update:
			messages.error(request, "No fields selected")
			return redirect(admin_reverse)

		# updating objects...
		for obj in objects_to_update_set:
			for field_name, field_value in field_values_to_update.items():
				setattr(obj, field_name, field_value)
			objects_to_update_list.append(obj)
		if len(objects_to_update_list) == 0:
			messages.error(request, "No objects selected")
			return redirect(admin_reverse)
		
		# chop list for reason in history if it's too long
		string_list_of_fields = str(list(field_values_to_update.keys()))
		if len(string_list_of_fields) > 75:
			string_list_of_fields = string_list_of_fields[:75]

		# update objects!
		bulk_update_with_history(
			objects_to_update_list,
			model_class,
			list( field_values_to_update.keys() ),
			default_change_reason = "Bulk update of " + string_list_of_fields,
		)
		
		# make somewhat human-readable confirmation message
		update_message = 'Updated ' + str(len(objects_to_update_list)) + ' ' + str(model_admin_instance.MODEL_NAME) + ' instances in bulk by unifying the following values: ' + str(field_values_to_update)
		messages.success(request, update_message)
	else:
		messages.error(request, "No data received")
	return redirect(admin_reverse)


### ADMIN SITE MODEL REGISTRATION ###

admin.site.register(Speaker, SimpleHistoryAdmin)
admin.site.register(Source, SimpleHistoryAdmin)
admin.site.register(Word, SimpleHistoryAdmin)
admin.site.register(CompleteUtterance, CompleteUtteranceAdmin)