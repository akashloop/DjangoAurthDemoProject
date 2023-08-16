from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()
from django_extensions.db.models import TimeStampedModel

# Create your models here.
class SubscriptionPlan(TimeStampedModel):
    name = models.CharField(max_length=100 ,blank=True, null=True,)
    price = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True,)
    duration = models.PositiveIntegerField(help_text="Duration in days", blank=True, null=True,)
    max_devices = models.PositiveIntegerField(help_text="Maximum allowed devices", blank=True, null=True,)

    def __str__(self):
        return self.name

class UserSubscription(TimeStampedModel):
    user = models.OneToOneField(User,related_name='user_subscription', on_delete=models.CASCADE, blank=True, null=True,)
    subscription_plan = models.ForeignKey(SubscriptionPlan,related_name='user_subscription_plan', on_delete=models.SET_NULL, null=True, blank=True)
    devices_in_use = models.PositiveIntegerField(default=0)
    status = models.BooleanField(default=True, blank=True)

    def __str__(self):
        # return str(self.subscription_plan.name)
        return str(self.id)


class Device(TimeStampedModel):
    user_subscription = models.ForeignKey(UserSubscription, related_name='device_user_subscription', on_delete=models.CASCADE, blank=True, null=True,)
    device_id = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return str(self.device_id)


class UserSubscriptionHistory(TimeStampedModel):
    user = models.ForeignKey(User,related_name='user_subscription_history', on_delete=models.CASCADE, blank=True, null=True,)
    subscription_plan = models.ForeignKey(SubscriptionPlan,related_name='user_subscription_history_plan', on_delete=models.SET_NULL, null=True, blank=True)
    devices_in_use = models.PositiveIntegerField(default=0)
    

    def __str__(self):
        # return str(self.subscription_plan.name)
        return str(self.id)

