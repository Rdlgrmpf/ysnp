from django.contrib import admin
from ysnp.models import *
from django.contrib.auth.models import Permission


admin.site.register(Permission)

admin.site.register(Profile)
admin.site.register(Course)
admin.site.register(Student_Course)
admin.site.register(Criterion)
admin.site.register(Assessment)
admin.site.register(Assignment)
admin.site.register(ScoreLevel)
admin.site.register(Criterion_Score)
