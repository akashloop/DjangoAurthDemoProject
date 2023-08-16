from django.shortcuts import render

# Create your views here.
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.mixins import ListModelMixin, CreateModelMixin, \
    UpdateModelMixin, DestroyModelMixin, RetrieveModelMixin
from .models import *
from rest_framework.decorators import action, api_view
from rest_framework import viewsets
from rest_framework import  status 
from .serializers import *
from datetime import timedelta
from django.utils import timezone
import platform
import socket
import uuid
import subprocess





class SubscriptionPlanViewet(viewsets.GenericViewSet, ListModelMixin):
    # permission_classes = [IsAuthenticated]
    queryset = SubscriptionPlan.objects.all().select_related(
        ).order_by('-modified')
    serializer_class = SubscriptionPlanSerializer
   
    
    def get_serializer_class(self):
        if self.action in ['list']:
            return SubscriptionPlanSerializer
        return SubscriptionPlanSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        return qs

    def create(self,request):
        params=request.data
        try: 
            serializer=self.get_serializer(data=params)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data,status=status.HTTP_201_CREATED)
        except Exception:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 

    def retrieve(self, request, pk, format=None):
        try: 
            obj = super().get_queryset().get(pk=pk)
            serializer = self.get_serializer(obj)
            return Response(serializer.data,status=status.HTTP_200_OK)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)
            
    def update(self,request,pk=None):
        obj=super().get_queryset().get(id=pk)
        serializer=self.get_serializer(obj,data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def destroy(self,request,pk=None):
        try:
            company=super().get_queryset().get(id=pk).delete() 
            return Response({"message":"Data  deleted successfully"})
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class UserSubscriptionViewet(viewsets.GenericViewSet, ListModelMixin):
    permission_classes = [IsAuthenticated]
    queryset = UserSubscription.objects.all().select_related(
        'subscription_plan',
        'user',
        ).order_by('-modified')
    serializer_class = UserSubscriptionSerializer
   
    
    def get_serializer_class(self):
        if self.action in ['list']:
            return UserSubscriptionSerializer
        return UserSubscriptionSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        return qs

    def create(self,request):
        params=request.data
        userdata = self.request.user
        user_subscription = UserSubscription.objects.filter(user=userdata,status=True).first()
        current_time = timezone.now()
        subscription_duration = timedelta(days=user_subscription.subscription_plan.duration)
        subscription_start_time = user_subscription.created
        subscription_expiration_time = subscription_start_time + subscription_duration
        if subscription_expiration_time >= current_time:
            return Response({"message":f" This {userdata} already have subscription plan...!"}, status=status.HTTP_400_BAD_REQUEST)   
        try: 
            serializer=self.get_serializer(data=params)
            if serializer.is_valid(raise_exception=True):
                serializer.save(user=userdata)
                return Response(serializer.data,status=status.HTTP_201_CREATED)
        except Exception:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)     

    def retrieve(self, request, pk, format=None):
        try: 
            obj = super().get_queryset().get(pk=pk)
            serializer = self.get_serializer(obj)
            return Response(serializer.data,status=status.HTTP_200_OK)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)


    @action(detail=False, methods=['post'])
    def upgrade_subscription(self, request):
        new_plan_id = request.data.get('new_plan_id')
        user = request.user
        user_subscription = UserSubscription.objects.filter(user=user, status=True).first()
        # Get the new subscription plan
        try:
            new_subscription_plan = SubscriptionPlan.objects.get(id=new_plan_id)
        except:
            return Response({"message": "Invalid subscription plan"}, status=status.HTTP_400_BAD_REQUEST)
        # Check if the user has an active subscription
        if not user_subscription:
            return Response({"message": "No active subscription found"}, status=status.HTTP_400_BAD_REQUEST)
        # Create a UserSubscriptionHistory entry before updating
        UserSubscriptionHistory.objects.create(
            user=user,
            subscription_plan=user_subscription.subscription_plan,
            devices_in_use=user_subscription.devices_in_use
        )
        # Calculate remaining time of the current subscription
        current_time = timezone.now()
        subscription_duration = timedelta(days=user_subscription.subscription_plan.duration)
        subscription_start_time = user_subscription.created
        subscription_expiration_time = subscription_start_time + subscription_duration
        remaining_time = subscription_expiration_time - current_time

        # Update the existing UserSubscription entry with the upgraded plan
        user_subscription.subscription_plan = new_subscription_plan
        user_subscription.save()
        serializer = self.get_serializer(user_subscription)
        return Response(serializer.data,status=status.HTTP_200_OK)


class UserSubscriptionHistoryViewet(viewsets.GenericViewSet, ListModelMixin):
    permission_classes = [IsAuthenticated]
    queryset = UserSubscriptionHistory.objects.all().select_related(
        ).order_by('-modified')
    serializer_class = UserSubscriptionHistorySerializer
   
    def get_serializer_class(self):
        if self.action in ['list']:
            return UserSubscriptionHistorySerializer
        return UserSubscriptionHistorySerializer

    def get_queryset(self):
        
        qs = super().get_queryset()
        return qs

    def retrieve(self, request, pk, format=None):
        try: 
            obj = super().get_queryset().get(pk=pk)
            serializer = self.get_serializer(obj)
            return Response(serializer.data,status=status.HTTP_200_OK)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def user_subscription(self,request):
        mac_address = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(0, 2 * 6, 2)])
        print("MAC Address:", mac_address)
        imei = subprocess.check_output("adb shell service call iphonesubinfo 1 | awk -F \"'\" '{print $2}'", shell=True)
        print("IMEI:", imei.strip().decode())
        user = request.user
        try: 
            qs = super().get_queryset()
            qs = qs.filter(user = user)
            serializer = self.get_serializer(qs,many=True)
            return Response(serializer.data,status=status.HTTP_200_OK)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)
            
    