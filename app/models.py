from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator,MinValueValidator
from home import settings
import os
# Create your models here.
class ExcelFileUpload(models.Model):
    file = models.FileField( upload_to= f"{settings.BASE_DIR}/static/excel", max_length=100)
    def delete(self, *args, **kwargs):
        os.remove(os.path.join(settings.STATICFILES_DIRS[0], self.file.name))
        super(ExcelFileUpload,self).delete(*args,**kwargs)
class Class(models.Model):
    classname = models.CharField(max_length=20)

    def __str__(self):
        return (self.classname) 

class Subject(models.Model):
    subjectname = models.CharField(max_length=20)
    classname = models.ForeignKey(Class,on_delete=models.CASCADE)

    def __str__(self):
        return (self.subjectname) 

class Attendence(models.Model):
    name = models.CharField(max_length=20)
    rollno = models.IntegerField()
    classname = models.ForeignKey(Class,on_delete=models.CASCADE)
    subjectname = models.ForeignKey(Subject,on_delete=models.CASCADE)
    date = models.DateTimeField()
    def __str__(self):
        return (self.name)
    
class ClassAttendence(models.Model):
    classname = models.ForeignKey(Class,on_delete=models.CASCADE)
    subjectname = models.ForeignKey(Subject,on_delete=models.CASCADE)
    date = models.DateTimeField()
    uploaded_by = models.ForeignKey(User,on_delete=models.CASCADE,null= True)
    students_present = models.IntegerField(default=0)
    

# class Student(models.Model):
#     name = models.CharField(max_length=20)
#     rollno = models.IntegerField()
#     classname = models.CharField(max_length=20,default='ce52')
#     automata=models.IntegerField(default=0)
#     signalandsystem=models.IntegerField(default=0)
#     bio=models.IntegerField(default=0)
#     vac=models.IntegerField(default=0)
#     dbmssubject=models.IntegerField(default=0)
#     dbmslab=models.IntegerField(default=0)
#     oopssubject=models.IntegerField(default=0)
#     oopslab=models.IntegerField(default=0)
#     ml=models.IntegerField(default=0)
    


#     def __str__(self):
#         return (self.id)