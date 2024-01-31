from .models import *



def cate_list(request):
    globa_list =Expensescategory.objects.all()
    return {
        'globa_list': globa_list,
    }

