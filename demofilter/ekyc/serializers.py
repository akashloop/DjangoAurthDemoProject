from dataclasses import field
from rest_framework import serializers
from .models import *

class DocumentChoiceSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='name')
    subtitle = serializers.CharField(source='number')
    class Meta: 
       model= Document
       fields=('id','title','subtitle',)

class DocumentSerializer(serializers.ModelSerializer):
    
    class Meta:
       model= Document
       fields='__all__'


class KYCKYBlistEntrySerializer(serializers.ModelSerializer):
    
    class Meta:
       model= KYCKYBEntry
       fields='__all__'


class KYCKYBEntrySerializer(serializers.ModelSerializer):
    
    class Meta:
       model= KYCKYBEntry
       fields='__all__'

    def create(self, validated_data):
        try:
            documents = self.context['request'].data['documents']
        except:
            documents = []
        # documents = self.context['request'].data['documents']
        contact = KYCKYBEntry.objects.create(**validated_data)
        contact.documents.set(documents)
        contact.save()
        return contact

    def update(self, instance, validated_data):
        try:
            documents = self.context['request'].data['documents']
        except:
            documents = []
        # documents = self.context['request'].data['documents']
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.user = validated_data.get('user', instance.user)
        instance.email_address = validated_data.get('email_address', instance.email_address)
        instance.dob = validated_data.get('dob', instance.dob)
        instance.doc_number = validated_data.get('doc_number', instance.doc_number)
        instance.doc_image = validated_data.get('doc_image', instance.doc_image)
        instance.company_name = validated_data.get('company_name', instance.company_name)
        instance.business_registreation_no = validated_data.get('business_registreation_no', instance.business_registreation_no)
        instance.doc_expiry_date = validated_data.get('doc_expiry_date', instance.doc_expiry_date)
        instance.verification_status = validated_data.get('verification_status', instance.verification_status)
        instance.documents.set(documents)
        instance.save()
        return instance