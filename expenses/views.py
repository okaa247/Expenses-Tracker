from django.shortcuts import render, redirect, HttpResponse
from django.views.generic import View, ListView
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from .models import *
import uuid
from django.contrib import messages
from django.db.models import Sum
from django.db import IntegrityError
from datetime import datetime
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.utils.encoding import force_str
from django.core.exceptions import MultipleObjectsReturned


# from django.http import HttpResponse, HttpResponseRedirect
# from django.contrib.auth import get_user_model

# Create your views here.



class Dashboard(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request):
        # Filter income and expense entries for the logged-in user
        income_list = Income.objects.filter(user=request.user)
        expenses_list = Expenses.objects.filter(user=request.user)
    
        # Calculate sum total of all category incomes
        sum_total_income = Incomecategory.objects.filter(
            income__user=request.user
        ).aggregate(sum_total_income=Sum('income__amount'))['sum_total_income'] or 0

        # Calculate sum total of all category expenses
        sum_total_expense = Expensescategory.objects.filter(
            expenses__user=request.user
        ).aggregate(sum_total_expense=Sum('expenses__amount'))['sum_total_expense'] or 0

        # Calculate percentage expenses in relation to total income
        total_expense_percentage = (sum_total_expense / sum_total_income) * 100 if sum_total_income != 0 else 0

        # Prepare data for the pie chart
        income_categories = Incomecategory.objects.filter(income__user=request.user).distinct()
        incometype_labels = [incometype.name for incometype in income_categories]
        incometype_amounts = [Income.objects.filter(incometype=incometype, user=request.user).aggregate(total_amount=Sum('amount'))['total_amount'] or 0 for incometype in income_categories]

        # Construct a date object for the first day of the current month
        current_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Fetch monthly budget for the logged-in user
        monthly_budget = MonthlyBudget.objects.filter(
            user=request.user, month=current_month_start
        ).aggregate(monthly_budget=Sum('amount'))['monthly_budget'] or 0

        # Calculate percentage of expenses in relation to monthly budget
        if monthly_budget != 0:
            expenses_percentage = (sum_total_expense / monthly_budget) * 100
        else:
            expenses_percentage = 0

        context = {
            'sum_total_income': sum_total_income,
            'sum_total_expense': sum_total_expense,
            'total_expense_percentage': total_expense_percentage,
            'income_categories': income_categories,
            'income_list': income_list,
            'monthly_budget': monthly_budget,
            'expenses_list': expenses_list,
            'category_labels': incometype_labels,
            'category_amounts': incometype_amounts,
            'remaining_monthly_budget': monthly_budget,
            'expenses_percentage': expenses_percentage,
            # 'user_profile': request.user_profile,
            # 'profile_image_url': profile_image_url,
        }
        return render(request, 'index.html', context)



class Signup(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'signup.html')
    
    def post(self, request):
        if request.method == 'POST':
            email = request.POST.get('email')
            username = request.POST.get('username')
            password = request.POST.get('password')
            password2 = request.POST.get('password2')

            # Check if the email already exists
            if User.objects.filter(email=email).exists():
                messages.error(request, 'Email address already exists.')
                return render(request, 'signup.html')

            if password != password2:
              return render(request, 'signup.html', {'error': 'Passwords do not match'})

            # Create a user without saving it to the database
            user = User.objects.create_user(username=username, email=email, password=password, is_active=False)
            # Generate a link for completing the registration
            activation_key = str(uuid.uuid4())
            profile = Userprofile.objects.create(user=user, activation_key=activation_key)
            registration_link = f"http://127.0.0.1:8000/register/{profile.activation_key}/"

            # Send registration link to the user's email
            send_mail(
                'Complete Your Registration',
                f'Use this link to complete your registration: {registration_link}',
                'joshlove00001@gmail.com',
                [email],
                fail_silently=False,
            )
            return HttpResponse('Check your mail for link to complete your registration')
        
        #  return render(request, 'register.html')



class RegisterActivationView(View):
    def get(self, request, activation_key):
        try:
            # Find the user profile with the given activation key
            profile = Userprofile.objects.get(activation_key=activation_key)
            # Activate the associated user
            user = profile.user
            user.is_active = True
            user.save()
            # Render a success page or redirect to registration page
            # messages.success(request, 'Activation successful. You can now continue with your registration.')
            # return redirect('register')
            return render(request, 'register.html', {'user': user})

        except Userprofile.DoesNotExist:
            # Render an error page or redirect to an error page
            messages.error(request, 'Invalid activation key. Please contact support.')
            return redirect('error_page')
        
  
