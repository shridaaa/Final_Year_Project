from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone
from datetime import timedelta, date
from django.conf import settings  # To link appointments to custom user model
from PIL import Image



# BaseUserManager allows for cration of method of users (eg. def create_user, def create super_user). 
# Also gives method to normalize email addresses.

class UserManager(BaseUserManager):
    def create_user(self, first_name, last_name , username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('An email is required')
        if not first_name:
            raise ValueError('A first name is required')
        if not password:
            raise ValueError('A password is required')
        if 'password2' in extra_fields and password != extra_fields['password2']:
            raise ValueError('Passwords do not match')
        
        user = self.model(
            email = self.normalize_email(email),
            first_name=first_name, 
            last_name=last_name,
            username = username,
            **extra_fields
            )
        
        user.set_password(password)
        user.save(using=self._db) #saving user into database
        return user

    def create_superuser(self, first_name, last_name , username, email, password=None, **extra_fields):

        user = self.model(
            email = self.normalize_email(email),
            first_name=first_name, 
            last_name=last_name,
            username = username,
            **extra_fields
            )
        
        if not password:
            raise ValueError('A password is required for superusers')

        user.is_admin = True
        user.is_active =True
        user.is_staff = True
        user.is_superadmin=True

      

        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superadmin = True
        user.save(using=self._db)  # Save the user after setting the required flags
        return user
        
        # extra_fields.setdefault('is_admin', True)
        # extra_fields.setdefault('is_staff', True)
        # extra_fields.setdefault('is_superuser', True)
        #return self.create_user(first_name, last_name, username, email, password, **extra_fields) #leverage the existing create_user method to handle the creation of the superuser.


#By using AbstarctBaseUser, we can use email to login, which is not possible in AbstactUser and normal User models

class AppUser(AbstractBaseUser):
    BLOOD_TYPE_CHOICES = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    ]

    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    
    MEMBERSHIP_CHOICES = [
        ('bronze', 'Bronze Member'),
        ('silver', 'Silver Member'),
        ('gold', 'Gold Member'),
        ('platinum', 'Platinum Member'),
    ]

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=100)
    phone_number= models.CharField(max_length=12, blank=True)
    dob = models.DateField(null=True)  # Date of Birth field
    identity_no = models.CharField(max_length=20, unique=True)
    additional_info = models.TextField(blank=True, null=True)
    blood_group = models.CharField(max_length=4, choices=BLOOD_TYPE_CHOICES, default='A+')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='M')
    membership_level = models.CharField(max_length=10, choices=MEMBERSHIP_CHOICES, default='bronze')

    #required fields
    date_joined = models.DateTimeField (auto_now_add=True)
    last_login = models.DateTimeField (auto_now_add=True)
    created_date = models.DateTimeField (auto_now_add=True, null=True)
    modified_date = models.DateTimeField (auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False )
    is_superadmin = models.BooleanField(default=False)

    objects = UserManager()
    
    USERNAME_FIELD = 'identity_no'
    REQUIRED_FIELDS = ['email', 'dob', 'username','first_name', 'last_name', 'phone_number','blood_group','gender']

    def __str__(self):
        return  self.identity_no + ' : ' + self.first_name + ' ' + self.last_name
    
    def has_perm(self,perm,obj=None): 
        return self.is_admin or self.is_superadmin
        #checks if a user has a specific permission, typically for
        #  individual actions, like adding or deleting a model object
    
    def has_module_perms(self, app_label):
        return self.is_admin or self.is_superadmin
    #checks if the user has any permissions within a specific app (e.g., auth, admin). 
    # It's used more broadly to see if the user can access an app and perform any actions within it.
    


class DonationCenter(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()
    city = models.CharField(max_length=50)
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    map_image = models.ImageField(upload_to='map_images/', blank=True, null=True)

    def __str__(self):
        return self.name
    

class Appointment(models.Model):
    donor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    center = models.ForeignKey(DonationCenter, on_delete=models.CASCADE)
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    notes = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, default='Pending', choices=[
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Cancelled', 'Cancelled'),
    ])

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Appointment for {self.donor} on {self.appointment_date} at {self.appointment_time}"
    

class BloodInventory(models.Model):
    BLOOD_TYPE_CHOICES = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    ]

    blood_type = models.CharField(max_length=3, choices=BLOOD_TYPE_CHOICES, unique=True)
    days_remaining = models.IntegerField()

    def __str__(self):
        return f"{self.blood_type} - {self.days_remaining} days remaining"