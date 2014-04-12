from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.views import login, logout, password_reset, password_reset_done, password_reset_confirm, password_reset_complete

from .views import Home, CourseListView, CourseDetailView, AssessmentListView, AssessmentDetailView, AssignmentListView, AssignmentDetailView, ProfileView

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
    url(r'profile/$', ProfileView.as_view(), name='user-profile'),
    url(r'^profile/password/reset/$', password_reset, {'post_reset_redirect' : '/profile/password/reset/done/'}, name="password-reset"),
    url(r'^profile/password/reset/done/$',password_reset_done),
    url(r'^profile/password/reset/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',password_reset_confirm,{'post_reset_redirect' : '/profile/password/done/'}),
    url(r'^profile/password/done/$',password_reset_complete),
)
