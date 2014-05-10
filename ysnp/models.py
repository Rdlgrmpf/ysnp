from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

class OccupationManager(models.Manager):
    def get_students(self):
        return super(OccupationManager, self).get_queryset().filter(user__groups__name__contains='Student')

    def get_assessors(self):
        return super(OccupationManager, self).get_queryset().filter(user__groups__name__contains='Assessor')

    def get_lecturers(self):
        return super(OccupationManager, self).get_queryset().filter(user__groups__name__contains='Lecturer')

class Profile(models.Model):
    profile_id = models.AutoField(primary_key = True)
    matrikel_nr = models.IntegerField(null = True, blank = True)
    employee_id = models.IntegerField(null = True, blank = True)
    user = models.OneToOneField(User)
    birthday = models.DateField()
    gender = models.TextField()

    objects = models.Manager()
    occupation = OccupationManager()

    def is_student(self):
        return self.user.groups.filter(name='Student')

    def is_assessor(self):
        return self.user.groups.filter(name='Assessor')

    def is_lecturer(self):
        return self.user.groups.filter(name='Lecturer')

    def __unicode__(self):
        return str(self.profile_id) + ' ' + self.user.first_name + ' ' + self.user.last_name

    class Meta:
        db_table = 'Profile'

class Course(models.Model):
    course_id = models.AutoField(primary_key = True)
    name = models.TextField()
    lecturer = models.ForeignKey(Profile)

    def __unicode__(self):
        return str(self.course_id) + ' ' + self.name + ' by ' + self.lecturer.user.first_name + ' ' + self.lecturer.user.last_name

    def get_absolute_url(self):
        return reverse('course-detail', args=[str(self.course_id)])

    class Meta:
        db_table = 'Course'

class Assessment(models.Model):
    assessment_id = models.AutoField(primary_key = True)
    name = models.TextField()
    course = models.ForeignKey(Course)
    assessor = models.ForeignKey(Profile)

    def __unicode__(self):
        return str(self.assessment_id) + ' ' + self.name + ' in ' + str(self.course.name) +  ' graded by ' + self.assessor.user.first_name + ' ' + self.assessor.user.last_name

    def get_absolute_url(self):
        return reverse('assessment-detail', args=[str(self.assessment_id)])

    class Meta:
        db_table = 'Assessment'

class Assignment(models.Model):
    assignment_id = models.AutoField(primary_key = True)
    name = models.TextField()
    tolerance = models.FloatField()
    weight = models.FloatField()
    assessment = models.ForeignKey(Assessment)

    def __unicode__(self):
        return str(self.assignment_id) + ' ' + self.name + ' part of ' + str(self.assessment.name)

    def get_absolute_url(self):
        return reverse('assignment-detail', args=[str(self.assignment_id)])

    def is_assessed(self):
        students = Profile.occupation.get_students().filter(student_course__course=self.assessment.course)
        #get all criteria associated with this assignment
        criteria = Criterion.objects.filter(assignment=self)
        #get all scorelevels associated with this assignment
        scoreLevels = ScoreLevel.objects.filter(assignment=self).order_by('level')
        temp = 0
        for student in students:
            temp += self.is_assessed_for_student(student)
        return (students.count()*criteria.count()*scorelevels.count() == temp)

    def is_assessed_for_student(self, student):
        #get all criteria associated with this assignment
        criteria = Criterion.objects.filter(assignment=self)
        #get all scorelevels associated with this assignment
        scoreLevels = ScoreLevel.objects.filter(assignment=self).order_by('level')
        #get the matching grades, for attributes see models/Criterion_Score
        scoreToCriterion = Criterion_Score.objects.filter(criterion=criteria, score_level=scoreLevels, student=student)

        return (criteria.count()*scoreLevels.count() == scoreToCriterion.count())

    class Meta:
        db_table = 'Assignment'

class Student_Course(models.Model):
    student = models.ForeignKey(Profile)
    course = models.ForeignKey(Course)
    semester = models.IntegerField()

    def __unicode__(self):
        return str(self.student) + ' ' + str(self.course) + ' ' + str(self.semester)

    class Meta:
        db_table = 'Student_Course'

class Criterion(models.Model):
    criterion_id = models.AutoField(primary_key = True)
    name = models.TextField()
    assignment = models.ForeignKey(Assignment)

    def __unicode__(self):
        return str(self.criterion_id) + ' ' + self.name

    def get_absolute_url(self):
        return reverse('criterion-detail', args=[str(self.criterion_id)])

    class Meta:
        db_table = 'Criterion'

class ScoreLevel(models.Model):
    score_level_id = models.AutoField(primary_key = True)
    level = models.IntegerField()
    assignment = models.ForeignKey(Assignment)

    def __unicode__(self):
        return str(self.score_level_id) + ' ' + str(self.level)

    class Meta:
        db_table = 'ScoreLevel'

class Criterion_Score(models.Model):
    criterion = models.ForeignKey(Criterion)
    score_level = models.ForeignKey(ScoreLevel)
    student = models.ForeignKey(Profile)
    number = models.IntegerField()

    def __unicode__(self):
        return str(self.criterion.name) + ' ' + str(self.score_level.level) + ' ' + str(self.number)

    class Meta:
        db_table = 'Criterion_Score'