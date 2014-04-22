from django import forms
from ysnp import models

class AssessmentForm(forms.ModelForm):
    name = forms.CharField(max_length=100)
    course = forms.ModelChoiceField(queryset=models.Course.objects.all())
    assessor = forms.ModelChoiceField(queryset=models.Profile.occupation.get_assessors())

    def __init__(self, possible_courses, *args, **kwargs):
        super (AssessmentForm, self).__init__(*args, **kwargs)
        self.fields['course'].queryset = possible_courses

    class Meta:
    	model = models.Assessment