class Register(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'register.html')

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            # Retrieve data from the form
            fullname = request.POST.get('fullname')
            address = request.POST.get('address')
            dob = request.POST.get('dob')

            # Retrieve the existing user based on the provided primary key (pk)
            user_pk = kwargs.get('pk')
            user = User.objects.get(pk=user_pk)

            # Create or update the user profile
            profile, profile_created = Userprofile.objects.get_or_create(user=user)
            profile.fullname = fullname
            profile.address = address
            profile.dob = dob
            profile.save()
            return redirect('login')  # Redirect to a success page or login page
        return render(request, 'register.html')


class Login(View):
    def get(self, request):
        return render(request, 'login.html') 
    
    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            return HttpResponse('Username and password are required', status=400)
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return HttpResponse('Username not found', status=404)
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return HttpResponse('Incorrect password, try again', status=401)
    
         
def Logout(request):
    logout(request)
    return redirect('login')
 


# Function for creating new income
class IncomeCreateView(View):
    def get(self, request):
        categories = Incomecategory.objects.all()
        context = {
            'categories': categories,
        }    
        return render(request, 'incoexp/income_create.html', context=context)

    def post(self, request):
        # Extract data from the request
        description = request.POST.get('description')
        amount = request.POST.get('amount')
        incometype_id = request.POST.get('incometype')

        # Create a new income entry
        Income.objects.create(
            user=request.user,
            description=description,
            amount=amount,
            incometype_id=incometype_id
        )
        return redirect('income-list')


# To view list of all income
class IncomeListView(ListView):
    model = Income
    template_name = 'incoexp/income_list.html'
    context_object_name = 'income_list'

    def get_queryset(self):
        # Filter income entries for the current user
        return Income.objects.filter(user=self.request.user)    
    
# class IncomeListView(ListView):
#     def get_queryset(self):
#         # Retrieve expenses for the currently logged-in user
#         return Income.objects.filter(user=self.request.user)

#     def get(self, request):
#         context = {
#             'income_list': self.get_queryset(),
#         }
#         return render(request, 'incoexp/income_list.html', context=context) 




# For income category creation
class IncomeCategoryCreateView(View):
    def get(self, request):
        return render(request, 'incoexp/incomecategory_create.html')

    def post(self, request):
        name = request.POST.get('name')
        try:
            category = Incomecategory.objects.create(name=name)
        except IntegrityError:
            error = "Category with this name already exists."
            return render(request, 'incoexp/incomecategory_create.html', {'error': error})
        return redirect('incomecategory-list')


# This is for viewing income categories
class IncomeCategoryListView(View):
    
    def get(self, request):
        income_categories = Incomecategory.objects.all()
        context ={
            'income_categories': income_categories,
        }
        return render(request, 'incoexp/incomecategory_list.html', context)



# Function for creating new expenses
class ExpensesCreateView(View):
    def get(self, request):
        categories = Expensescategory.objects.all()
        return render(request, 'incoexp/expenses_create.html', {'categories': categories})

    def post(self, request):
        # Extract data from the request
        description = request.POST.get('description')
        amount = request.POST.get('amount')
        expensetype_id = request.POST.get('expensetype')

        # Check if there is a budget for the month
        current_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        # formatting a datetime object into a string
        month_str = current_month_start.strftime('%Y-%m-%d')
        monthly_budget = MonthlyBudget.objects.filter(user=request.user, month=month_str).first()

        # If there's a budget and the expense exceeds the budget, return an error
        if monthly_budget and float(amount) > monthly_budget.amount:
            error = f"Expense exceeds the budget of ${monthly_budget.amount} for {month_str}."
            categories = Expensescategory.objects.all()
            return render(request, 'incoexp/expenses_create.html', {'categories': categories, 'error': error})

        # Use create to create a new entry
        Expenses.objects.create(
            user=request.user,
            description=description,
            amount=amount,
            expensetype_id=expensetype_id,
        )
        return redirect('expenses-list')



# Function to view list of all expenses
class ExpensesListView(ListView):
    model = Expenses
    template_name = 'incoexp/expenses_list.html'
    context_object_name = 'expenses_list'

    def get_queryset(self):
        # Filter income entries for the current user
        return Expenses.objects.filter(user=self.request.user)


