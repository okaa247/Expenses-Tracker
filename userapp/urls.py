from django.urls import path
from .views import *


urlpatterns = [
    path('', BaseProfileView.as_view(), name='userprofile'),
    path('profilepage', ProfilePage.as_view(), name='profilepage'),
    path('updateprofile', UserProfileUpdateView.as_view(), name='updateprofile'),

]