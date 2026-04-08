from django.shortcuts import render

# Create your views here.
def home_page(request):
    return render(request, 'index.html')

def catalog_page(request):
    return render(request, 'catalog.html')

def account_page(request):
    return render(request, 'account.html')