# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from receipts.models import Receipt, Item, Profile
from django.contrib.auth.models import User

import django_filters.rest_framework
from rest_framework import viewsets
from receipts.serializers import ItemSerializer, ReceiptSerializer, ProfileSerializer

# Create your views here.

from django.http import HttpResponse
from django.http import JsonResponse
from django.core import serializers

from rest_framework import filters


from rest_framework import permissions
from rest_framework.generics import CreateAPIView
from django.contrib.auth import get_user_model # If used custom user model

from .serializers import UserSerializer


class CreateUserView(viewsets.ModelViewSet):

    model = get_user_model()
    permission_classes = [
        permissions.AllowAny # Or anon users can't register
    ]
    serializer_class = UserSerializer
    queryset = User.objects.all()


class ItemViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Item.objects.all()
    serializer_class = ItemSerializer


class ReceiptViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Receipt.objects.all()
    serializer_class = ReceiptSerializer

class ProfileViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """

    serializer_class = ProfileSerializer

    def get_queryset(self) :
        result = Profile.objects.filter(user=self.request.user)
        return result

def index(request):

    receipts = Receipt.objects.filter(profile__user=request.user).values()
    items = Item.objects.filter(receipt__profile__user=request.user).values('receipt__user', 'receipt__operator', 'receipt__total_sum', 'receipt__date_time', 'receipt__retail_place_address', 'receipt__kkt_reg_id', 'receipt__cash_total_sum', 'receipt__ecash_total_sum', 'quantity', 'sum', 'price', 'name', 'receipt')

    return JsonResponse({"profile": list(items)}, safe=False)
