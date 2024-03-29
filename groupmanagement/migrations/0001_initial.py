# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-04 19:50
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('reports', '__first__'),
        ('auth', '0008_alter_user_username_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupReports',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='auth.Group')),
                ('report_document', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='reports.report')),
            ],
        ),
    ]
