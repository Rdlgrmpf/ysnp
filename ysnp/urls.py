from django.conf.urls import patterns, include, url

from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',

	url(r'^$', 'ysnp.views.home'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/', 'ysnp.views.user_login',  name='user_login'),
    url(r'^logout/', 'ysnp.views.user_login'),
    url(r'^courses/', 'ysnp.views.courses_view'),
)
