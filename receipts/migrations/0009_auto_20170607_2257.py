# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-06-07 22:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('receipts', '0008_auto_20170606_2215'),
    ]

    operations = [
        migrations.AlterField(
            model_name='receipt',
            name='fiscal_sign',
            field=models.BigIntegerField(blank=True, null=True),
        ),
    ]
