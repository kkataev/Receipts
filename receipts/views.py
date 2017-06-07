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

from rest_framework.views import APIView
from rest_framework.response import Response

from django.contrib.auth import login, logout

from django.views.generic.base import TemplateView

from django.core.files.storage import FileSystemStorage
import json
from django.views.decorators.csrf import csrf_exempt
import codecs

@csrf_exempt 
def upload(request):
    if request.method == 'POST' and request.FILES.get('file',False) and request.user.is_authenticated():
        myfile = request.FILES['file']
        # Read file 
        myfile = myfile.decode("utf-8", errors='replace')

        json_string = myfile.read()
        print(json_string)
        # Convert json string to python object
        data = json.loads(json_string)
        print(Profile.objects.all())
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

            #receipts.append(receipt)

        # Create all in one query
        #Receipt.objects.bulk_create(receipts)
        return HttpResponse("Successful")
    return HttpResponse("Failed")



class OnePageAppView(TemplateView):
    template_name = 'static/views/auth.html'


class AuthView(APIView):
    #authentication_classes = (authentication.QuietBasicAuthentication,)
 
    def post(self, request, *args, **kwargs):
        login(request, request.user)
        return Response(UserSerializer(request.user).data)
 
    def delete(self, request, *args, **kwargs):
        logout(request)
        return Response({})


class CreateUserView(viewsets.ModelViewSet):

    model = get_user_model()
    permission_classes = [
        permissions.AllowAny # Or anon users can't register
    ]
    serializer_class = UserSerializer
    #queryset = User.objects.all()


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
