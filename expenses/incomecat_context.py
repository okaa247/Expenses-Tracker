from .models import *



def category_list(request):
    global_list = Incomecategory.objects.all()
    return {
        'global_list': global_list,
    }

