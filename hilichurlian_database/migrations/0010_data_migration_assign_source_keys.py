# Generated by Django 4.0.1 on 2022-01-22 05:03
# MANUALLY WRITTEN

from django.db import migrations

# database already has Source objects and source URLs in CompleteUtterance objects
def assign_sources(apps, schema_editor):
	CompleteUtterance = apps.get_model('hilichurlian_database', 'CompleteUtterance')
	Source = apps.get_model('hilichurlian_database', 'Source')

	for utterance in CompleteUtterance.objects.all():
		utterance.source = Source.objects.get(url=utterance.source_url)
		utterance.save()

class Migration(migrations.Migration):

	dependencies = [
		('hilichurlian_database', '0009_completeutterance_source_and_more'),
	]

	operations = [
		migrations.RunPython(assign_sources)
	]