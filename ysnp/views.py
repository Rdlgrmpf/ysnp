from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.template import RequestContext, Template
from django.views.generic import ListView, TemplateView
from braces.views import LoginRequiredMixin
from ysnp.models import Course,Student

class Home(LoginRequiredMixin, TemplateView):
    template_name = 'base.html'

def logout_view(request):
    logout(request)
    
class ListCourseView(LoginRequiredMixin, ListView):

    model = Course
    template_name = 'courses_list.html'


@login_required
def course_view(request, id):
    if id:
        students = Student.objects.filter(student_course__course=id)
        return render(request, 'studentList.html', {'students':students})
        
        
        
        