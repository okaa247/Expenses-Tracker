from django.urls import path
from .views import *

urlpatterns = [
    path('', Dashboard.as_view(), name='dashboard'),
    path('register', Register.as_view(), name='register'),
    path('login', Login.as_view(), name='login'),
    path('passwordreset', ForgotPassword.as_view(), name='resetpassword'),
    # path('logout', Logout, name='logout'),



    # path('details_blog/<int:pk>', Blog_details.as_view(), name='details'),
    # path('categories/<slug:category_slug>', Categories.as_view(), name='category'),
]