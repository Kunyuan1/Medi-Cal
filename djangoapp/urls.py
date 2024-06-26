"""
URL configuration for djangoapp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from core import views

#any url starting with schedule gets routed to that app's url file
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.default.as_view(), name="default"),
    path('home/',views.home.as_view(), name = 'home'),
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name = 'signin'),
    path('signout/', views.signout, name = 'signout'),
    #path('activate/',views.activate, name = 'activate'),
    path('index/',views.index.as_view(), name = 'index'),
    path('appointment/', views.appointment.as_view(), name = 'appointment'),
    path('personschedule/',views.personschedule.as_view(), name = 'personschedule'),
    path('personschedule/event-surgery.html/',views.eventsurgery, name = 'event-surgery'),
    path('followups/',views.followups, name = 'followups'),
    path('aboutus/',views.aboutus, name = 'aboutus'),
    path('archive/', views.archive.as_view(), name='archive'),    
    path('archive/event-surgery.html/', views.eventsurgery, name='event-surgery'),
    path('delete/', views.delete.as_view(), name='delete'),
    path('followups/',views.followups, name = 'followups'),
    path('aboutus/',views.aboutus, name = 'aboutus'),
    path('archive/', views.archive.as_view(), name='archive'),    
]