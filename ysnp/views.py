from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.template import RequestContext, Template
from django.views.generic import DetailView, ListView, TemplateView, CreateView, UpdateView
from braces.views import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from itertools import chain
from ysnp.models import Assessment, Assignment, Course, Profile, Student_Course, Criterion, ScoreLevel
from ysnp import forms
from django.core.urlresolvers import reverse

class Home(LoginRequiredMixin, TemplateView):
    template_name = 'base.html'

###
#   Courses
###

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

###
#   Assessments
###

class AssessmentListView(LoginRequiredMixin, ListView):
    model = Assessment
    template_name = 'assessment_list.html'
    context_object_name = 'assessments'

    def get_queryset(self):
        user = self.request.user
        if user.profile.is_student():
            return Assessment.objects.filter(course__student_course__student=user.profile)
        else:
            return Assessment.objects.filter(Q(course__lecturer=user.profile)|Q(assessor=user.profile)).distinct()


class AssessmentDetailView(LoginRequiredMixin, DetailView):
    model = Assessment
    template_name = 'assessment_detail.html'
    context_object_name = 'assessment'

    def test_func(self, user):
        permission = False
        if user.profile.is_lecturer():
            permission = self.object.course.lecturer == user.profile
        if user.profile.is_student() and not permission:
            permission = Student_Course.objects.filter(course=self.object.course, student=user.profile).exists()
        if user.profile.is_assessor() and not permission:
            permission = self.object.assessor == user.profile
        
        return permission
    
    def get_context_data(self, **kwargs):
        context = super(AssessmentDetailView, self).get_context_data(**kwargs)
        context['allowed'] = self.test_func(self.request.user)
        if context['allowed']:
            context['is_this_lecturer'] = (self.request.user.profile == self.object.course.lecturer)
            context['is_this_assessor'] = (self.request.user.profile == self.object.assessor)
            context['assignments'] = Assignment.objects.filter(assessment=self.object)

        return context

class AssessmentCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = "ysnp.add_assessment"
    raise_exception = True
    model = Assessment
    template_name = 'assessment_create.html'
    form_class = forms.AssessmentForm

    def get_form_kwargs(self):
        kwargs = super(AssessmentCreateView, self).get_form_kwargs()
        kwargs['possible_courses'] = Course.objects.filter(lecturer=self.request.user.profile)
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(AssessmentCreateView, self).get_context_data(**kwargs)
        context['edit'] = False
        return context

class AssessmentUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = "ysnp.change_assessment"
    raise_exception = True
    model = Assessment
    template_name = 'assessment_create.html'
    form_class = forms.AssessmentForm

    def get_form_kwargs(self):
        kwargs = super(AssessmentUpdateView, self).get_form_kwargs()
        kwargs['possible_courses'] = Course.objects.filter(lecturer=self.request.user.profile)
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(AssessmentUpdateView, self).get_context_data(**kwargs)
        context['edit'] = True
        return context

###
#   Assignments
###

class AssignmentListView(LoginRequiredMixin, ListView):
    model = Assignment
    template_name = 'assignment_list.html'
    context_object_name = 'assignments'

    def get_queryset(self):
        user = self.request.user
        if user.profile.is_student():
            return Assignment.objects.filter(assessment__course__student_course__student=user.profile)
        else:
            return Assignment.objects.filter(Q(assessment__course__lecturer=user.profile)|Q(assessment__assessor=user.profile)).distinct()
    
    def get_context_data(self, **kwargs):
        context = super(AssignmentListView, self).get_context_data(**kwargs)
        return context

class AssignmentDetailView(LoginRequiredMixin, DetailView):
    model = Assignment
    template_name = 'assignment_detail.html'
    context_object_name = 'assignment'

    def test_func(self, user):
        permission = False
        if user.profile.is_lecturer():
            permission = self.object.assessment.course.lecturer == user.profile
        if user.profile.is_student() and not permission:
            permission = Student_Course.objects.filter(course=self.object.assessment.course, student=user.profile).exists()
        if user.profile.is_assessor() and not permission:
            permission = self.object.assessment.assessor == user.profile
        
        return permission
    
    def get_context_data(self, **kwargs):
        context = super(AssignmentDetailView, self).get_context_data(**kwargs)
        context['allowed'] = self.test_func(self.request.user)
        if context['allowed']:
            context['criteria'] = Criterion.objects.filter(assignment=self.object)
            context['scorelevels'] = ScoreLevel.objects.filter(assignment=self.object)
            context['is_this_lecturer'] = (self.request.user.profile == self.object.assessment.course.lecturer)
            context['is_this_assessor'] = (self.request.user.profile == self.object.assessment.assessor)
        return context

class AssignmentCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = "ysnp.add_assignment"
    raise_exception = True
    model = Assignment
    template_name = 'assignment_create.html'
    form_class = forms.AssignmentForm

    def get_form_kwargs(self):
        kwargs = super(AssignmentCreateView, self).get_form_kwargs()
        kwargs['possible_assessments'] = Assessment.objects.filter(course__lecturer=self.request.user.profile)
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(AssignmentCreateView, self).get_context_data(**kwargs)
        context['edit'] = False
        return context

class AssignmentUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = "ysnp.change_assignment"
    raise_exception = True
    model = Assignment
    template_name = 'assignment_create.html'
    form_class = forms.AssignmentForm

    def get_form_kwargs(self):
        kwargs = super(AssignmentUpdateView, self).get_form_kwargs()
        kwargs['possible_assessments'] = Assessment.objects.filter(course__lecturer=self.request.user.profile)
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(AssignmentUpdateView, self).get_context_data(**kwargs)
        context['edit'] = True
        return context

###
#   Criterion
###

class CriterionDetailView(LoginRequiredMixin, DetailView):
    model = Criterion
    template_name = 'criterion_detail.html'
    context_object_name = 'criterion'
    
    def get_context_data(self, **kwargs):
        context = super(CriterionDetailView, self).get_context_data(**kwargs)
        return context

class CriterionCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = "ysnp.add_criterion"
    raise_exception = True
    model = Criterion
    template_name = 'criterion_create.html'
    form_class = forms.CriterionForm
    success_url = '.'

    def get_form_kwargs(self):
        kwargs = super(CriterionCreateView, self).get_form_kwargs()
        return kwargs

    def form_valid(self, form):
        form.instance.assignment = Assignment.objects.get(assignment_id=self.kwargs.get('assignment_id'))
        self.success_url = reverse('assignment-detail', kwargs={'pk': self.kwargs.get('assignment_id')})
        return super(CriterionCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(CriterionCreateView, self).get_context_data(**kwargs)
        context['edit'] = False
        return context

class CriterionUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = "ysnp.change_criterion"
    raise_exception = True
    model = Criterion
    template_name = 'criterion_create.html'
    form_class = forms.CriterionForm
    success_url = '.'

    def get_form_kwargs(self):
        kwargs = super(CriterionUpdateView, self).get_form_kwargs()
        return kwargs

    def form_valid(self, form):
        self.success_url = reverse('assignment-detail', kwargs={'pk': form.instance.assignment.assignment_id})
        return super(CriterionUpdateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(CriterionUpdateView, self).get_context_data(**kwargs)
        context['edit'] = True
        return context

###
#   ScoreLevel
###

class ScoreLevelCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = "ysnp.add_scorelevel"
    raise_exception = True
    model = ScoreLevel
    template_name = 'scorelevel_create.html'
    form_class = forms.ScoreLevelForm
    success_url = '.'

    def get_form_kwargs(self):
        kwargs = super(ScoreLevelCreateView, self).get_form_kwargs()
        return kwargs

    def form_valid(self, form):
        form.instance.assignment = Assignment.objects.get(assignment_id=self.kwargs.get('assignment_id'))
        self.success_url = reverse('assignment-detail', kwargs={'pk': self.kwargs.get('assignment_id')})
        return super(ScoreLevelCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(ScoreLevelCreateView, self).get_context_data(**kwargs)
        context['edit'] = False
        return context

class ScoreLevelUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = "ysnp.change_scorelevel"
    raise_exception = True
    model = ScoreLevel
    template_name = 'scorelevel_create.html'
    form_class = forms.ScoreLevelForm
    success_url = '.'

    def get_form_kwargs(self):
        kwargs = super(ScoreLevelUpdateView, self).get_form_kwargs()
        return kwargs

    def form_valid(self, form):
        self.success_url = reverse('assignment-detail', kwargs={'pk': form.instance.assignment.assignment_id})
        return super(ScoreLevelUpdateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(ScoreLevelUpdateView, self).get_context_data(**kwargs)
        context['edit'] = True
        return context

###
#   Miscellaneous
###

class ProfileView(LoginRequiredMixin, TemplateView):
    model = User
    template_name = 'profile.html'

class PasswordSuccessView(LoginRequiredMixin, TemplateView):
    template_name = 'passwordChangeSuccess.html'
     