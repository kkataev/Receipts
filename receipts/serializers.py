from receipts.models import Receipt, Item, Profile
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model # If used custom user model

from rest_framework import serializers
import django_filters
from django.contrib.auth.models import Permission

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count

UserModel = get_user_model()


class UserSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True)

    def create(self, validated_data):


        user = UserModel.objects.create(
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        #permission = Permission.objects.get(name='Can add item')
        user.user_permissions.add(Permission.objects.get(name='Can add item'), 
            Permission.objects.get(name='Can delete item'),
            Permission.objects.get(name='Can change item'),
            Permission.objects.get(name='Can add profile'),
            Permission.objects.get(name='Can delete profile'),
            Permission.objects.get(name='Can change profile'),
            Permission.objects.get(name='Can add receipt'),
            Permission.objects.get(name='Can delete receipt'),
            Permission.objects.get(name='Can change receipt'))

        user.save()

        profile = Profile.objects.filter(user__username=validated_data['username'])
        if not profile: 
            p = Profile()
            setattr(p, 'user', user)
            p.save()

        return user

    class Meta:
        model = UserModel
        fields = ('__all__')


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ('quantity', 'sum', 'price', 'name')

class ReceiptSerializer(serializers.ModelSerializer):   
    items = serializers.SerializerMethodField('get_items_with')

    class Meta:
        model = Receipt
        fields = ('user', 'operator', 'total_sum', 'date_time', 'retail_place_address', 'kkt_reg_id', 'cash_total_sum', 'ecash_total_sum', 'items')

    def get_items_with(self, obj):
        if self.context.get('name'):
            name = self.context['name']
            items = Item.objects.filter(name__contains=name, receipt=obj)
            serializer = ItemSerializer(items, many=True)
            return serializer.data
        else:
            items = Item.objects.filter(receipt=obj)
            serializer = ItemSerializer(items, many=True)
            return serializer.data

class ProfileSerializer(serializers.ModelSerializer):  
    user = UserSerializer()
    #receipts = ReceiptSerializer(many=True)
    receipts = serializers.SerializerMethodField('get_receipts_with')
    rec_count = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ('user', 'receipts', 'rec_count')

    def get_rec_count(self, obj):
        return self.rec_count
    
    def get_receipts_with(self, obj):
    	serializer = None
    	name = None
    	receipts = None

        receipts = Receipt.objects.filter(profile=obj).order_by('date_time')

        if self.context['request'].GET.get('name'):
            name = self.context['request'].GET.get('name')
            receipts = receipts.filter(items__name__contains=name)

        if self.context['request'].GET.get('date_start') or self.context['request'].GET.get('date_end'):
            date_start = self.context['request'].GET.get('date_start')
            date_end = self.context['request'].GET.get('date_end')
            if date_start:
                receipts = receipts.filter(date_time__gte=date_start)
            if date_end:
                receipts = receipts.filter(date_time__lte=date_end)

        if self.context['request'].GET.get('user'):
            user = self.context['request'].GET.get('user')
            receipts = receipts.filter(user__contains=user)

        self.rec_count = receipts.count()

        if self.context['request'].GET.get('page_num'):
            paginator = Paginator(receipts, 10) # Show 25 contacts per page
            page_num = int(self.context['request'].GET.get('page_num'))
            try:
                receipts = paginator.page(page_num)
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                receipts = paginator.page(1)
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of results.
                receipts = paginator.page(paginator.num_pages)


        serializer = ReceiptSerializer(receipts, context={'name': name}, many=True)

        return serializer.data