# For expenses category creation
class ExpensesCategoryCreateView(View):
    def get(self, request):
        return render(request, 'incoexp/expensescategory_create.html')

    def post(self, request):
        name = request.POST.get('name')
        try:
            category = Expensescategory.objects.create(name=name)
        except IntegrityError:
            error = "Category with this name already exists."
            return render(request, 'incoexp/expensescategory_create.html', {'error': error})
        return redirect('expensescategory-list')


# Function for viewing expenses categories
class ExpensesCategoryListView(View):
    def get(self, request):
        expense_categories = Expensescategory.objects.all()
        return render(request, 'incoexp/expensescategory_list.html', {'expenses_categories': expense_categories})



class TotalExpenseByCategoryView(View):
    def get(self, request):
        # Calculate total expenses for each category
        total_expense_by_category = Expensescategory.objects.annotate(
            total_expense=Sum('expenses__amount')
        ).values('name', 'total_expense')

        # Calculate sum total of all category expenses
        sum_total_expense = Expensescategory.objects.aggregate(
            sum_total_expense=Sum('expenses__amount')
        )['sum_total_expense'] or 0

        # Calculate total income for each income category
        total_income_by_category = Incomecategory.objects.annotate(
            total_income=Sum('income__amount')
        ).values('name', 'total_income')

        # Calculate sum total of all category incomes
        sum_total_income = Incomecategory.objects.aggregate(
            sum_total_income=Sum('income__amount')
        )['sum_total_income'] or 0

        # Calculate total expenses as a percentage of total income
        total_expense_percentage = (sum_total_expense / sum_total_income) * 100 if sum_total_income != 0 else 0
        context = {
            'total_expense_by_category': total_expense_by_category,
            'sum_total_expense': sum_total_expense,
            'total_income_by_category': total_income_by_category,
            'sum_total_income': sum_total_income,
            'total_expense_percentage': total_expense_percentage,
        }
        return render(request, 'incoexp/total_expense.html', context)



class TotalIncomeByCategoryView(View):
    def get(self, request):
        # Calculate total income for each category
        total_income_by_category = Incomecategory.objects.annotate(
            total_income=Sum('income__amount')
        ).values('name', 'total_income')

        # Calculate sum total of all category incomes
        sum_total_income = Incomecategory.objects.aggregate(
            sum_total_income=Sum('income__amount')
        )['sum_total_income'] or 0
        context = {
            'total_income_by_category': total_income_by_category,
            'sum_total_income': sum_total_income,
        }
        return render(request, 'incoexp/total_income.html', context)


class TransactionHistoryView(View):
    def get(self, request):
        # Fetch income and expenses entries for the current user
        income_list = Income.objects.filter(user=request.user)
        expenses_list = Expenses.objects.filter(user=request.user)

        # Combine income and expenses into a single list
        transaction_history = list(income_list) + list(expenses_list)

        # Sort the combined list by date in descending order
        transaction_history.sort(key=lambda x: x.date, reverse=True)
        context = {
            'transaction_history': transaction_history,
        }
        return render(request, 'transaction_history.html', context)



class MonthlyBudgetView(LoginRequiredMixin, View):
    login_url = 'login'  

    def get(self, request):
        # Fetch all monthly budgets
        monthly_budgets = MonthlyBudget.objects.filter(user=request.user)
        # Fetch total income by category
        total_income_by_category = Incomecategory.objects.annotate(
            total_income=Sum('income__amount')
        ).values('name', 'total_income')

        # Fetch sum total income
        sum_total_income = Incomecategory.objects.aggregate(
            sum_total_income=Sum('income__amount')
        )['sum_total_income'] or 0

        context = {
            'monthly_budgets': monthly_budgets,
            'total_income_by_category': total_income_by_category,
            'sum_total_income': sum_total_income,
        }
        return render(request, 'incoexp/monthly_budget.html', context)

    def post(self, request):
        # Extract data from the request
        name = request.POST.get('name')
        amount = request.POST.get('amount')
        month_str = request.POST.get('month')

        # Parse the month string to a datetime object
        try:
            month = datetime.strptime(month_str, '%Y-%m').date()
        except ValueError:
            # Handle invalid date format
            return HttpResponse('Invalid date format for month', status=400)

        # Create a new MonthlyBudget entry with the logged-in user
        MonthlyBudget.objects.create(
            user=request.user,
            name=name,
            amount=amount,
            month=month,
        )
        return redirect('monthly-budget-list')
    


