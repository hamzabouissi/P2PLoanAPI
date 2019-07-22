from django.db import models
from django.conf import settings
# Create your models here.
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser,PermissionsMixin
)
from django.utils.translation import gettext_lazy as _
import uuid

class MyUserManager(BaseUserManager):
    def create_user(self,email,password,**extra_field):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """

        user = self.model(
            email=self.normalize_email(email),
            **extra_field
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self,email,password,**extra_field):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.model(
            email=self.normalize_email(email),
            **extra_field
        )
        user.is_admin = True
        user.is_staff=True
        user.is_superuser = True
        user.set_password(password)
        user.save(using=self._db)
        return user


class User(AbstractBaseUser,PermissionsMixin):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    
    id_card = models.PositiveIntegerField(null=True,default=None)
    picture = models.ImageField(upload_to='users_pic',null=True)
    first_name=models.CharField(max_length=25)
    last_name=models.CharField(max_length=25)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )

    money = models.PositiveIntegerField(default=0)
    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name','last_name']

    def __str__(self):
        return f"MR {self.first_name} "

   



class Loan(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    giver = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='loan_giver', on_delete=models.CASCADE)
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='loan_receiver', on_delete=models.CASCADE)
    loaned_at = models.DateTimeField(auto_now_add=True)        
    length = models.PositiveSmallIntegerField()
    amount = models.PositiveIntegerField(blank=False)
    accepted = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # CHECK USER GIVER MONEY
        if self.accepted and self.giver.money>=self.amount:
            self.exchange()
          # Call the "real" save() method.
        super().save(*args,**kwargs)
        
    # TRANSER MONEY
    def exchange(self,*args,**kwargs):
        self.giver.money -= self.amount
        self.receiver.money += self.amount
        self.giver.save()
        self.receiver.save()