from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

# Create your models here.  
#Always install Pilllow anytime you are making use of the ImageField

class Userprofile(models.Model):
    fullname = models.CharField(max_length= 300, blank=True, null=True)
    email_address = models.EmailField(max_length=300, blank=True, null=True)
    address = models.CharField(max_length= 300, blank=True, null=True)
    dob = models.DateField(auto_now_add=True)
    profile_image = models.ImageField(upload_to='userprofile')
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.fullname


class Incomecategory(models.Model):
    name = models.CharField(max_length=200, blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True, max_length=300,)
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Incomecategory, self).save(*args, **kwargs)
    
    def __str__(self):
        return self.name

class Income(models.Model):
    description = models.CharField(max_length=300, blank=True, null=True)
    amount = models.IntegerField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    incometype = models.ForeignKey(Incomecategory, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.description 


class Expensescategory(models.Model):
    name = models.CharField(max_length=200, blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True, max_length=300,)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Expensescategory, self).save(*args, **kwargs)
    
    def __str__(self):
        return self.name


class Expenses(models.Model):
    description = models.CharField(max_length=300, blank=True, null=True)
    amount = models.IntegerField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    expensetype = models.ForeignKey(Expensescategory, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.description 



#Models to manage resetting income and expenses.
class IncomeReset(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    last_reset = models.DateField()
    # Add other fields related to income reset
    
    def _str_(self):
        return self.name



class ExpenseReset(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    last_reset = models.DateField()
    # Add other fields related to expense reset
    
    def _str_(self):
        return self.name