from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.views import login, logout, password_change
from django.shortcuts import render_to_response

from .views import Home, CourseListView, CourseDetailView, AssessmentListView, AssessmentDetailView, AssessmentCreateView, AssessmentUpdateView, AssignmentListView, AssignmentCreateView, AssignmentUpdateView, AssignmentDetailView, CriterionDetailView, CriterionCreateView, CriterionUpdateView, ScoreLevelCreateView, ScoreLevelUpdateView, GradingView, ResultListView, ResultDetailView, ProfileView, PasswordSuccessView

admin.autodiscover()

urlpatterns = patterns('',
	url(r'^$', Home.as_view(), name='home'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/$', login, {'template_name': 'login.html'}, name='user-login'),
    url(r'^logout/$', logout, {'template_name': 'logout.html'}, name='user-logout'),
    url(r'^courses/$', CourseListView.as_view(), name='course-list'),
    url(r'^courses/(?P<pk>[0-9]+)/$',CourseDetailView.as_view(), name='course-detail'),
    url(r'^assessments/$', AssessmentListView.as_view(), name='assessment-list'),
    url(r'^assessments/add/$', AssessmentCreateView.as_view(), name='assessment-create'),
    url(r'^assessments/(?P<pk>[0-9]+)/$',AssessmentDetailView.as_view(), name='assessment-detail'),
    url(r'^assessments/(?P<pk>[0-9]+)/edit$',AssessmentUpdateView.as_view(), name='assessment-update'),
    url(r'^assignments/$', AssignmentListView.as_view(), name='assignment-list'),
    url(r'^assignments/(?P<assessment_id>[0-9]+)/add/$', AssignmentCreateView.as_view(), name='assignment-create'),
    url(r'^assignments/(?P<pk>[0-9]+)/$',AssignmentDetailView.as_view(), name='assignment-detail'),
    url(r'^assignments/(?P<pk>[0-9]+)/edit$',AssignmentUpdateView.as_view(), name='assignment-update'),
    url(r'^criteria/(?P<pk>[0-9]+)/$', CriterionDetailView.as_view(), name='criterion-detail'),
    url(r'^criteria/(?P<assignment_id>[0-9]+)/add/$', CriterionCreateView.as_view(), name='criterion-create'),
    url(r'^criteria/(?P<pk>[0-9]+)/edit/$', CriterionUpdateView.as_view(), name='criterion-update'),
    url(r'^scorelevel/(?P<assignment_id>[0-9]+)/add/$', ScoreLevelCreateView.as_view(), name='scorelevel-create'),
    url(r'^scorelevel/(?P<pk>[0-9]+)/edit/$', ScoreLevelUpdateView.as_view(), name='scorelevel-update'),
    url(r'^grading/(?P<assignment_id>[0-9]+)/(?P<student_id>[0-9]+)/$', GradingView.as_view(), name='grading'),
    url(r'^results/$', ResultListView.as_view(), name='result-list'),
    url(r'^results/(?P<assignment_id>[0-9]+)/$', ResultDetailView.as_view(), name='result-detail'),
    url(r'^profile/$', ProfileView.as_view(), name='user-profile'),
    url(r'^profile/password/change/$',password_change, {'template_name': 'passwordChange.html', 'post_change_redirect' : '/profile/password/change/successful'}, name='user-change-password'),
    url(r'^profile/password/change/successful/$', PasswordSuccessView.as_view()),
    url(r'^profile/password/',include('password_reset.urls')),
)
