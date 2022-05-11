from typing import final
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
from .models import ExcelFileUpload, Subject, Class, Attendence, ClassAttendence, SubjectAttendence
from django_email_verification import send_email
from datetime import datetime
import pandas as pd
import glob
import os
import re
from home import settings
import numpy as np

from django.db.models import Count
regexteacher = r'\b[A-Za-z._%+-]+@jcboseust.ac.in'

regexstudent = r'\b[0-9._%+-]+@jcboseust.ac.in'
def home(request):
    return render(request,'home.html')





def addattendencesuccessfully(request):
    if(request.method == 'POST'):
        classnam = request.POST.get('clas')
        subjectnam = request.POST.get('subject')
        date = request.POST.get('date')

        df = request.POST.get('data')
        

        list_of_files = glob.glob('static/excel/*.csv')
        latest_file = max(list_of_files, key=os.path.getctime)
        excelfile = ExcelFileUpload.objects.all()
        
        df = pd.read_csv(f"{latest_file}")
        df = df.values.tolist()
        finallist = []
        for i in df:

            try:
                if int(i[0][:11]):
                    finallist.append(i)

            except:
                pass
        
        classname=Class.objects.filter(classname=classnam).first()
        subjectname=Subject.objects.filter(subjectname=subjectnam).first()
        
        ClassAttendence(classname=classname,subjectname=subjectname,date=date,uploaded_by = request.user, students_present= len(finallist)).save()
        for i in range(len(finallist)):
            
                nam=finallist[i][0][12:]
                rol=int(finallist[i][0][:11])
                #  will find object for the student in specific subject
                subject_att = SubjectAttendence.objects.filter(studentroll = rol).filter(subjectname = subjectname).first()
                if(subject_att):
                   subject_att.att_count +=1
                   subject_att.save()
                #     updating the att count
                else:
                    #  creating attendence
                    SubjectAttendence(studentroll = rol, classname= classname, subjectname= subjectname, att_count = 1).save()

                Attendence(name= nam,rollno=rol,classname=classname,subjectname=subjectname,date=date).save()
            
            
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
                user.is_active = False
                user.username = email
                user.save()
                user.groups.add(teacher_group)
                
                messages.success(request,'Congratulations!! You are registered successfully as a Teacher, Your Username is Your Email')
            elif ( re.fullmatch(regexstudent, email)):
                user.username = email[:11]
                user.is_active = False
                user.save()
                messages.success(request,'Congratulations!! You are registered successfully as a Student , Your Username is your roll Number')
            else :
                
                messages.warning(request,'Oops, Your Email dont seems to be a University Email !')
                return render(request,'customerregistration.html',{'form':form})
            
            
            
            
            
            send_email(user)
        return render(request,'customerregistration.html',{'form':form})

def ImportExport(request):
    if (request.method == 'GET'):
        return redirect('/addattendence')
    if(request.method == 'POST'):
        
        excel_file = ExcelFileUpload.objects.create(file = request.FILES["excel"])
        df = pd.read_csv(f"{excel_file.file}")
        classname = request.POST.get('class')
        subjectname = request.POST.get('subject')
        date = request.POST.get('date')
        
    
        
        df = df.values.tolist()
        finallist = []
        for i in df:

            try:
                if int(i[0][:11]):
                    finallist.append(i)

            except:
                pass
        

        return render(request,'attendence.html',{'classname':classname, 'subjectname':subjectname,'date':date,'df' : finallist})

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
    subjects = Subject.objects.filter(teacher = request.user)
    classes = Class.objects.all()
    date = datetime.now().date()
    return render(request,'addattendence.html',{'classes': classes,'curr_date':date,'subjects': subjects})


def DetailedStudentDashboard(request):
    subjects = Subject.objects.all()
    attendence = Attendence.objects.filter(rollno = int(request.user.username))
    if request.method == 'POST' :
        startdate = request.POST.get('startdate')
        enddate = request.POST.get('enddate')
        attendence = Attendence.objects.filter(rollno = int(request.user.username)).filter(date__range=[startdate, enddate])
    
    
    return render(request, 'StudentDashboard.html', {'subjects': subjects,'attendence': attendence})

def StudentDashboard(request):
    studentattendence = SubjectAttendence.objects.filter(studentroll = int(request.user.username))
    for attendence in studentattendence:
        attendence.total_count = ClassAttendence.objects.filter(subjectname = attendence.subjectname).count()
    print(studentattendence)
    pass

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
        Subject.objects.create(subjectname=subjectname, classname = class_name,teacher = request.user)
        return redirect('/addattendence')

def AddDeleteClass(request):
    if request.method == 'GET':
        return render(request, 'addClass.html')
    if request.method == 'POST':
        
        classname = request.POST.get('classname')
        
        Class.objects.create(classname = classname)

        return redirect('/addattendence')
    
def ExportExcel(request):
    if request.method == 'GET':
        subjects = Subject.objects.filter(teacher = request.user)
        classes = Class.objects.all()
        return render(request,'exportexcel.html',{'classes': classes,'subjects': subjects})


    if request.method == 'POST':
        subjectname = request.POST.get('subject')
        classname = request.POST.get('class')
        class_name = Class.objects.filter(classname = classname).first()
        subject_name = Subject.objects.filter(subjectname = subjectname).first()
        startdate = request.POST.get('startdate')
        enddate = request.POST.get('enddate')
        # print(subject_name, class_name, startdate, enddate)
        if startdate and enddate:
            attendence = Attendence.objects.filter(classname=class_name ).filter(subjectname = subject_name).filter(date__range=[startdate, enddate])
        else:
            attendence = Attendence.objects.filter(classname=class_name ).filter(subjectname = subject_name)
        result = (attendence
        .values('rollno')
        .annotate(dcount=Count('rollno'))
        .order_by()
        )
        rollno_list = []
        total_attendence = []
        attendence_percentage = []
        for student in result:
            rollno_list.append(student['rollno'])
            total_attendence.append(student['dcount'])
        if startdate and enddate :
            totalattcount = ClassAttendence.objects.filter(classname = class_name).filter(subjectname = subject_name).filter(date__range=[startdate, enddate]).count()
        else:
            totalattcount = ClassAttendence.objects.filter(classname = class_name).filter(subjectname = subject_name).count()
        for count in total_attendence:
            attendence_percentage.append(int((count/totalattcount)*100))
        # dictionary of lists
        dict = {'Roll Number': rollno_list, 'Total Attendence': total_attendence, '%': attendence_percentage}

        df = pd.DataFrame(dict)

        # saving the dataframe
        file_name="Att_"+str(classname)+"_"+str(datetime.now().date())+".csv"
        df.to_csv(file_name)
        return redirect('/export')
    