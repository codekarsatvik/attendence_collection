from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.db.models.query_utils import Q
from django.http.response import JsonResponse
from django.shortcuts import redirect, render
from django.urls.resolvers import RegexPattern
from django.utils import regex_helper
from django.views import View
from .forms import  CustomerRegistrationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User,Group
from .models import ExcelFileUpload,Subject,Class,Attendence,ClassAttendence
from django_email_verification import send_email
from datetime import datetime
import pandas as pd
import glob
import os
import re
from home import settings
import numpy as np


regexteacher = r'\b[A-Za-z._%+-]+@jcboseust.ac.in'

regexstudent = r'\b[0-9._%+-]+@jcboseust.ac.in'
def home(request):
    return render(request,'home.html')





def addattendencesuccessfully(request):
    if(request.method == 'POST'):
        classnam = request.POST.get('clas')
        subjectnam = request.POST.get('subject')
        df = request.POST.get('data')
        
        list_of_files = glob.glob('static/excel/*.csv')
        latest_file = max(list_of_files, key=os.path.getctime)
        excelfile = ExcelFileUpload.objects.all()
        
        df = pd.read_csv(f"{latest_file}")
        data=df.values.tolist()
        classname=Class.objects.filter(classname=classnam).first()
        subjectname=Subject.objects.filter(subjectname=subjectnam).first()
        ClassAttendence(classname=classname,subjectname=subjectname,date=datetime.now().date(),uploaded_by = request.user, students_present= len(data)).save()
        for i in range(len(data)):
            nam=data[i][0][12:]
            rol=int(data[i][0][:11])
            Attendence(name= nam,rollno=rol,classname=classname,subjectname=subjectname,date=datetime.now().date()).save()
        for document in excelfile:
            document.delete()
        return redirect('/teacher/dashboard')


class CustomerRegistrationView(View):
    def get(self,request):
        form=CustomerRegistrationForm()
        return render(request,'customerregistration.html',{'form':form})
    def post(self,request):
        form=CustomerRegistrationForm(request.POST)
        if form.is_valid():
            
            # form.save()
            user = form.save( commit= False)
            email=form.cleaned_data['email']
            if(re.fullmatch(regexteacher, email)):
                teacher_group = Group.objects.get(name='teachers') 
                teacher_group.user_set.add(user)
                user.username = email
                messages.success(request,'Congratulations!! You are registered successfully as a Teacher, Your Username is Your Email')
            elif ( re.fullmatch(regexstudent, email)):
                user.username = email[:11]
                messages.success(request,'Congratulations!! You are registered successfully as a Student , Your Username is your roll Number')
            else :
                
                messages.warning(request,'Oops, Your Email dont seems to be a University Email !')
                return render(request,'customerregistration.html',{'form':form})
            
            user.is_active = False
            user.save()
            
            
            
            send_email(user)
        return render(request,'customerregistration.html',{'form':form})

def ImportExport(request):
    if (request.method == 'GET'):
        list_of_files = glob.glob('static/excel/*.csv')
         # * means all if need specific format then *.csv
        latest_file = max(list_of_files, key=os.path.getctime)
        print(latest_file)
        df = pd.read_csv(f"{latest_file}")
        
        return render(request,'attendence.html',{'df' : df.values.tolist()})
    if(request.method == 'POST'):
        
        excel_file = ExcelFileUpload.objects.create(file = request.FILES["excel"])
        df = pd.read_csv(f"{excel_file.file}")
        classname = request.POST.get('class')
        subjectname = request.POST.get('subject')
        return render(request,'attendence.html',{'classname':classname, 'subjectname':subjectname,'df' : df.values.tolist()})

def TeacherDashboard(request):
    classes = Class.objects.all()
    attendence = ClassAttendence.objects.filter(uploaded_by = request.user).reverse()

    if request.method == 'POST' :
        startdate = request.POST.get('startdate')
        enddate = request.POST.get('enddate')
        attendence = ClassAttendence.objects.filter(uploaded_by = request.user).filter(date__range=[startdate, enddate])
    return render(request,'teacherDashboard.html', {'attendence':attendence,'classes' : classes})


def filter(request):  
    class_name = Class.objects.filter(classname = request.GET.get('classname')).first()
    attendence = ClassAttendence.objects.filter(uploaded_by = request.user).filter(classname = class_name).order_by('date')
    classes = Class.objects.all()
    return render(request,'teacherDashboard.html', {'attendence':attendence,'classes' : classes})


def attendencepage(request):
    subjects = Subject.objects.all()
    classes = Class.objects.all()
    return render(request,'addattendence.html',{'classes': classes,'subjects': subjects})


def StudentDashboard(request):
    subjects = Subject.objects.all()
    attendence = Attendence.objects.filter(rollno = int(request.user.username))
    if request.method == 'POST' :
        startdate = request.POST.get('startdate')
        enddate = request.POST.get('enddate')
        attendence = Attendence.objects.filter(rollno = int(request.user.username)).filter(date__range=[startdate, enddate])
    
    
    return render(request, 'StudentDashboard.html', {'subjects': subjects,'attendence': attendence})


def SubjectFilter(request):  
    subject_name = Subject.objects.filter(subjectname = request.GET.get('subjectname')).first()
    attendence =Attendence.objects.filter(rollno = int(request.user.username)).filter(subjectname =subject_name).order_by('date')
    subjects = Subject.objects.all()
    return render(request,'StudentDashboard.html', {'attendence':attendence,'subjects' : subjects})


def AddDeleteSubject(request):
    if request.method == 'GET':
        classes = Class.objects.all()
        return render(request, 'addSubject.html',{'classes':classes})
    if request.method == 'POST':
        subjectname = request.POST.get('subjectname')
        classname = request.POST.get('classname')
        class_name = Class.objects.filter(classname=classname).first()
        Subject.objects.create(subjectname=subjectname, classname = class_name)
        return redirect('/addattendence')

def AddDeleteClass(request):
    if request.method == 'GET':
        return render(request, 'addClass.html')
    if request.method == 'POST':
        
        classname = request.POST.get('classname')
        
        Class.objects.create(classname = classname)

        return redirect('/addattendence')
    
    