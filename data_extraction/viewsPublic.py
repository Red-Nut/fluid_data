from django.shortcuts import render

def index(request):
    return render(request, "public/index.html")

def about(request):
    return render(request, "public/about.html")

def pricing(request):
    return render(request, "public/pricing.html")

def contact(request):
    return render(request, "public/contact.html")
