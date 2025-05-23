# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-06-03 14:25
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField()),
                ('sum', models.IntegerField()),
                ('price', models.IntegerField()),
                ('name', models.TextField(max_length=500)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Receipt',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.TextField(blank=True, max_length=500)),
                ('operator', models.TextField(blank=True, max_length=500)),
                ('total_sum', models.IntegerField()),
                ('date_time', models.DateTimeField()),
                ('retail_place_address', models.TextField(blank=True, max_length=500)),
                ('kkt_reg_id', models.IntegerField()),
                ('cash_total_sum', models.IntegerField()),
                ('ecash_total_sum', models.IntegerField()),
                ('items', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='receipts.Item')),
            ],
        ),
        migrations.AddField(
            model_name='profile',
            name='receipts',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='receipts.Receipt'),
        ),
        migrations.AddField(
            model_name='profile',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
