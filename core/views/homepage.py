from django.shortcuts import render
from django.http import HttpResponse
from core.models import Surgeon
from django.views.generic import TemplateView

class base(TemplateView):
    """
    View which displays base.html
    Sidebar for personschedule and archive
    """
    template_name = 'base.html'
    def post(self, request):
        '''
        Displays the base for all websites
        '''
        dict = {"name": "test name, should be accessing model though"}
        return render(request, self.template_name, dict)

class home(TemplateView):
    """
    View for home template
    homepage
    """
    template_name = 'home.html'
    def post(self, request):
        '''
        Displays homepage, using base template
        '''
        dict = {"name": "test name, should be accessing model though"} 
        return render(request, self.template_name, dict)


class index(TemplateView):
    """
    index view
    This is a test view
    """
    template_name = 'base.html'
    def post(self, request, id):
        return render(request, self.template_name, {"name": "test name, should be accessing model though"})

       