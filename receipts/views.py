# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from receipts.models import Receipt, Item, Profile, Exclude
from django.contrib.auth.models import User

import django_filters.rest_framework
from rest_framework import viewsets
from receipts.serializers import ItemSerializer, ReceiptSerializer, ProfileSerializer, ExcludeSerializer

# Create your views here.

from django.http import HttpResponse
from django.http import JsonResponse
from django.core import serializers

from rest_framework import filters


from rest_framework import permissions
from rest_framework.generics import CreateAPIView
from django.contrib.auth import get_user_model # If used custom user model

from .serializers import UserSerializer

from rest_framework.views import APIView
from rest_framework.response import Response

from django.contrib.auth import login, logout

from django.views.generic.base import TemplateView

from django.core.files.storage import FileSystemStorage
import json
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

import codecs
from chardet.universaldetector import UniversalDetector

import sys  

from pprint import pprint

reload(sys)  
sys.setdefaultencoding('utf8')


@csrf_exempt 
def upload(request):
    if request.method == 'POST' and request.FILES.get('file',False) and request.user.is_authenticated():
        myfile = request.FILES['file']
        
        json_string = myfile.read()

        # Convert json string to python object
        data = json.loads(json_string)
        profile = Profile.objects.get(user__username=request.user.username)

        # Create model instances for each item
        receipts = []
        for document in data:
            # create model instances...
            items = []
            r = Receipt()
            setattr(r, 'user', document.get('document').get('receipt').get('user'))
            setattr(r, 'operator', document.get('document').get('receipt').get('operator'))
            setattr(r, 'total_sum', document.get('document').get('receipt').get('totalSum'))
            setattr(r, 'date_time', document.get('document').get('receipt').get('dateTime'))
            setattr(r, 'retail_place_address', document.get('document').get('receipt').get('useretailPlaceAddressr'))
            setattr(r, 'kkt_reg_id', document.get('document').get('receipt').get('kktRegId'))
            setattr(r, 'cash_total_sum', document.get('document').get('receipt').get('cashTotalSum'))
            setattr(r, 'ecash_total_sum', document.get('document').get('receipt').get('ecashTotalSum'))
            setattr(r, 'nds_no', document.get('document').get('receipt').get('ndsNo'))
            setattr(r, 'fiscal_document_number', document.get('document').get('receipt').get('fiscalDocumentNumber'))
            setattr(r, 'taxation_type', document.get('document').get('receipt').get('taxationType'))
            setattr(r, 'user_inn', document.get('document').get('receipt').get('userInn'))
            setattr(r, 'raw_data', document.get('document').get('receipt').get('rawData'))
            setattr(r, 'fiscal_sign', document.get('document').get('receipt').get('fiscalSign'))
            setattr(r, 'operation_type', document.get('document').get('receipt').get('operationType'))
            setattr(r, 'receipt_code', document.get('document').get('receipt').get('receiptCode'))
            setattr(r, 'shift_number', document.get('document').get('receipt').get('shiftNumber'))
            setattr(r, 'request_number', document.get('document').get('receipt').get('requestNumber'))
            setattr(r, 'fiscal_drive_number', document.get('document').get('receipt').get('fiscalDriveNumber'))
            setattr(r, 'profile', profile)
            r.save()

            for item in document['document']['receipt'].get('items'):
            	i = Item()

                setattr(i, 'quantity', item.get('quantity'))
                setattr(i, 'sum', item.get('sum'))
                setattr(i, 'price', item.get('price'))
                setattr(i, 'name', item.get('name'))
                setattr(i, 'ndsNo', item.get('ndsNo'))
                setattr(i, 'receipt', r)
                i.save()

        return HttpResponse("Successful")
    return HttpResponse("Failed")



class OnePageAppView(TemplateView):
    template_name = 'static/views/auth.html'

@method_decorator(csrf_exempt, name='dispatch')
class AuthView(APIView):
    #authentication_classes = (authentication.QuietBasicAuthentication,)
    def post(self, request, *args, **kwargs):
        login(request, request.user)
        return Response(UserSerializer(request.user).data)
 
    def delete(self, request, *args, **kwargs):
        logout(request)
        return Response({})

    def perform_authentication(self, request):
        pass

@method_decorator(csrf_exempt, name='dispatch')
class CreateUserView(viewsets.ModelViewSet):

    model = get_user_model()
    permission_classes = [
        permissions.AllowAny # Or anon users can't register
    ]
    serializer_class = UserSerializer
    #queryset = User.objects.all()

@method_decorator(csrf_exempt, name='dispatch')
class ItemViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

    def post(self, request, pk, format=None):
        item = Item.objects.get(id=request.data.get('id'))
        print getattr(item, 'exclude')
        if getattr(item, 'exclude') == False:
            exclude = True
        else:
            exclude = False
        setattr(item, 'exclude', exclude)
        item.save()
        return HttpResponse("Successful")

@method_decorator(csrf_exempt, name='dispatch')
class ReceiptViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Receipt.objects.all()
    serializer_class = ReceiptSerializer

@method_decorator(csrf_exempt, name='dispatch')
class ExcludeViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    serializer_class = ExcludeSerializer

    def get_queryset(self) :
        result = Exclude.objects.filter(user=self.request.user.id)
        return result

@method_decorator(csrf_exempt, name='dispatch')
class ProfileViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """

    serializer_class = ProfileSerializer

    def get_queryset(self) :
        result = Profile.objects.filter(user__username=self.request.user)
        return result

@csrf_exempt
def index(request):

    receipts = Receipt.objects.filter(profile__user=request.user).values()
    items = Item.objects.filter(receipt__profile__user=request.user).values('receipt__user', 'receipt__operator', 'receipt__total_sum', 'receipt__date_time', 'receipt__retail_place_address', 'receipt__kkt_reg_id', 'receipt__cash_total_sum', 'receipt__ecash_total_sum', 'quantity', 'sum', 'price', 'name', 'receipt')

    return JsonResponse({"profile": list(items)}, safe=False)