class MonthlyBudgetListView(View):
    def get(self, request):
        # Fetch all monthly budgets
        monthly_budgets = MonthlyBudget.objects.all()
        context = {
            'monthly_budgets': monthly_budgets,
        }
        return render(request, 'incoexp/monthly_budget_list.html', context)




# class ForgotPassword(View):
#     def get(self, request):
#         return render(request, 'forgot-password.html')

#     def post(self, request):
#         email = request.POST.get('email')

#         # Retrieve the user based on the provided email address
#         try:
#             user = User.objects.get(email=email)
#         except User.DoesNotExist:
#             # Provide an error message or redirect to a failure page
#             return HttpResponse('User with this email address does not exist.', status=404)

#         # Generate a one-time use token for password reset
#         uid = urlsafe_base64_encode(force_bytes(user.pk))
#         token = default_token_generator.make_token(user)

#         # Construct the password reset link
#         reset_link = f"http://{request.get_host()}/reset/{uid}/{token}/"

#         # Send the password reset link to the user's email
#         send_mail(
#             'Password Reset',
#             f'Use this link to reset your password: {reset_link}',
#             'joshlove00001@gmail.com',  
#             [email],
#             fail_silently=False,
#         )
#         # Provide a success message 
#         return HttpResponse('Check your mail for the password reset link.')
    


# class PasswordResetConfirm(View):
#     template_name = 'resetconfirm.html' 
#     success_url = '/login/'  # URL to redirect to after successful password reset

#     def get(self, request, uidb64, token):
#         try:
#             # Decode the user ID from base64
#             uid = force_str(urlsafe_base64_decode(uidb64))
#             # Get the user based on the decoded ID
#             user = get_user_model().objects.get(pk=uid)

#             # Check if the token is valid for the user
#             if default_token_generator.check_token(user, token):
#                 # Render the password reset confirmation form
#                 return render(request, 'resetconfirm.html', {'validlink': True, 'uidb64': uidb64, 'token': token})
#         except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
#             pass

#         # If the link is invalid, render an error page
#         return render(request, 'invalid_reset_link.html')

#     def post(self, request, uidb64, token):
#         # Handle the form submission to set a new password
#         uid = force_str(urlsafe_base64_decode(uidb64))
#         user = get_user_model().objects.get(pk=uid)

#         password = request.POST.get('new_password')
#         confirm_password = request.POST.get('confirm_password')

#         # Add any additional validation logic here if needed
#         if password != confirm_password:
#               return render(request, 'resetconfirm.html', {'error': 'Passwords do not match'})

#         # Set the new password
#         user.set_password(password)
#         user.save()

#         # Redirect to the success page
#         return HttpResponseRedirect('login')


class ForgotPassword(View):
    def get(self, request):
        return render(request,  'forgot-password.html')

    def post(self, request):
        email = request.POST.get('email')

        # Retrieve the user based on the provided email address
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Provide an error message or redirect to a failure page
            return HttpResponse('User with this email address does not exist.', status=404)

        # Generate a one-time use token for password reset
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        # Construct the password reset link
        reset_link = f"http://{request.get_host()}/reset/{uid}/{token}/"

        # Send the password reset link to the user's email
        send_mail(
            'Password Reset',
            f'Use this link to reset your password: {reset_link}',
            'joshlove00001@gmail.com',  
            [email],
            fail_silently=False,
        )
        # Provide a success message 
        return HttpResponse('Check your mail for the password reset link.')
    
    
class PasswordResetConfirm(View):
    def get(self, request, uidb64, token):
        try:
            # Decode the user ID from base64
            uid = force_str(urlsafe_base64_decode(uidb64))
            # Get the user based on the decoded ID
            user = User.objects.get(pk=uid)

            # Check if the token is valid for the user
            if default_token_generator.check_token(user, token):
                # Render the password reset confirmation form
                return render(request, 'resetconfirm.html', {'validlink': True, 'uidb64': uidb64, 'token': token})
        except (TypeError, ValueError, OverflowError, User.DoesNotExist, MultipleObjectsReturned):
            pass

        # If the link is invalid, 
        return render(request, 'forgot-password')

    def post(self, request, uidb64, token):
        # We Handle the form submission to set a new password
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)

        password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        # validation logic 
        if password != confirm_password:
            return render(request, 'resetconfirm.html', {'error': 'Passwords do not match'})

        # Set the new password
        user.set_password(password)
        user.save()

        # Redirect to the login page
        return redirect('login')