from django import forms
from ysnp import models

class AssessmentForm(forms.ModelForm):
    name = forms.CharField(max_length=100)
    assessor = forms.ModelChoiceField(queryset=models.Profile.occupation.get_assessors())

    def __init__(self, possible_courses, *args, **kwargs):
        super (AssessmentForm, self).__init__(*args, **kwargs)
        self.fields['course'].queryset = possible_courses

    class Meta:
    	model = models.Assessment

class AssignmentForm(forms.ModelForm):
    name = forms.CharField(max_length=100)
    '''
    def __init__(self, possible_assessments, *args, **kwargs):
        super (AssignmentForm, self).__init__(*args, **kwargs)
        self.fields['assessment'].queryset = possible_assessments
    '''
    class Meta:
        model = models.Assignment
        exclude = ('assessment',)

class CriterionForm(forms.ModelForm):
    name = forms.CharField(max_length=100)

    class Meta:
        model = models.Criterion
        exclude = ('assignment',)

class ScoreLevelForm(forms.ModelForm):

	class Meta:
		model = models.ScoreLevel
		exclude = ('assignment',)

class GradingForm(forms.Form):
    scorelevels = None
    criteria = None
    outer_list = []

    def __init__(self, scorelevels, criteria, has_old_values, old_values, *args, **kwargs):
        super (GradingForm, self).__init__(*args, **kwargs)
        self.outer_list = []
        self.scorelevels = scorelevels
        self.criteria = criteria
        if has_old_values:
            for index, item in enumerate(criteria):
                inner_list = []
                for index2, item2 in enumerate(scorelevels):
                    field = forms.IntegerField(label=item.name)
                    self.fields['custom_{0}_{1}'.format(index, index2)] = field
                    self.fields['custom_{0}_{1}'.format(index, index2)].initial = old_values.pop(0)
                    inner_list.append(forms.forms.BoundField(self, self.fields['custom_{0}_{1}'.format(index, index2)], 'custom_{0}_{1}'.format(index, index2)))
                self.outer_list.append(inner_list)
        else:
            for index, item in enumerate(criteria):
                inner_list = []
                for index2, item2 in enumerate(scorelevels):
                    field = forms.IntegerField(label=item.name)
                    self.fields['custom_{0}_{1}'.format(index, index2)] = field
                    inner_list.append(forms.forms.BoundField(self, self.fields['custom_{0}_{1}'.format(index, index2)], 'custom_{0}_{1}'.format(index, index2)))
                self.outer_list.append(inner_list)