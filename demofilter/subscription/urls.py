from django.urls import path, include
from .views import *
from rest_framework.routers import SimpleRouter


router = SimpleRouter()
router.register("subscriptions",SubscriptionPlanViewet, basename='subscription'),
router.register("user_subscriptions",UserSubscriptionViewet, basename='user_subscription'),
router.register("user_subscription_historys",UserSubscriptionHistoryViewet, basename='user_subscription_history'),



urlpatterns = [  
    path('', include(router.urls)),
    
]
app_name = 'subscription'