from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(User)
admin.site.register(UserRoll)
admin.site.register(UserPermissions)
admin.site.register(UserRolePermissions)

