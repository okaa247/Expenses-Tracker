# Create a file 'context_processors.py' in your app
from .models import Userprofile

def profile_info(request):
    if request.user.is_authenticated:
        try:
            profile = Userprofile.objects.get(user=request.user)
            return {'user_profile': profile}
        except Userprofile.DoesNotExist:
            pass
    return {}
