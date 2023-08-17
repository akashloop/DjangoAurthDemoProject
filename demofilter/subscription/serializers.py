from dataclasses import field
from rest_framework import serializers
from .models import *
from django.contrib.auth import get_user_model
User = get_user_model()



class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = '__all__'

class UserSubscriptionSerializer(serializers.ModelSerializer):
    subscription_plan = SubscriptionPlanSerializer(read_only=True)

    class Meta:
        model = UserSubscription
        fields = '__all__'

class UserSubscriptionCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserSubscription
        fields = '__all__'

class UserCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','email','phone','first_name','last_name')

class UserSubscriptionHistorySerializer(serializers.ModelSerializer):
    subscription_plan = SubscriptionPlanSerializer(read_only=True)
    users_card = UserCardSerializer(source='user', read_only=True)

    class Meta:
        model = UserSubscriptionHistory
        fields = '__all__'