from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

# Create your models here.  
#Always install Pilllow anytime you are making use of the ImageField


# class Userprofile(models.Model):
#     username = models.CharField(max_length=200, blank=True, null=True)
#     fullname = models.CharField(max_length= 300, blank=True, null=True)
#     email = models.EmailField(max_length=300, blank=True, null=True)
#     address = models.CharField(max_length= 300, blank=True, null=True)
#     dob = models.DateField(blank=True, null=True)
#     profile_image = models.ImageField(upload_to='userprofile')
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     # user = models.ForeignKey(User, on_delete=models.CASCADE)
#     activation_key = models.CharField(max_length=300, blank=True, null=True)
    
#     def __str__(self):
#         return str(self.user)
# User.profile = property(lambda u: Userprofile.objects.get_or_create(user=u)[0])

# class Userprofile(models.Model):
#     username = models.CharField(max_length=200, blank=True, null=True)
#     fullname = models.CharField(max_length= 300, blank=True, null=True)
#     email = models.EmailField(max_length=300, blank=True, null=True)
#     address = models.CharField(max_length= 300, blank=True, null=True)
#     dob = models.DateField(blank=True, null=True)
#     profile_image = models.ImageField(upload_to='profile')
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     # user = models.ForeignKey(User, on_delete=models.CASCADE)
#     activation_key = models.CharField(max_length=300, blank=True, null=True)
    
#     def __str__(self):
#         return str(self.user)


class Userprofile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField(max_length=300, blank=True, null=True)
    address = models.CharField(max_length= 300, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    fullname = models.CharField(max_length=100, blank=True, null=True)
    username = models.CharField(max_length=50, null=True, default=1)
    profile_image = models.ImageField(upload_to='profile')
    activation_key = models.CharField(max_length=300, blank=True, null=True)

    def __str__(self):
        return str(self.user)



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
    user = models.ForeignKey(User, on_delete=models.CASCADE)
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
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.CharField(max_length=300, blank=True, null=True)
    amount = models.IntegerField(null=True, blank=True)
    date = models.DateTimeField(auto_now=True)
    expensetype = models.ForeignKey(Expensescategory, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.description} - {self.date.strftime('%B %Y')}" 


#Models to manage resetting income and expenses
class IncomeReset(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    last_reset = models.DateField()
    # Add other fields related to income reset
    
    def _str_(self):
        return self.user



class ExpenseReset(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    last_reset = models.DateField()
    # Add other fields related to expense reset
    def _str_(self):
        return self.user
    


class MonthlyBudget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    month = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.month.strftime('%B %Y')}"
