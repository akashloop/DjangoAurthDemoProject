from django.contrib import admin

# Register your models here.
from .models import *
admin.site.register(SubscriptionPlan)
admin.site.register(UserSubscription)
admin.site.register(UserSubscriptionHistory)
admin.site.register(Device)

