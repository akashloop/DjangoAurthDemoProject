from django.shortcuts import render

# Create your views here.
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


class CountryViewet(viewsets.GenericViewSet, ListModelMixin):
    # permission_classes = [IsAuthenticated]
    queryset = Country.objects.all().select_related().order_by('-modified')
    serializer_class = CountrySerializer
   
    
    def get_serializer_class(self):
        if self.action in ['list']:
            return CountrySerializer
        return CountrySerializer

    def get_queryset(self):
        qs = super().get_queryset()
        return qs