from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (('CRM', {'fields': ('role', 'daily_target')}),)
    add_fieldsets = UserAdmin.add_fieldsets + (('CRM', {'fields': ('role', 'daily_target')}),)
    list_display = ('username', 'role', 'daily_target', 'is_active')