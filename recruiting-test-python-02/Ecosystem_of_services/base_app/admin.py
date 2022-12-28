from django.contrib import admin

# Register your models here.
from .models import Investor
admin.register(Investor)(admin.ModelAdmin)