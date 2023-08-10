from django.urls import path, include
from .views import *
from rest_framework.routers import SimpleRouter


router = SimpleRouter()
router.register("users",UserListView, basename='user'),
router.register("usersroles",UserRollViewset, basename='userrole'),
router.register("permissions",PermissionViewset, basename='permission')
router.register("rolepermissions",UserRolePermissionsViewset, basename='rolepermission'),

urlpatterns = [
    path('', include(router.urls)),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('signup/phone/', SignUpPhoneView.as_view(), name='phone_signup'),
    path('user/login/', UserLoginView.as_view(),name="Login"),
    path('user/login/otp/', LoginOtpView.as_view(),name="Login"),
    path('generate/otp/', GenerateOTPView.as_view(),name="Login"),
    path('change-password/', PasswordChangeView.as_view(), name='password-change'),
    path('profile/update/', ProfileUpdateView.as_view(), name='profile-update'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('resetpassword_link/', ResetPasswordLinkView.as_view(), name='resetpassword_link'),
    path('password/reset/<str:token>/', ResetPasswordView.as_view(), name='reset_password'),
    
]
app_name = 'account'