# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from receipts.models import Receipt, Item, Profile
# Create your views here.

from django.http import HttpResponse
from django.http import JsonResponse


def index(request):

    receipts = Receipt.objects.filter(profile__user=request.user).values()
    items = Item.objects.filter(receipt__profile__user=request.user).values('receipt__user', 'receipt__operator', 'receipt__total_sum', 'receipt__date_time', 'receipt__retail_place_address', 'receipt__kkt_reg_id', 'receipt__cash_total_sum', 'receipt__ecash_total_sum', 'quantity', 'sum', 'price', 'name', 'receipt')

    return JsonResponse({"profile": list(items)}, safe=False)
