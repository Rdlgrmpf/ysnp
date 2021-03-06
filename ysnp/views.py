from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.template import RequestContext, Template
from django.views.generic import DetailView, ListView, TemplateView, CreateView, UpdateView, FormView
from braces.views import LoginRequiredMixin, PermissionRequiredMixin, GroupRequiredMixin
from itertools import chain
from ysnp.models import Assessment, Assignment, Course, Profile, Student_Course, Criterion, ScoreLevel, Criterion_Score
from ysnp import forms
from django.core.urlresolvers import reverse
from utils import Utils
import math
from collections import defaultdict

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
                
            assessments = context['assessments'] = Assessment.objects.filter(course=self.object)

            for assessment in assessments:
                assignments = Assignment.objects.filter(assessment=assessment)

                result = []
                weight = []

                if self.request.user.profile.is_student():
                    for assignment in assignments:
                        if assignment.is_assessed_for_student(self.request.user.profile):
                                                     
                            #get all criteria associated with this assignment
                            criteria = Criterion.objects.filter(assignment=assignment)
                            #get all scorelevels associated with this assignment
                            scoreLevels = ScoreLevel.objects.filter(assignment=assignment).order_by('level')
                            #get the matching grades, for attributes see models/Criterion_Score
                            scoreToCriterion = Criterion_Score.objects.filter(criterion=criteria, score_level=scoreLevels, student=self.request.user.profile)

            
                            totalSum = 0.0
                            crits = defaultdict(list)
                            for level in scoreLevels:
                                criterionScore = Criterion_Score.objects.filter(score_level=level.score_level_id, student=self.request.user.profile).order_by('score_level')
                                level.sum = 0.0
                                for score in criterionScore:
                                    crits[score.criterion_id].append(score.number)
                                    level.sum += score.number
                                totalSum += level.sum
        
                    
                            levelPercentages = []
                            for level in scoreLevels:
                                levelPercentages.append(level.sum /totalSum)
                                level.percentage = round(level.sum /totalSum, 2) * 100
                                
                            for criterion in criteria:
                                criterion.res = crits[criterion.criterion_id]
                                
                            assignment.result = round(Utils.profileToScore(self, levelPercentages, assignment.tolerance), 2)
                            result.append(round(Utils.profileToScore(self, levelPercentages, assignment.tolerance), 2))
                            weight.append(assignment.weight)
                            
                            if result.count('-') == 0:
                                assessment.grade = round(Utils.scoreToGrade(self, Utils.scoreToScore(self, result, weight, assessment.lenience)),2)
                            else:
                                assessment.grade = '-'
                            
                        else:
                            assignment.result = '-'
                            result.append('-') 


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
            
            assignments = Assignment.objects.filter(assessment=self.object)

            result = []
            weight = []

            if self.request.user.profile.is_student():
                for assignment in assignments:
                    if assignment.is_assessed_for_student(self.request.user.profile):
                                                 
                        #get all criteria associated with this assignment
                        criteria = Criterion.objects.filter(assignment=assignment)
                        #get all scorelevels associated with this assignment
                        scoreLevels = ScoreLevel.objects.filter(assignment=assignment).order_by('level')
                        #get the matching grades, for attributes see models/Criterion_Score
                        scoreToCriterion = Criterion_Score.objects.filter(criterion=criteria, score_level=scoreLevels, student=self.request.user.profile)

        
                        totalSum = 0.0
                        crits = defaultdict(list)
                        for level in scoreLevels:
                            criterionScore = Criterion_Score.objects.filter(score_level=level.score_level_id, student=self.request.user.profile).order_by('score_level')
                            level.sum = 0.0
                            for score in criterionScore:
                                crits[score.criterion_id].append(score.number)
                                level.sum += score.number
                            totalSum += level.sum
    
                
                        levelPercentages = []
                        for level in scoreLevels:
                            levelPercentages.append(level.sum /totalSum)
                            level.percentage = round(level.sum /totalSum, 2) * 100
                            
                        for criterion in criteria:
                            criterion.res = crits[criterion.criterion_id]
                            
                        assignment.result = round(Utils.profileToScore(self, levelPercentages, assignment.tolerance), 2)
                        result.append(round(Utils.profileToScore(self, levelPercentages, assignment.tolerance), 2))
                        weight.append(assignment.weight)
                        
                        if result.count('-') == 0:
                            context['grade'] = round(Utils.scoreToGrade(self, Utils.scoreToScore(self, result, weight, self.object.lenience)),2)
                        else:
                            context['grade'] = '-'
                        
                    else:
                        assignment.result = '-'
                        result.append('-') 
                        
        
        context['assignments'] = assignments           
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
            context['students'] = Profile.occupation.get_students().filter(student_course__course=self.object.assessment.course)
            context['is_this_lecturer'] = (self.request.user.profile == self.object.assessment.course.lecturer)
            context['is_this_assessor'] = (self.request.user.profile == self.object.assessment.assessor)
            context['is_assessed'] = self.object.is_assessed_for_student(self.request.user.profile)
        return context

class AssignmentCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = "ysnp.add_assignment"
    raise_exception = True
    model = Assignment
    template_name = 'assignment_create.html'
    form_class = forms.AssignmentForm
    success_url = '.'

    def form_valid(self, form):
        form.instance.assessment = Assessment.objects.get(assessment_id=self.kwargs.get('assessment_id'))
        self.success_url = reverse('assessment-detail', kwargs={'pk': self.kwargs.get('assessment_id')})
        return super(AssignmentCreateView, self).form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(AssignmentCreateView, self).get_form_kwargs()
        #kwargs['possible_assessments'] = Assessment.objects.filter(course__lecturer=self.request.user.profile)
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
    success_url = '.'

    def form_valid(self, form):
        self.success_url = reverse('assessment-detail', kwargs={'pk': form.instance.assessment.assessment_id})
        return super(AssignmentUpdateView, self).form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(AssignmentUpdateView, self).get_form_kwargs()
        #kwargs['possible_assessments'] = Assessment.objects.filter(course__lecturer=self.request.user.profile)
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
#   Assessing
###
class GradingView(LoginRequiredMixin, FormView):
    template_name = 'grading.html'
    form_class = forms.GradingForm
    success_url = '.'

    def get_form_kwargs(self):
        kwargs = super(GradingView, self).get_form_kwargs()
        ass = Assignment.objects.get(assignment_id=self.kwargs.get('assignment_id'))
        student = Profile.occupation.get_students().get(profile_id=self.kwargs.get('student_id'))
        kwargs['scorelevels'] = ScoreLevel.objects.filter(assignment=ass).order_by('level')
        kwargs['criteria'] = Criterion.objects.filter(assignment=ass)
        kwargs['has_old_values'] = ass.is_assessed_for_student(student)
        kwargs['old_values'] = []
        if kwargs['has_old_values']:
            for index, item in enumerate(kwargs['criteria']):
                for index2, item2 in enumerate(kwargs['scorelevels']):
                    kwargs['old_values'].append(Criterion_Score.objects.get(criterion=item, score_level=item2, student=student).number)

        return kwargs

    def form_valid(self, form):
        #get student
        student = Profile.occupation.get_students().get(profile_id=self.kwargs.get('student_id'))
        #if already assessed, update
        if Assignment.objects.get(assignment_id=self.kwargs.get('assignment_id')).is_assessed_for_student(student):
            for index, item in enumerate(form.criteria):
                for index2, item2 in enumerate(form.scorelevels):
                    value = form.cleaned_data['custom_{0}_{1}'.format(index, index2)]
                    cs = Criterion_Score.objects.get(criterion=item, score_level=item2, student=student)
                    cs.number = value
                    cs.save()
        else:
            for index, item in enumerate(form.criteria):
                for index2, item2 in enumerate(form.scorelevels):
                    value = form.cleaned_data['custom_{0}_{1}'.format(index, index2)]
                    s = Criterion_Score(criterion=item, score_level=item2, student=student, number=value)
                    s.save()
        #send email to student and lecturer?
        self.success_url = reverse('assignment-detail', kwargs={'pk': self.kwargs.get('assignment_id')})
        return super(GradingView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(GradingView, self).get_context_data(**kwargs)
        context['assignment'] = Assignment.objects.get(assignment_id=self.kwargs.get('assignment_id'))
        context['allowed'] = (self.request.user.profile == context['assignment'].assessment.assessor)
        if context['allowed']:
            context['student'] = Profile.occupation.get_students().get(profile_id=self.kwargs.get('student_id'))
            context['scorelevels'] = ScoreLevel.objects.filter(assignment=context['assignment']).order_by('level')
            context['criterion'] = Criterion.objects.filter(assignment=context['assignment'])
            context['edit'] = True #anpassen
        return context

class ResultListView(LoginRequiredMixin, GroupRequiredMixin, TemplateView):
    template_name = 'result_list.html'
    group_required = u'Student'

    def get_context_data(self, **kwargs):
        context = super(ResultListView, self).get_context_data(**kwargs)
        result = []
        for assignment in Assignment.objects.filter(assessment__course__student_course__student=self.request.user.profile):
            if assignment.is_assessed_for_student(self.request.user.profile):
                result.append(assignment)
        context['assignments']  = result
        return context

class ResultDetailView(LoginRequiredMixin, GroupRequiredMixin, TemplateView):
    template_name = 'result_detail.html'
    group_required = u'Student'

    def get_context_data(self, **kwargs):
        context = super(ResultDetailView, self).get_context_data(**kwargs)
        #get the student from logindata
        student = self.request.user.profile
        #get the assignment he/she wants details for
        assignment = Assignment.objects.filter(assessment__course__student_course__student=student).get(assignment_id=self.kwargs.get('assignment_id'))
        #get all criteria associated with this assignment
        criteria = Criterion.objects.filter(assignment=assignment)
        #get all scorelevels associated with this assignment
        scoreLevels = ScoreLevel.objects.filter(assignment=assignment).order_by('level')
        #get the matching grades, for attributes see models/Criterion_Score
        scoreToCriterion = Criterion_Score.objects.filter(criterion=criteria, score_level=scoreLevels, student=student)

        if assignment.is_assessed_for_student(self.request.user.profile):
            totalSum = 0.0
            crits = defaultdict(list)
            for level in scoreLevels:
                criterionScore = Criterion_Score.objects.filter(score_level=level.score_level_id, student=student).order_by('score_level')
                level.sum = 0.0
                for score in criterionScore:
                    crits[score.criterion_id].append(score.number)
                    level.sum += score.number
                totalSum += level.sum
    
                
            levelPercentages = []
            for level in scoreLevels:
                levelPercentages.append(level.sum /totalSum)
                level.percentage = round(level.sum /totalSum, 2) * 100
                
            for criterion in criteria:
                criterion.res = crits[criterion.criterion_id]

        
            #make everything from above available in the template
            context['is_assessed'] = True
            context['assignment'] = assignment
            context['criteria'] = criteria
            context['crits'] = crits
            context['scoreLevels'] = scoreLevels
            context['result'] = round(Utils.profileToScore(self, levelPercentages, assignment.tolerance), 2)
        else:
            context['is_assessed'] = False
        return context

###
#   Miscellaneous
###

class ProfileView(LoginRequiredMixin, TemplateView):
    model = User
    template_name = 'profile.html'

class PasswordSuccessView(LoginRequiredMixin, TemplateView):
    template_name = 'passwordChangeSuccess.html'
     