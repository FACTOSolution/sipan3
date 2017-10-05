# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-10-05 18:15
from __future__ import unicode_literals

from django.db import migrations, models
import site_functions.validators


class Migration(migrations.Migration):

    dependencies = [
        ('site_functions', '0033_auto_20171004_1735'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='certificado',
            field=models.FileField(default=False, null=True, upload_to='certificados/', validators=[site_functions.validators.validate_article_type]),
        ),
    ]