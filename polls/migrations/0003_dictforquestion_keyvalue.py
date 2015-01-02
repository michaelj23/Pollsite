# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0002_question_total_votes'),
    ]

    operations = [
        migrations.CreateModel(
            name='DictforQuestion',
            fields=[
                ('question', models.OneToOneField(serialize=False, to='polls.Question', primary_key=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='KeyValue',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('key', models.IntegerField()),
                ('value', models.IntegerField()),
                ('dictionary', models.ForeignKey(to='polls.DictforQuestion')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
