from django.contrib import admin
from .models import User
# Register your models here.

class UserAdmin(admin.ModelAdmin):
    list_display = ['nickname', 'email', 'date_joined', 'is_active']

admin.site.register(User,UserAdmin)
