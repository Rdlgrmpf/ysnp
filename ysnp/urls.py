from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.views import login, logout, password_change
from django.shortcuts import render_to_response

from .views import Home, CourseListView, CourseDetailView, AssessmentListView, AssessmentDetailView, AssignmentListView, AssignmentDetailView, ProfileView, PasswordSuccessView

admin.autodiscover()

urlpatterns = patterns('',
	url(r'^$', Home.as_view(), name='home'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/$', login, {'template_name': 'login.html'}, name='user-login'),
    url(r'^logout/$', logout, {'template_name': 'logout.html'}, name='user-logout'),
    url(r'^courses/$', CourseListView.as_view(), name='course-list'),
    url(r'^courses/(?P<pk>[0-9]+)/$',CourseDetailView.as_view(), name='course-detail'),
    url(r'^assessments/$', AssessmentListView.as_view(), name='assessment-list'),
    url(r'^assessments/(?P<pk>[0-9]+)/$',AssessmentDetailView.as_view(), name='assessment-detail'),
    url(r'^assignments/$', AssignmentListView.as_view(), name='assignment-list'),
    url(r'^assignments/(?P<pk>[0-9]+)/$',AssignmentDetailView.as_view(), name='assignment-detail'),
    url(r'^profile/$', ProfileView.as_view(), name='user-profile'),
    url(r'^profile/password/change/$',password_change, {'template_name': 'passwordChange.html', 'post_change_redirect' : '/profile/password/change/successful'}, name='user-change-password'),
    url(r'^profile/password/change/successful/$', PasswordSuccessView.as_view()),
    url(r'^profile/password/',include('password_reset.urls')),
)
