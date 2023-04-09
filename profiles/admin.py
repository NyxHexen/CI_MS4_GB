from django.contrib import admin
from .models import UserProfile

# Register your models here.

# class ProfilesAdmin(admin.ModelAdmin):



admin.site.register(UserProfile)
