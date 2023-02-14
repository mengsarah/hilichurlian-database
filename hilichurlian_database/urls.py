from django.urls import path

from . import views

app_name = 'hilichurlian_database'
# be careful to not overlap with _project/urls.py
urlpatterns = [
	path('', views.index, name='index'),
	path('view', views.index, name='view'),
	path('about', views.about, name='about'),
	path('select', views.view_all_criteria, name='select'),
	path('filter', views.filter, name='filter'),
	path('utterance/<int:id>', views.view_utterance, name='utterance'),
	path('word/<slug:word>', views.view_word, name='word'),
	path('source/<int:id>', views.view_source, name='source'),
	path('speaker/<int:id>', views.view_speaker, name='speaker')
]

if views.SUBMISSIONS_OPEN:
	urlpatterns.append(path('submit', views.data_entry, name='data_entry'))
	# for POST
	urlpatterns.append(path('add_data/<slug:submit_type>', views.add_data, name='add_data'))