from rest_framework import serializers

from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
User = get_user_model()
from djoser.conf import settings as djoser_settings
from django.contrib.auth.password_validation import validate_password
from djoser.conf import settings
# from djoser.conf import settings as djoser_settings
# from .models import User
from account.models import *
from demofilter.utils import *

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    # def create(self, validated_data):
    #     user = User.objects.create_user(**validated_data)
    #     return user
    def create(self, validated_data):
        # TODO: Owner role
        org = Organization.objects.create(brand_name = "" )
        default_role = UserRoll.objects.create(name='Owner', organization=org, can_edit=False)
        role= UserRoll.objects.create(name = "Admin", organization=org)
        # prmissions = LSPPermissions.objects.all()
        prmissions=UserPermissions.objects.filter(permission_status=True)
        print(prmissions)
        if prmissions:
            role.permission.set([i.id for i in prmissions])
            role.save()
            default_role.permission.set([i.id for i in prmissions])
            default_role.save()
        user = User.objects.create_user(validated_data['email'],password = validated_data['password'], organization=org, user_roll=default_role)
        org.owner = user
        org.save()
        return user

class LoginResponceSerializer(serializers.ModelSerializer):
    user_roll_name = serializers.SerializerMethodField(read_only=True)
    def get_user_roll_name(self, obj):
        if obj.user_roll:
            return str(obj.user_roll)
        return str("")

    class Meta:
        model = User
        fields = ('id','profile','email','full_name','phone','user_roll','user_roll_name')


class PasswordChangeSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_new_password = serializers.CharField(required=True)

    def validate(self, data):
        new_password = data.get('new_password')
        confirm_new_password = data.get('confirm_new_password')

        if new_password != confirm_new_password:
            raise serializers.ValidationError("New passwords must match.")
        return data
    class Meta:
        model = User
        fields = ('id','old_password', 'new_password', 'confirm_new_password')

class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name','last_name','profile','phone')


class PasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(style={"input_type": "password"})

    def validate(self, attrs):
        user =  self.context['user'] # or self.context["request"].user
        # why assert? There are ValidationError / fail everywhere
        assert user is not None

        try:
            validate_password(attrs["new_password"], user)
        except ValidationError as e:
            raise serializers.ValidationError(
                {"new_password": list(e.messages)})
        return super().validate(attrs)


class PasswordRetypeSerializer(PasswordSerializer):
    confirm_password = serializers.CharField(style={"input_type": "password"})

    default_error_messages = {
        "password_mismatch":
            djoser_settings.CONSTANTS.messages.PASSWORD_MISMATCH_ERROR
    }

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if attrs["new_password"] == attrs["confirm_password"]:
            return attrs
        else:
            self.fail("password_mismatch")


######################################### permission(03/08/2023) ##################################

class PermisionSerializer(serializers.ModelSerializer):
    class Meta:
       model= UserPermissions
       fields = '__all__'  

class RolePermissionsSerializer(serializers.ModelSerializer):
    class Meta:
       model= UserRolePermissions
       fields = '__all__'  

class PermSerializer(serializers.ModelSerializer):
    permissions_code = serializers.CharField(source='user_permissions.permissions_code')
    class Meta:
        model= UserRolePermissions
        fields=('id', 'permissions_code', 'permission_level')

class UserRollSerializer(serializers.ModelSerializer):
    class Meta:
       model= UserRoll
       fields=('id','name','permission','organization', 'can_edit')       
     
class UserRSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'email','phone', 'first_name', 'profile', 'organization', 'user_roll',
            'user_image', 'org_id', 'organization_name', 'user_roll_name', 'user_roll_id', 'user_permissions',
        )
    user_image = serializers.SerializerMethodField()
    org_id = serializers.SerializerMethodField()
    organization_name = serializers.SerializerMethodField()
    user_roll_name = serializers.SerializerMethodField()
    user_roll_id = serializers.SerializerMethodField()
    user_permissions = serializers.SerializerMethodField()

    def get_user_image(self, user):
        return user.profile.url if user.profile else None

    def get_org_id(self, user):
        try:
            return int(user.organization.id)
        except:
            return None
    def get_organization_name(self, user):
        return user.organization.brand_name if user.organization else None

    def get_user_roll_name(self, user):
        return user.user_roll.name if user.user_roll else None

    def get_user_roll_id(self, user):
        return user.user_roll.id if user.user_roll else None

    def get_user_permissions(self, user):
        if user.organization and user.user_roll:
            queryset = UserRolePermissions.objects.filter(
                user_role=user.user_roll,
                user_permissions__permission_status=True
            ).select_related('user_permissions')
            return PermSerializer(queryset, many=True).data
        return None


################################################ for phone ####################################################

class UserRegistrationPhoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'phone')
        
    def create(self, validated_data):
        print(validated_data)
        org = Organization.objects.create(brand_name = "" )
        default_role = UserRoll.objects.create(name='Owner', organization=org, can_edit=False)
        role= UserRoll.objects.create(name = "Admin", organization=org)
        prmissions=UserPermissions.objects.filter(permission_status=True)
        print(prmissions)
        if prmissions:
            role.permission.set([i.id for i in prmissions])
            role.save()
            default_role.permission.set([i.id for i in prmissions])
            default_role.save()
        phone_number = validated_data['phone']
        user = User(phone=phone_number,organization=org, user_roll=default_role )
        user.set_password("Admin@1234")
        user.save()
        org.owner = user
        org.save()
        otp_code = generate_otp()
        OTP.objects.create(user_id=user.id, phone=phone_number, otp_code=otp_code)

        return user

class LoginPhoneSerializer(serializers.Serializer):
    phone = serializers.CharField()
    otp = serializers.CharField()

class PhoneOtpSerializer(serializers.Serializer):
    phone = serializers.CharField()
    