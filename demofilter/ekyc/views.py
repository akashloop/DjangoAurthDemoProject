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
from .tasks import ocr_process
from .admin import *
from django.http import HttpResponse
from openpyxl import Workbook

class DocumentViewet(viewsets.GenericViewSet, ListModelMixin):
    # permission_classes = [IsAuthenticated]
    queryset = Document.objects.all().select_related(
            'country', 
        ).order_by('-modified')
    serializer_class = DocumentSerializer
   
    
    def get_serializer_class(self):
        if self.action in ['list']:
            return DocumentSerializer
        elif self.action in ['choices']:
            return DocumentChoiceSerializer
        return DocumentSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        country= self.request.GET.get('country', None)
        if country:
            qs = qs.filter(country=country) 
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
    
          
    @action(detail=False, methods=['get'])
    def choices(self, request,**kwargs):
        obj = self.get_queryset()
        serializer=self.get_serializer(obj, many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)



class KYCKYBViewet(viewsets.GenericViewSet, ListModelMixin):
    # permission_classes = [IsAuthenticated]
    queryset = KYCKYBEntry.objects.all().select_related(
            'user', 
        ).prefetch_related(
            'documents',
        ).order_by('-modified')
    serializer_class = KYCKYBEntrySerializer
   
    def get_serializer_class(self):
        if self.action in ['list']:
            return KYCKYBlistEntrySerializer
        return KYCKYBEntrySerializer

    def get_queryset(self):
        qs = super().get_queryset()
        return qs

    def create(self,request):
        params = request.data
        try:
            serializer = self.get_serializer(data=params)
            if serializer.is_valid(raise_exception=True):
                instance = serializer.save()
                id = instance.id
                if id:
                    task_result = ocr_process.delay(id)
                    return Response({'serializer_data': serializer.data}, status=status.HTTP_201_CREATED)
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

    @action(detail=False, methods=['get'])
    def export_data(self, request):
        print(request)
        file_format = request.query_params.get('file_format')  # Default to CSV if no format specified
        print("file_format", file_format)

        if file_format not in ['csv', 'xls', 'xlsx', 'json', 'tsv']:
            return Response({'error': 'Invalid format'}, status=status.HTTP_400_BAD_REQUEST)

        resource = KYCKYBEntryResource()
        dataset = resource.export()

        response = HttpResponse(content_type=f'text/{file_format}')
        response['Content-Disposition'] = f'attachment; filename="kyckyb-sheet.{file_format}"'

        if file_format == 'csv':
            response.write(dataset.csv)
        elif file_format == 'xls':
            response.write(dataset.xls)
        elif file_format == 'xlsx':
            response.write(dataset.xlsx)
        elif file_format == 'json':
            response.write(dataset.json)
        elif file_format == 'tsv':
            response.write(dataset.tsv)
        return response

   

    