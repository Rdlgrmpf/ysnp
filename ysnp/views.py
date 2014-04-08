from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.template import RequestContext, Template
from ysnp.models import Course,Student



def user_login(request):
    # Like before, obtain the context for the user's request.
    context = RequestContext(request)

    # If the request is a HTTP POST, try to pull out the relevant information.
    if request.method == 'POST':
        # Gather the username and password provided by the user.
        # This information is obtained from the login form.
        username = request.POST['username']
        password = request.POST['password']

        # Use Django's machinery to attempt to see if the username/password
        # combination is valid - a User object is returned if it is.
        user = authenticate(username=username, password=password)

        # If we have a User object, the details are correct.
        # If None (Python's way of representing the absence of a value), no user
        # with matching credentials was found.
        if user is not None:
            # Is the account active? It could have been disabled.
            if user.is_active:
                # If the account is valid and active, we can log the user in.
                # We'll send the user back to the homepage.
                login(request, user)
                return HttpResponseRedirect('/admin/')
            else:
                # An inactive account was used - no logging in!
                return HttpResponse("Your User account is disabled.")
        else:
            # Bad login details were provided. So we can't log the user in.
            return render(request, 'app/login.html', {'next': '/main/', 'error':1})

    # The request is not a HTTP POST, so display the login form.
    # This scenario would most likely be a HTTP GET.
    else:
        # No context variables to pass to the template system, hence the
        # blank dictionary object...
           return render(request, 'login.html', {'next': '/main/'})
       
@login_required
def home(request):
    return render(request, 'base.html')

def logout_view(request):
    logout(request)
    
@login_required
def courses_view(request):
    courses = Course.objects.filter(lecturer=1)
    return render(request, 'coursesList.html', {'courses':courses})

@login_required
def course_view(request, id):
    if id:
        students = Student.objects.filter(student_course__course=id)
        return render(request, 'studentList.html', {'students':students})
        
        
        
        