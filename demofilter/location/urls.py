from django.urls import path, include
from .views import *
from rest_framework.routers import SimpleRouter


router = SimpleRouter()
router.register("countres",CountryViewet, basename='country'),




urlpatterns = [  
    path('', include(router.urls)),
    
]
app_name = 'location'