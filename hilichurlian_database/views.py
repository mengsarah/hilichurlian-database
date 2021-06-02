from django.shortcuts import render, redirect
from django.contrib import messages
from django.forms import modelform_factory
from .models import CompleteUtterance

### FORM CLASSES ###
# CompleteUtterance: don't show the words field
CompleteUtteranceForm = modelform_factory(CompleteUtterance, fields=['utterance', 'speaker', 'translation', 'translation_source', 'context', 'source'])

### VIEWS FOR POST ###
def add_data(request):
	if request.method == 'POST':
		data = request.POST
	else:
		messages.error(request, "No data received")
	return redirect("hilichurlian_database:data_entry")

### VIEWS FOR USERS ###

def index(request):
	return render(request, "hilichurlian_database/index.html")

# the /submit page
def data_entry(request):
	# blank form
	submit_form = CompleteUtteranceForm()
	return render(request, "hilichurlian_database/submit.html", {'form': submit_form})