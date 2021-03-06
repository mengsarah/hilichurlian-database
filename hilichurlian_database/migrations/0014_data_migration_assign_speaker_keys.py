# Generated by Django 4.0.1 on 2022-01-23 23:14
# MANUALLY WRITTEN

from django.db import migrations

# database already has Speaker objects and speaker names in CompleteUtterance objects
def assign_speakers(apps, schema_editor):
	CompleteUtterance = apps.get_model('hilichurlian_database', 'CompleteUtterance')
	Speaker = apps.get_model('hilichurlian_database', 'Speaker')

	for utterance in CompleteUtterance.objects.all():
		utterance.speaker = Speaker.objects.get(name=utterance.speaker_name)
		utterance.save()

class Migration(migrations.Migration):

	dependencies = [
		('hilichurlian_database', '0013_completeutterance_speaker_and_more'),
	]

	operations = [
		migrations.RunPython(assign_speakers)
	]
