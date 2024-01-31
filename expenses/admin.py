from django.contrib import admin
from .models import *
# Register your models here.


@admin.register(Userprofile)
class userprofile(admin.ModelAdmin):
    list_display = ('fullname', 'dob', 'address')

@admin.register(Incomecategory)
class incomecategory(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Income)
class income(admin.ModelAdmin):
    list_display = ('description', 'amount', 'date')


@admin.register(Expensescategory)
class expensescategory(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Expenses)
class expenses(admin.ModelAdmin):
    list_display = ('description', 'amount', 'date')

@admin.register(MonthlyBudget)
class budget(admin.ModelAdmin):
    list_display = ('name', 'amount', 'month')

admin.site.register(IncomeReset)

admin.site.register(ExpenseReset)