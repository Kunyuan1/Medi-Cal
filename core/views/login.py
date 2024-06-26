from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.views.generic import TemplateView
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage, send_mail
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from core.models import Time, Employee, Surgeon, Cleaner, Patient, Surgery

# from core import Surgeon, Time, Employee

# Create your views here.
class default(TemplateView):
    """
    Default template which returns index.html
    """
    template_name = 'index.html'


#signup view 
def signup(request):
    #POST is only request method
    if request.method == "POST":
        #get input via POST
        username = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']

        #validation for fields
        #if invalid, return a message error and redirect
        if User.objects.filter(username=username):
            messages.error(request, "Username already exists.")
            return redirect('index')
        
        if User.objects.filter(email=email):
            messages.error(request, "Email already registered.")
            return redirect('index')
        
        if len(username)>15:
            messages.error(request, "Username must be under 15 characters.")

        if pass1 != pass2:
            messages.error(request, "Passwords do not match.")

        if not username.isalnum():
            messages.error(request, "Username must be alpha-numeric.")
            return redirect('index')

        #create user
        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name = fname
        myuser.last_name = lname

        #save
        myuser.is_active = True
        myuser.save()

        #redirect to signin
        return redirect('signin')

    return render(request, "index.html")


#signin view
def signin(request):
    #POST is only method
    if request.method == 'POST': 
        #get input via POST
        username = request.POST['username']
        pass1 = request.POST['pass1']

        #authenticate
        user = authenticate(username=username, password=pass1)
        
        #if it works, login
        if user is not None:
            login(request, user)
            fname = user.first_name
            return render(request, "home.html", {'fname': fname})
            
            

        else:
            #return error message otherwise
            messages.error(request, "Wrong Credentials.")
            return redirect('index')


    return render(request, "index.html")

#signout 
def signout(request):
    logout(request)
    #redirect to index
    return redirect('index')

def aboutus(request):
    #about us view, returns aboutus.html
    return render(request, "aboutus.html")

