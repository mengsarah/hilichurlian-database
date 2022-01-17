# Generated by Django 4.0.1 on 2022-01-17 03:01

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import simple_history.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('hilichurlian_database', '0005_auto_20220110_0103'),
    ]

    operations = [
        migrations.CreateModel(
            name='Speaker',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Provide a living being when possible. Non-living entities such as Quest UI are acceptable as a last resort.', max_length=75)),
                ('type', models.CharField(choices=[('hili', 'Hilichurl'), ('abys', 'Abyss Order'), ('stud', 'Student')], max_length=4)),
            ],
        ),
        migrations.AddField(
            model_name='word',
            name='variants_grammatical',
            field=models.ManyToManyField(blank=True, help_text="Select words that are grammatical variants of this word. These words must not be the same words. For example, 'mi' and 'mimi' are grammatical variants of each other.", to='hilichurlian_database.Word'),
        ),
        migrations.AddField(
            model_name='word',
            name='variants_same_word',
            field=models.ManyToManyField(blank=True, help_text="Select words that are exactly the same as this word and are only elongated, shortened, or otherwise similarly altered. For example, 'yaaaa' is an elongated version of 'ya' and is otherwise the exact same word.", to='hilichurlian_database.Word'),
        ),
        migrations.AlterField(
            model_name='source',
            name='related_sources',
            field=models.ManyToManyField(blank=True, to='hilichurlian_database.Source'),
        ),
        migrations.CreateModel(
            name='HistoricalSpeaker',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('name', models.CharField(help_text='Provide a living being when possible. Non-living entities such as Quest UI are acceptable as a last resort.', max_length=75)),
                ('type', models.CharField(choices=[('hili', 'Hilichurl'), ('abys', 'Abyss Order'), ('stud', 'Student')], max_length=4)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical speaker',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]
