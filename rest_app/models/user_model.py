from django.db import models
from django.utils import timezone
from .model import SupabaseModelMixin


# class CustomUserManager(BaseUserManager):
#     def create_user(self, email, password=None, **extra_fields):
#         if not email:
#             raise ValueError('The Email field must be set')
#         email = self.normalize_email(email)
#         user = self.model(email=email, **extra_fields)
#         user.set_password(password)
#         user.save(using=self._db)
#         return user

#     def create_superuser(self, email, password=None, **extra_fields):
#         extra_fields.setdefault('is_staff', True)
#         extra_fields.setdefault('is_superuser', True)
#         extra_fields.setdefault('is_active', True)

#         if extra_fields.get('is_staff') is not True:
#             raise ValueError('Superuser must have is_staff=True.')
#         if extra_fields.get('is_superuser') is not True:
#             raise ValueError('Superuser must have is_superuser=True.')
#         return self.create_user(email, password, **extra_fields)


# class CustomUser(AbstractBaseUser, PermissionsMixin, SupabaseModelMixin):
class Account(models.Model, SupabaseModelMixin):
    # Set the Supabase table name
    table_name = 'accounts'

    # def get_username(self):
    #     return self.email
        
    # # Change these from methods to properties
    # @property
    # def is_anonymous(self):
    #     return False
        
    # @property
    # def is_authenticated(self):
    #     return True

    # Attributes to access django's database
    email = models.EmailField(unique=True)
    # is_staff = models.BooleanField(default=False)
    # is_active = models.BooleanField(default=True)
    # date_joined = models.DateTimeField(default=timezone.now)
    # supabase_uid = models.CharField(max_length=255, null=True, blank=True)
    supabase_access_token = models.TextField(null=True, blank=True)
    supabase_refresh_token = models.TextField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email 