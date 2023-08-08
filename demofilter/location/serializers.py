from dataclasses import field
from rest_framework import serializers
from .models import *

class CountrySerializer(serializers.ModelSerializer):
    
    class Meta:
       model= Country
       fields='__all__'