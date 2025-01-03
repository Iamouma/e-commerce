# Create your views here.
from django.shortcuts import render

def homepage(request):
    return render(request, 'shop/homepage.html')
