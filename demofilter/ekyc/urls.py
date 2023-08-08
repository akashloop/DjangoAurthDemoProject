from django.urls import path, include
from .views import *
from rest_framework.routers import SimpleRouter


router = SimpleRouter()
router.register("documents",DocumentViewet, basename='document'),
router.register("ekycs",KYCKYBViewet, basename='ekyc'),



urlpatterns = [  
    path('', include(router.urls)),
    
]
app_name = 'ekyc'