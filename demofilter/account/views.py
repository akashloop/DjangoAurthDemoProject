from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from .serializers import *
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
User = get_user_model()
from templated_email import send_templated_mail
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
import urllib.parse
from rest_framework.mixins import ListModelMixin, CreateModelMixin, \
    UpdateModelMixin, DestroyModelMixin, RetrieveModelMixin

from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet
from rest_framework import viewsets
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from demofilter.mixin import *
from demofilter.utils import *
from django.utils import timezone
from datetime import datetime, timedelta


class SignUpView(APIView):
    """
    url = /api/account/signup/
    {
        "email": "akash.sharma@loopmethod.com",
        "password": "test"
    }

    """
    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user_data_serializer = LoginResponceSerializer(user)
        return Response({'data':user_data_serializer.data,'message': "User Created Successfully.  Now perform Login to get your token",},status=status.HTTP_201_CREATED)

class PasswordChangeView(APIView):
    """
    url = /api/account/change-password/
    {
        "old_password": "test",
        "new_password": "test1",
        "confirm_new_password":"test1"
    }
    """
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        serializer = PasswordChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        old_password = serializer.validated_data.get('old_password')
        new_password = serializer.validated_data.get('new_password')

        if not user.check_password(old_password):
            return Response({"error": "Invalid old password."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return Response({"message": "Password changed successfully."}, status=status.HTTP_200_OK)


class ProfileUpdateView(APIView):
    """
    url = api/account/profile/update/
    {
    "first_name": "Test",
    "last_name": "Data",
    "profile": "/profile_photo/Screenshot_from_2023-05-31_16-33-40.png",
    "phone": "9876543728"
    }
    """

    permission_classes = [IsAuthenticated]
    def get_object(self, user):
        try:
            return User.objects.get(id=user)
        except User.DoesNotExist:
            return None

    def put(self, request, *args, **kwargs):
        user_profile = self.get_object(request.user.id)
        serializer = UserProfileUpdateSerializer(user_profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

class LogoutView(APIView):
    """
    url = api/account/logout/
    {
        "refresh_token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTY5MTA1ODAzNSwiaWF0IjoxNjkwOTcxNjM1LCJqdGkiOiI0MzNhN2QzZjVhYWU0MWMwYjVlNzQxOGFiMTYyYmE1NSIsInVzZXJfaWQiOjJ9.2PVhENWSGgJU_XQtcbPriv9lu_sS1cSv5kdyWJXNp6A"
    }
    """
    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            try:
                outstanding_token = OutstandingToken.objects.get(token=refresh_token)
            except OutstandingToken.DoesNotExist:
                return Response({"message": "Invalid refresh token."}, status=400)
            BlacklistedToken.objects.create(token=outstanding_token)
            return Response({"message": "Logout successful."})
        except Exception:
            return Response({"message": "An error occurred during logout."}, status=500)



class ResetPasswordLinkView(APIView):
    """
    url = api/account/resetpassword_link
    {
        "email":"loopakash7@gmail.com"
    }
    """
    def post(self, request):
        email = request.data.get("email")
        try:
            user = User.objects.get(email=email, is_active=True)
        except User.DoesNotExist:
            return Response({"error": "User not found or not active."}, status=status.HTTP_404_NOT_FOUND)

        current_site = get_current_site(request).name
        refresh = RefreshToken.for_user(user)
        token_url = urllib.parse.urljoin(current_site, 'reset-password/{}'.format(refresh))

        msg_html = "{}".format(token_url)
        send_mail(
            'User - Password Reset Request', 
            "", 
            settings.EMAIL_HOST_USER, 
            [email], 
            html_message=msg_html
        )
        return Response({"status": "Token Generated Successfully"}, status=status.HTTP_200_OK)


class ResetPasswordView(APIView):
    """
    url = api/account/password/reset/<str:token>/
    {
        "new_password":"test"
        "confirm_password":"test"
    }
    """
    def get(self, request, token):
        try:
            token = RefreshToken(token)
            user = User.objects.get(id=token['user_id'])
            return Response({"status": "Token Validated"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"non_field_errors": "Not a Valid URL!"}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, token):
        data = request.data
        try:
            token = RefreshToken(token)
            user = User.objects.get(id=token['user_id'])
            serializer = PasswordRetypeSerializer(data=data, context={"user": user})
            if serializer.is_valid():
                user.set_password(data.get('new_password'))
                user.save()
                token.blacklist()  # Invalidate the token instead of deleting it
                return Response({"status": True, "message": "Password reset successfully!"}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"non_field_errors": "Invalid Token!"}, status=status.HTTP_400_BAD_REQUEST)

class UserListView(OnlyMeMixin, viewsets.GenericViewSet, ListModelMixin, 
                UpdateModelMixin,RetrieveModelMixin):
    # permission_classes = [IsAuthenticated]
    queryset = User.objects.all().select_related(
            'user_roll',
            'organization',
        )
    serializer_class = LoginResponceSerializer
    filter_backends = [filters.SearchFilter,filters.OrderingFilter,DjangoFilterBackend]
    search_fields = ['id','first_name','last_name','email'] 
    filterset_fields = {'id':['exact'],'user_roll':['exact'],'is_active':['exact']}
    ordering_fields = ['id']
    PERMISSION_CODE = 'u_seen'

    def get_serializer_class(self):
        if self.action in ['list']:
            return LoginResponceSerializer
        return LoginResponceSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        return qs


from django.db.models import Prefetch
#---------------login API ---------------------------------
class UserLoginView(APIView):
    """
    url = api/account/user/login/
    {
        "email": "akash.sharma@loopmethod.com",
        "password": "test"
    },
    {
        "email": "loopakash7@gmail.com",
        "password": "test"
    }
    """
    serializer_class = TokenObtainPairSerializer
    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = TokenObtainPairSerializer(data=data)
        try:
            serializer.is_valid(raise_exception=True)
            token = serializer.validated_data
            user = User.objects.get(email=data["email"])
            # Use the UserSerializer to serialize the user data
            user_serializer = UserRSerializer(user)
            return Response({
                "tokens": token,
                "data": user_serializer.data,
                "message": "Login Successfully !!!!!"
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print(e)
            return Response({"status": 300, "message": "Invalid Login !!!!!!!!!!!!!"})


class UserRollViewset(viewsets.GenericViewSet,ListModelMixin):
    """
    url = /api/account/usersroles/
    {
    "name": "Manager"
    }
    """
    permission_classes = [IsAuthenticated]
    queryset = UserRoll.objects.all()
    serializer_class = UserRollSerializer 
    
    def get_queryset(self):
        organization = self.request.user.organization
        qs = super().get_queryset().filter(organization=organization)
        return qs

    def create(self,request):
        organization= request.user.organization
        params=request.data 
        serializer=self.get_serializer(data=params)
        if serializer.is_valid(raise_exception=True):
            serializer.save(organization=organization)
            prmissions = UserPermissions.objects.filter(permission_status=True)
            print(prmissions)
            if prmissions:
                userroll = UserRoll.objects.get(id=serializer.data['id']) 
                userroll.permission.set([i.id for i in prmissions])
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PermissionViewset(viewsets.GenericViewSet,ListModelMixin):
    """
    url = /api/account/permissions/
    """
    queryset = UserPermissions.objects.filter(permission_status=True).order_by('id')
    serializer_class = PermisionSerializer 

    def get_queryset(self):
        qs = super().get_queryset()
        return qs
from django.shortcuts import get_object_or_404
class UserRolePermissionsViewset(viewsets.GenericViewSet,ListModelMixin):
    """
    url = /api/account/rolepermissions?user_role=3
    user_role  =  user role id  given then get all userrole permissions like read, write, no_access, only_me
    pass in params
    """

    queryset = UserRolePermissions.objects.all()
    serializer_class = RolePermissionsSerializer 
    def get_queryset(self):
        qs = super().get_queryset()
        user_role = self.request.GET.get('user_role', None)
        if user_role:
            qs= qs.filter(user_role=user_role)
            return qs
        return qs
        
    def retrieve(self, request, pk, format=None):
        try: 
            obj = super().get_queryset().get(pk=pk)
            serializer = self.get_serializer(obj)
            return Response(serializer.data,status=status.HTTP_200_OK)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        # Step 1: Apply filtering
        queryset = super().get_queryset().exclude(user_role__can_edit=False)
        obj = get_object_or_404(queryset, id=pk)
        
        # Step 2: Update the object using serializer
        serializer = self.get_serializer(obj, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


######################################################## For Phone Functionality  ####################################################
class SignUpPhoneView(APIView):
    """
    url = /api/account/signup/
    {
        "phone": "9650036672",
    }

    """
    def post(self, request, *args, **kwargs):
        serializer = UserRegistrationPhoneSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user_data_serializer = UserRegistrationPhoneSerializer(user)
        return Response({'data':user_data_serializer.data,'message': "User Created Successfully.  Now perform Login to get your token",},status=status.HTTP_201_CREATED)  

class GenerateOTPView(APIView):
    """
    url = api/account/generate/otp/
    {
        "phone": "9650036673",
    }
    """
    def post(self, request, format=None):
        serializer = PhoneOtpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data['phone']
        try:
            user = User.objects.get(phone=phone)
            
            # Try to get an existing unexpired OTP or create a new one
            otp_obj, created = OTP.objects.get_or_create(
                user=user,
                phone=phone,
                created__gte=timezone.now() - settings.OTP_EXPIRATION_TIME,
                defaults={'otp_code': generate_otp()}
            )
            if not created:
                # If an unexpired OTP already existed, return an appropriate response
                return Response({'detail': f"An unexpired OTP already exists for this {user}: {phone}."}, status=status.HTTP_400_BAD_REQUEST)
            
            # Implement OTP sending logic here (via SMS, email, etc.)
            # For demonstration purposes, we'll print the OTP
            print(f"Generated OTP for {phone}: {otp_obj.otp_code}")
            return Response({'detail': 'OTP sent successfully.'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)




class LoginOtpView(APIView):
    """
    url = /api/account/user/login/otp/
    {
        "phone": "9650036673",
        "otp": "8972"
    }
    """  
    def post(self, request, format=None):
        serializer = LoginPhoneSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data['phone']
        otp = serializer.validated_data['otp']
        
        try:
            user = User.objects.get(phone=phone)
            otp_obj = OTP.objects.filter(user=user, phone=phone).order_by('-created').first()

            if otp_obj and otp_obj.otp_code == otp:
                current_time = timezone.now()
                if otp_obj.created + settings.OTP_EXPIRATION_TIME >= current_time:
                    refresh = RefreshToken.for_user(user)
                    user_serializer = UserRSerializer(user)
                    return Response({
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                        "data": user_serializer.data,
                        "message": "Login Successfully !!!!!"
                    }, status=status.HTTP_200_OK)
                else:
                    otp_obj.delete()
                    return Response({'detail': 'OTP has expired.'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'detail': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
