from django.shortcuts import render

def home_view(request):
    return render(request, 'home.html')

def bell_view(request):
    return render(request, 'bells.html')

def manufacturer_view(request):
    return render(request, 'manufacturers.html')

def tower_view(request):
    return render(request, 'towers.html')

def carillon_view(request):
    return render(request, 'carillons.html')

def search_view(request):
    return render(request, 'search.html')
