from django.contrib import admin

# Register your models here.
from .models import *
from django.contrib.auth.admin import UserAdmin

admin.site.register(User)
admin.site.register(UserRoll)
admin.site.register(UserPermissions)
admin.site.register(UserRolePermissions)
admin.site.register(Currency)
admin.site.register(OTP)
# class AccountAdmin(UserAdmin):
#     list_display = ("first_name","email", 'phone')

# admin.site.register(User, AccountAdmin)

