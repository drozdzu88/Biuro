from django.urls import path 
from . import views

app_name = 'strona'
urlpatterns = [
	path('', views.home, name='home'),
	path('about_me/', views.about_me, name='about_me'),
	path('projects/', views.projects, name='projects'),
	path('video/', views.video, name='video'),
	#path('blog/', views.blog, name="blog"),

]