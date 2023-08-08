import email
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from datetime import datetime
from django.utils import timezone
from django.db.models import Q, Value,Max,F
from django_extensions.db.models import TimeStampedModel
from django.contrib.auth.models import Permission
from model_utils.fields import StatusField



class UserManager(BaseUserManager):
    """
        Manager for :model:`account.User` extending from Base User Manager
    """
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given email and password.

        Overrides the function from BaseUserManager
        """
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a user with the given email and password.

        Overrides the function from BaseUserManager
        """
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_active', True)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a super user with the given email and password.

        Overrides the function from BaseUserManager
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class AbstractEmailUser(AbstractUser):
    """
        User Fields:
            * id
            * email
            * first_name
            * phone
            * is_active,
            * is_staff
            * last_login
        Custom User Model extending Django's AbstractUser model
        which updates the following -
            * Makes Email the default Username
            * Discards username

    """
    email = models.EmailField('email address', unique=True)
    
    username = None
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    __original_email = None

    def __init__(self, *args, **kwargs):
        super(AbstractEmailUser, self).__init__(*args, **kwargs)
        self.__original_email = self.email

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
        abstract = True

    def full_name(self):
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name.strip()


class User(AbstractEmailUser,TimeStampedModel):
    phone = models.CharField("Phone", max_length=15, null=True, blank=True)
    profile= models.FileField("Profile Pick", upload_to="profile_photo",null=True, blank=True)
    is_deleted = models.BooleanField(default=False, verbose_name="Is Deleted")
    organization = models.ForeignKey("Organization",related_name="user_organization", on_delete=models.SET_NULL, null=True, blank=True)
    user_roll = models.ForeignKey("UserRoll",related_name="user_roll", on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return str(self.get_full_name()) or str(self.email)
        
    @property
    def full_name(self):
        return str(self.get_full_name()) or str(self.email) 
    

class Organization(TimeStampedModel):
    """ Model for Creating organization """
    owner = models.OneToOneField(User, related_name="user_organization", on_delete=models.SET_NULL, null=True, blank=True)
    url =  models.URLField(max_length=250,null=True, blank=True )
    logo= models.ImageField(upload_to="organization_logo",null=True, blank=True)
    brand_name = models.CharField("Brand Name", max_length=100, null=True, blank=True)
    legal_name = models.CharField("Legal Name", max_length=100, null=True, blank=True)
    location = models.CharField("Location", max_length=200, null=True, blank=True)
    phone = models.CharField("Phone No", max_length=20, null=True, blank=True)
    email = models.EmailField("Email", max_length=200, null=True, blank=True)
    tax_id = models.CharField("Tax Id", max_length=70,null=True, blank=True)
    business_id  = models.CharField("Business ID", max_length=70,null=True, blank=True)
    description = models.TextField("Description", null=True, blank=True)
    country =  models.CharField("Country", max_length=100, null=True, blank=True)
    state =  models.CharField("state", max_length=100, null=True, blank=True)
    profile_compleate = models.BooleanField(default=False, verbose_name="Profile Compleate")
    
    
    class Meta:
        verbose_name = "Organization"
        verbose_name_plural = "Organizations"

    def __str__(self):
        return str(self.brand_name) or str(self.id)

class UserRoll(TimeStampedModel):
    name = models.CharField("Name", max_length=200)
    organization = models.ForeignKey(Organization,related_name="userroll_organization", on_delete=models.SET_NULL, null=True, blank=True)
    permission = models.ManyToManyField("UserPermissions",verbose_name="Permission", related_name="userroll_permission", blank=True, through="UserRolePermissions")
    can_edit = models.BooleanField(default=True, blank=True)
    
    def __str__(self):
        return str(self.name)


class UserPermissions(TimeStampedModel):
    permissions_name = models.CharField(max_length=100,null=True, blank=True)
    permissions_code = models.CharField(max_length=100,null=True, blank=True)
    permission_status = models.BooleanField(verbose_name="Permission Status",default=True, null=True)


    def __str__(self):
        return self.permissions_name
    
# through model for LSPRoles m2m LSPPermissions
class UserRolePermissions(TimeStampedModel):
    PERMISSION_LEVEL = (
        ('read', 'Read'),
        ('write', 'Write'),
        ('no_access', 'No Access'),
        ('only_me', 'Only Me'),
    )
    user_role = models.ForeignKey("UserRoll",related_name="user_permissions_role", on_delete=models.SET_NULL, null=True, blank=True)
    user_permissions = models.ForeignKey(UserPermissions,related_name="user_permissions_permisions",on_delete=models.CASCADE,blank=True,null=True)
    permission_level = StatusField(max_length=100, choices_name='PERMISSION_LEVEL', default='write', blank=True)
    
    def __str__(self):
        return str(self.permission_level)


class Currency(TimeStampedModel):
    currency = models.CharField(max_length=50,unique=True,db_index=True)
    iso_code = models.CharField(max_length=3,unique=True,db_index=True)
    symbol = models.CharField(max_length=10,unique=True)

    class Meta:
        verbose_name = "Currency"
        verbose_name_plural = "Currencies"
        db_table = "Currency"

    def __str__(self):
        return self.currency

