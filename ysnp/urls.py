from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.views import login, logout

from .views import Home, ListCourseView

admin.autodiscover()

urlpatterns = patterns('',

	url(r'^$', Home.as_view(), name='home'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/$', login, {'template_name': 'login.html'}, name='user-login'),
    url(r'^logout/$', logout, {'template_name': 'logout.html'}, name='user-logout'),
    url(r'^courses/$', ListCourseView.as_view(), name='courses-list'),
    url(r'^course/(?P<course_id>\d+)/','ysnp.views.course_view', name='course-detail')
)
