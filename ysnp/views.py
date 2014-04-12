from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout

from django.http import HttpResponseRedirect
from django.template import RequestContext, Template
from django.views.generic import DetailView, ListView, TemplateView
from braces.views import LoginRequiredMixin
from ysnp.models import Course, Student, Student_Course

class Home(LoginRequiredMixin, TemplateView):
    template_name = 'base.html'
    
class CourseListView(LoginRequiredMixin, ListView):
    model = Course
    template_name = 'course_list.html'
    context_object_name = 'courses'
    
    def get_context_data(self, **kwargs):
        context = super(CourseListView, self).get_context_data(**kwargs)
        for course in self.object_list:
            course.attendees = Student.objects.filter(student_course__course=course).count()
        return context

class CourseDetailView(LoginRequiredMixin, DetailView):
    model = Course
    template_name = 'course_detail.html'
    context_object_name = 'course'            
    
    def get_context_data(self, **kwargs):
        context = super(CourseDetailView, self).get_context_data(**kwargs)
        context['students'] = Student.objects.filter(student_course__course__courseId=self.kwargs.get('pk'))
        for student in context['students']:
            student.semester = Student_Course.objects.get(course=self.object, matrikelNr=student).semester
        return context

        