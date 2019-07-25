from django.db import models
from django.conf import settings
# Create your models here.
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser,PermissionsMixin
)
from django.utils.translation import gettext_lazy as _
import uuid
from datetime import date,timedelta
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import MaxValueValidator,MinValueValidator 
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
   
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    phone = models.PositiveIntegerField(unique = True,validators=[MinValueValidator(10000000),MaxValueValidator(19999999)])
    picture = models.ImageField(upload_to='users_pic',null=True)
    money = models.PositiveIntegerField(default=0)
    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone',]

    def __str__(self):
        return f"MR {self.email} "


class Citizien(models.Model):

    profile = models.OneToOneField(settings.AUTH_USER_MODEL,related_name='citizien',on_delete=models.CASCADE)
    id_card = models.PositiveIntegerField(unique = True,blank=True,null=True,default=None,validators=[MinValueValidator(10000000),MaxValueValidator(19999999)])
    first_name=models.CharField(max_length=25)
    last_name=models.CharField(max_length=25)



class Company(models.Model):

    profile = models.OneToOneField(settings.AUTH_USER_MODEL,related_name='company',on_delete=models.CASCADE)
    name = models.CharField(max_length=25)
    rue = models.CharField(max_length='100')






class Loan(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    giver = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='loan_giver', on_delete=models.CASCADE)
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='loan_receiver', on_delete=models.CASCADE)
    description = models.TextField(max_length=200,default='')
    length = models.PositiveSmallIntegerField()
    amount = models.PositiveIntegerField(blank=False)
    #accepted = models.BooleanField(default=False)
    giver_acceptance = models.BooleanField(default=False)
    receiver_acceptance = models.BooleanField(
        default=False,
        help_text=_('Don\'t check this until your receive your money '),
        )

    final_amount = models.PositiveIntegerField(default=0) # THIS FIELD DESCRIBE FINAL AMOUNT TO RETURN TO THE BORROWER
    
    loaned_at = models.DateField(null=True,blank=True)        

    def save(self, *args, **kwargs):
        # CHECK USER GIVER MONEY
        if self.giver_acceptance and self.receiver_acceptance and self.giver.money>=self.amount:
            
            self.exchange()
            self.loaned_at = date.today()
            self.create_new_track()
            

        # Call the "real" save() method.
        super().save(*args,**kwargs)
        
    # TRANSER MONEY
    def exchange(self,*args,**kwargs):
        self.giver.money -= self.amount
        self.receiver.money += self.amount
        self.giver.save()
        self.receiver.save()

    def create_new_track(self):
        Track.objects.create(loan=self,expected_date=self.loaned_at+timedelta(30))
    
class Track(models.Model):
    loan = models.ForeignKey('Loan',related_name='tracks',on_delete=models.CASCADE)
    money = models.PositiveIntegerField(default=0) # THIS DESCRIBE THE AMOUNT RECEIVED
    expected_date = models.DateField(blank=False) # DESCRIBE THE DATE WHEN RECEIVER SHOULD PAY HIS BILL
    final_date = models.DateField(null=True,blank=True)
    received = models.BooleanField(default=False)

    def save(self,*args,**kwargs):
        if self.received == True:
            # self.final_date = date.today() # REMOVER THIS DURING DEVELOPMENT
            # WE SHOULD CREATE THE NEXT TRACK WITH CONDITION 
            # THE DATE OF THE LAST TRACK < THE CREATION DATE OF LOAN + LENGTH
            month = self.loan.loaned_at.month + self.loan.length
            if self.expected_date.month < month :
                self.create_new_track()
        super().save(*args,**kwargs)


    def create_new_track(self):
        Track.objects.create(loan=self.loan,expected_date=self.expected_date+timedelta(30))

    def __str__(self):
        msg = f'This Bill shoud be payed at {self.expected_date}'
        if self.received:
            delay = self.final_date - self.expected_date
            msg = f"Received amount = {self.money} at {self.final_date} with delay {delay}"
        return msg