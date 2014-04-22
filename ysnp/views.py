from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.template import RequestContext, Template
from django.views.generic import DetailView, ListView, TemplateView, CreateView, UpdateView
from braces.views import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from ysnp.models import Assessment, Assignment, Course, Profile, Student_Course
from ysnp import forms

class Home(LoginRequiredMixin, TemplateView):
    template_name = 'base.html'
    
class CourseListView(LoginRequiredMixin, ListView):
    model = Course
    template_name = 'course_list.html'
    context_object_name = 'courses'

    def get_queryset(self):
    	user = self.request.user
    	if user.profile.is_lecturer():
    		return Course.objects.filter(lecturer=user.profile)
    	elif user.profile.is_student():
    		return Course.objects.filter(student_course__student=user.profile)
    	else:
    		return Course.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super(CourseListView, self).get_context_data(**kwargs)
        for course in self.object_list:
            course.attendees = Profile.occupation.get_students().filter(student_course__course=course).count()
        return context

class CourseDetailView(LoginRequiredMixin, DetailView):
    model = Course
    template_name = 'course_detail.html'
    context_object_name = 'course'

    def test_func(self, user):
    	if user.profile.is_lecturer():
    		return self.object.lecturer == user.profile
    	elif user.profile.is_student():
    		return Student_Course.objects.filter(course=self.object, student=user.profile).exists()
    	else:
    		return False
    
    def get_context_data(self, **kwargs):
        context = super(CourseDetailView, self).get_context_data(**kwargs)
        context['allowed'] = self.test_func(self.request.user)
        if context['allowed']:
            context['students'] = Profile.occupation.get_students().filter(student_course__course__course_id=self.kwargs.get('pk'))
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

class AssessmentCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = "ysnp.add_assessment"
    model = Assessment
    template_name = 'assessment_create.html'
    form_class = forms.AssessmentForm

    def get_form_kwargs(self):
        kwargs = super(AssessmentCreateView, self).get_form_kwargs()
        kwargs['possible_courses'] = Course.objects.filter(lecturer=self.request.user.profile)
        return kwargs

class AssessmentUpdateView(LoginRequiredMixin, UpdateView):
    model = Assessment
    template_name = 'assessment_create'
    form_class = 'AssessmentForm'

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

class ProfileView(LoginRequiredMixin, TemplateView):
    model = User
    template_name = 'profile.html'

class PasswordSuccessView(LoginRequiredMixin, TemplateView):
    template_name = 'passwordChangeSuccess.html'
     