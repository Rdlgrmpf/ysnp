from django.db import models
from django.contrib.auth.models import User

class Student(models.Model):
	matrikelNr = models.AutoField(primary_key = True)
	user = models.OneToOneField(User)
	birthday = models.DateField()
	gender = models.TextField()
	street = models.TextField()
	postalCode = models.IntegerField()

	def __unicode__(self):
		return str(self.matrikelNr) + ' ' + self.user.first_name + ' ' + self.user.last_name

	class Meta:
		db_table = 'Student'

class Employee(models.Model):
	employeeId = models.AutoField(primary_key = True)
	user = models.OneToOneField(User)
	birthday = models.DateField()
	street = models.TextField()
	postalCode = models.IntegerField()
	jobFunction = models.IntegerField()

	def __unicode__(self):
		return str(self.employeeId) + ' ' + self.user.first_name + ' ' + self.user.last_name

	class Meta:
		db_table = 'Employee'

class Course(models.Model):
	courseId = models.AutoField(primary_key = True)
	name = models.TextField()
	lecturer = models.ForeignKey(Employee)

	def __unicode__(self):
		return str(self.courseId) + ' ' + self.name + ' by ' + self.lecturer.user.first_name + ' ' + self.lecturer.user.last_name

	class Meta:
		db_table = 'Course'

class Assessment(models.Model):
	assessmentId = models.AutoField(primary_key = True)
	name = models.TextField()
	course = models.ForeignKey(Course)
	assessor = models.ForeignKey(Employee)

	def __unicode__(self):
		return str(self.assessmentId) + ' ' + self.name + ' in ' + self.course +  ' graded by ' + self.assessor

	class Meta:
		db_table = 'Assessment'

class Assignment(models.Model):
	assignmentId = models.AutoField(primary_key = True)
	name = models.TextField()
	tolerance = models.FloatField()
	assessment = models.ForeignKey(Assessment)

	def __unicode__(self):
		return str(self.assignmentId) + ' ' + self.name + ' part of ' + self.assessment

	class Meta:
		db_table = 'Assignment'

class Student_Course(models.Model):
	matrikelNr = models.ForeignKey(Student)
	course = models.ForeignKey(Course)
	semester = models.IntegerField()

	def __unicode__(self):
		return str(self.matrikelNr) + ' ' + str(self.course) + ' ' + str(self.semester)

	class Meta:
		db_table = 'Student_Course'

class Criterion(models.Model):
	criterionId = models.AutoField(primary_key = True)
	name = models.TextField()
	assignment = models.ForeignKey(Assignment)

	def __unicode__(self):
		return str(self.criterionId) + ' ' + self.name

	class Meta:
		db_table = 'Criterion'

class ScoreLevel(models.Model):
	scoreLevelId = models.AutoField(primary_key = True)
	level = models.IntegerField()
	assignment = models.ForeignKey(Assignment)

	def __unicode__(self):
		return str(self.scoreLevelId) + ' ' + self.level

	class Meta:
		db_table = 'ScoreLevel'

class Criterion_Score(models.Model):
	criterion = models.ForeignKey(Criterion)
	scoreLevel = models.ForeignKey(ScoreLevel)
	student = models.ForeignKey(Student)
	number = models.IntegerField()

	def __unicode__(self):
		return str(self.criterion) + ' ' + str(scoreLevel) + ' ' + str(number)

	class Meta:
		db_table = 'Criterion_Score'