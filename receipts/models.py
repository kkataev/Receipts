# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from rest_framework import serializers

# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, blank=False, null = False)

    def __str__(self):
        return 'My profile: {}'.format(self.user.username)

class Receipt(models.Model):    
    user = models.TextField(max_length=500, blank=True, null = True)
    operator = models.TextField(max_length=500, blank=True, null = True)
    total_sum = models.IntegerField(blank=True, null = True)
    date_time = models.DateTimeField(auto_now=False, blank=True, null = True)
    retail_place_address = models.TextField(max_length=500, blank=True, null = True)
    kkt_reg_id = models.TextField(blank=True, null = True)
    cash_total_sum = models.IntegerField(blank=True, null = True)
    ecash_total_sum = models.IntegerField(blank=True, null = True)
    nds_no = models.IntegerField(blank=True, null = True)
    fiscal_document_number = models.IntegerField(blank=True, null = True)
    taxation_type = models.IntegerField(blank=True, null = True)
    user_inn = models.TextField(max_length=500, blank=True, null = True)
    raw_data = models.TextField(max_length=1000, blank=True, null = True)
    fiscal_sign = models.BigIntegerField(blank=True, null = True)
    operation_type = models.IntegerField(blank=True, null = True)
    receipt_code = models.IntegerField(blank=True, null = True)
    shift_number = models.IntegerField(blank=True, null = True)
    request_number = models.IntegerField(blank=True, null = True)
    fiscal_drive_number = models.TextField(max_length=500, blank=True, null = True)
    profile = models.ForeignKey(Profile, related_name='receipts', blank=True, null = True)

    def __str__(self):
        return 'My receipt: {}'.format(self.date_time)

class Item(models.Model):
    quantity = models.IntegerField(blank=True, null = True)
    sum = models.IntegerField(blank=True, null = True)
    price = models.IntegerField(blank=True, null = True)
    name = models.TextField(max_length=500, blank=False, null = True)
    ndsNo = models.IntegerField(blank=True, null = True)
    receipt = models.ForeignKey(Receipt, related_name='items', blank=True, null = True)

    def __str__(self):
        return '{}'.format(self.name)
