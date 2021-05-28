from django.shortcuts import render

def index(request):
    return render(request, "hilichurlian_database/index.html")