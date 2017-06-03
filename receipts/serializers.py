from receipts.models import Receipt, Item, Profile
from django.contrib.auth.models import User

from rest_framework import serializers
import django_filters

class UserSerializer(serializers.ModelSerializer):  
    class Meta:
        model = User
        fields = ('__all__')

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ('quantity', 'sum', 'price', 'name')


class ReceiptSerializer(serializers.ModelSerializer):   
    items = ItemSerializer(many=True)
    class Meta:
        model = Receipt
        fields = ('user', 'operator', 'total_sum', 'date_time', 'retail_place_address', 'kkt_reg_id', 'cash_total_sum', 'ecash_total_sum', 'items')


class ProfileSerializer(serializers.ModelSerializer):  
    user = UserSerializer()
    receipts = ReceiptSerializer(many=True)
    class Meta:
        model = Profile
        fields = ('user', 'receipts')