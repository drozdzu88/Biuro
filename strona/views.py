from django.shortcuts import render


# Create your views here.

def home(request):
	return render(request, 'strona/home.html')

def about_me(request):
	return render(request, 'strona/about_me.html')

def projects(request):
	return render(request, 'strona/projects.html')

def video(request):
	return render(request, 'strona/video.html')
