from django.contrib import admin
from django.contrib.auth.forms import AuthenticationForm
from django.urls import path,include
from app import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import authenticate, views as auth_views
from .forms import LoginForm, MyPasswordChangeForm, MyPasswwordResetForm,MySetPasswordForm

urlpatterns = [
    path('', views.home ,name = "home"),
    path('registration/',views.CustomerRegistrationView.as_view(),name='customerregistration'),
    path('accounts/login/',auth_views.LoginView.as_view(template_name='login.html',authentication_form=LoginForm),name='login'),
    path('logout/',auth_views.LogoutView.as_view(),name='logout'),
    
    path('passwordchange/',auth_views.PasswordChangeView.as_view(template_name='passwordchange.html',form_class=MyPasswordChangeForm,success_url='/passwordchangedone/'),name='passwordchange'),
    path('passwordchangedone/',auth_views.PasswordChangeDoneView.as_view(template_name='passwordchangedone.html'),name='passwordchangedone'),
    path('password-reset/',auth_views.PasswordResetView.as_view(template_name='password_reset.html',form_class=MyPasswwordResetForm),name='password_reset'),

    path('password-reset/done/',auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'),name='password_reset_done'),

    path('password-reset-confirm/<uidb64>/<token>',auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html',form_class=MySetPasswordForm),name='password_reset_confirm'),

    path('password-reset-complete/',auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'),name='password_reset_complete'),

    path('excel/',views.ImportExport,name="import_export"),
    path('addattendence/',views.attendencepage,name="attendencepage"),
    path('addattendencesuccessfully/',views.addattendencesuccessfully,name="addattendencesuccessfully"),
    # path('filter/',views.Filter,name="filter"),
    # path('filteredattendence/',views.Filteredattendence,name="filteredattendence")
    path('teacher/dashboard/' , views.TeacherDashboard,name="teacher-dashboard"),
    path('classfilter/',views.filter, name="classfilter"),
    path('student/dashboard/',views.StudentDashboard,name="student-dashboard"),
    path('subjectfilter/' ,views.SubjectFilter, name="subjectfilter"),
    path('addclass/',views.AddDeleteClass, name="addclass"),
    path('addsubject/',views.AddDeleteSubject , name="addsubject"),
]