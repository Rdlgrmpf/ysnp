from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout

from django.http import HttpResponseRedirect
from django.template import RequestContext, Template
from django.views.generic import DetailView, ListView, TemplateView
from braces.views import LoginRequiredMixin
from ysnp.models import Assessment, Assignment, Course, Student, Student_Course

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
            student.semester = Student_Course.objects.get(course=self.object, student=student).semester
            
        context['assessments'] = Assessment.objects.filter(course=self.object)
        return context

class AssessmentListView(LoginRequiredMixin, ListView):
    model = Assessment
    template_name = 'assessment_list.html'
    context_object_name = 'assessments'


class AssessmentDetailView(LoginRequiredMixin, DetailView):
    model = Assessment
    template_name = 'assessment_detail.html'
    context_object_name = 'assessment'            
    
    def get_context_data(self, **kwargs):
        context = super(AssessmentDetailView, self).get_context_data(**kwargs)
        context['assignments'] = Assignment.objects.filter(assessment=self.object)
        return context       

class AssignmentListView(LoginRequiredMixin, ListView):
    model = Assignment
    template_name = 'assignment_list.html'
    context_object_name = 'assignments'
    
    def get_context_data(self, **kwargs):
        context = super(AssignmentListView, self).get_context_data(**kwargs)
        return context

class AssignmentDetailView(LoginRequiredMixin, DetailView):
    model = Assignment
    template_name = 'assignment_detail.html'
    context_object_name = 'assignment'            
    
    def get_context_data(self, **kwargs):
        context = super(AssignmentDetailView, self).get_context_data(**kwargs)
        return context             