from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from expenses.models import *
from django.contrib import messages
from datetime import datetime
# Create your views here.




class BaseProfileView(View):
    def get_profile_info(self, user):
        try:
            profile = get_object_or_404(Userprofile, user=user)  # Access the related Profile using the lowercased name
        
            profile_info = {
                'profile_image_url': profile.profile_image if profile.profile_image else None,
                'username': profile.fullname,
                'fullname': profile.fullname,
                'email': profile.user.email,
                'address': profile.address,
                'dob': profile.dob,
                'user': profile.user,
            }
            return {'profile_info': profile_info}

        except Userprofile.DoesNotExist:
            return {}


class ProfilePage(LoginRequiredMixin, BaseProfileView):
    login_url = 'login'

    def get(self, request):
        context = {}  # Initialize context
        try:
            context = self.get_profile_info(request.user)
            # if not context:
            #     return redirect('dashboard')
        except:
            if request.user.is_superuser:
                Userprofile.objects.create(user=request.user)
        return render(request, 'usertemp/profile.html', context=context)

    def post(self, request):
        # Process the submitted form data
        return render(request, 'usertemp/profile.html')

# class ProfilePage(LoginRequiredMixin, BaseProfileView):
#     login_url = 'login'
#     def get(self, request):
#         context = self.get_profile_info(request.user)
#         if not context:
#             return redirect('dashboard')
#         return render(request, 'usertemp/profile.html', context=context)
    
#     def post(self, request):
#         # Process the submitted form data
#         return render(request, 'usertemp/profile.html')
    


class UserProfileUpdateView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        profile = get_object_or_404(Userprofile, user=request.user)
        context = {'profile': profile}
        return render(request, 'usertemp/profile_update.html', context)

    def post(self, request, *args, **kwargs):
        profile = get_object_or_404(Userprofile, user=request.user)

        # Update profile fields based on POST data
        fullname = request.POST.get('fullname')
        address = request.POST.get('address')
        dob = request.POST.get('dob')

        # Validate and update fullname
        if fullname:
            profile.fullname = fullname

        # Validate and update address
        if address:
            profile.address = address

        # Validate and update dob
        if dob:
            try:
                # Attempt to parse the provided date
                dob_date = datetime.strptime(dob, "%Y-%m-%d").date()
                profile.dob = dob_date
            except ValueError:
                # Handle invalid date format
                messages.error(request, 'Invalid date format for Date of Birth. Use YYYY-MM-DD.')
                return redirect('updateprofile')

        # Handle profile image
        profile_image = request.FILES.get('profile_image')
        if profile_image:
            profile.profile_image = profile_image

        profile.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profilepage')



# class UserProfileUpdateView(LoginRequiredMixin, View):
#     template_name = 'usertemp/profile_update.html'

#     def get(self, request, *args, **kwargs):
#         profile = get_object_or_404(Userprofile, user=request.user)
#         context = {'profile': profile}
#         return render(request, self.template_name, context)

#     def post(self, request, *args, **kwargs):
#         profile = get_object_or_404(Userprofile, user=request.user)

#         # Update profile fields based on POST data
#         profile.fullname = request.POST.get('fullname')
#         profile.address = request.POST.get('address')
#         profile.dob = request.POST.get('dob')

#         # Handle profile image
#         profile_image = request.FILES.get('profile_image')
#         if profile_image:
#             profile.profile_image = profile_image

#         profile.save()
#         messages.success(request, 'Profile updated successfully!')
#         return redirect('profilepage')






