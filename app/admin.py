from django.contrib import admin
from .models import ExcelFileUpload,Class,Subject,Attendence,ClassAttendence

class ClassAdmin(admin.ModelAdmin):
    list_display = ['classname']
admin.site.register(Class,ClassAdmin)

class SubjectAdmin(admin.ModelAdmin):
    list_display = ['subjectname', 'classname']
admin.site.register(Subject,SubjectAdmin)

class AttendenceAdmin(admin.ModelAdmin):
    list_display = ['name', 'rollno', 'classname', 'subjectname', 'date']
admin.site.register(Attendence,AttendenceAdmin)

class ClassAttendenceAdmin(admin.ModelAdmin):
    list_display = ['classname', 'subjectname', 'date']
admin.site.register(ClassAttendence,ClassAttendenceAdmin)


admin.site.register(ExcelFileUpload)
# Register your models here.
