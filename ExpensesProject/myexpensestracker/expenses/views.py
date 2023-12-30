from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

# Create your views here.


class Dashboard(View):
    def get(self, request):
        return render(request, 'index.html')
    
    def post(self, request):
        return render(request, 'index.html')


class Register(View):
    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
        return render(request, 'register.html') 
    

class Login(View):
    def get(self, request):
        return render(request, 'login.html') 
    
    def post(self, request):
        return render(request, 'login.html')
    

class ForgotPassword(View):
    def get(self, request):
        return render(request, 'forgot-password.html') 
    
    def post(self, request):
        return render(request, 'forgot-password.html')    