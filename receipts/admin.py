# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import Profile
from .models import Receipt
from .models import Item
from .models import Exclude


# Register your models here.
admin.site.register(Profile)
admin.site.register(Receipt)
admin.site.register(Item)
admin.site.register(Exclude)
