from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, email, nickname, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, nickname=nickname, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nickname, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_uploader', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        if extra_fields.get('is_uploader') is not True:
            raise ValueError('Superuser must have is_uploader=True.')

        return self.create_user(email, nickname, password, **extra_fields)

class User(AbstractUser):

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',  # 충돌 방지를 위해 새로운 이름 지정
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        verbose_name='groups'
    )
    
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_permissions_set',  # 충돌 방지를 위해 새로운 이름 지정
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )


    nickname =models.CharField(max_length=30, null=True, unique=True)
    email = models.EmailField(unique=True, null=False, blank=False)
    is_uploader = models.BooleanField(default=False, help_text='Enable file uploads', verbose_name='uploader')
    username = None

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nickname']
    
    objects = UserManager()

    def __str__(self):
        return self.email

# Create your models here.