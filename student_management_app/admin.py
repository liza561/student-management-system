from django.contrib import admin

# Register your models here.
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser  , Students

class UserModel(UserAdmin):
    pass
admin.site.register(CustomUser, UserModel)
admin.site.register(Students)