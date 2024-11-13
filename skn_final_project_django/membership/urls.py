from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # 로그인 URL
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),  # 회원가입 URL
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('upload_resume/', views.upload_resume_view, name='upload_resume'),  # 이력서 업로드 URL
    # 로그아웃 URL
    path('logout/', views.logout_view, name='logout'),
    path('delete_account/', views.delete_account_view, name='delete_account'),
    path('find_id/', views.find_id_view, name='find_id'),
    path('intro/', views.intro, name='intro'),
    path('main/', views.main, name='main'),
    path('terms/', views.terms_view, name='terms'),  # 이용약관 페이지 추가
    path('interview_result/', views.interview_result, name='interview_result'),
    path('upload_resume_to_fastapi/', views.upload_resume_to_fastapi, name='upload_resume_to_fastapi'),  # 이력서 업로드 URL
    path('interview_form/', views.interview_form, name='interview_form'),
    path('question/', views.question, name='question'),
    path('start_interview/', views.start_interview, name='start_interview'),
    path('delete_resume/<str:resume_id>/', views.delete_resume, name='delete_resume'),
    path('api/jobs/<str:company_id>/', views.get_jobs_by_company, name='get_jobs_by_company'),
    path('api/interview/<str:interview_id>/', views.get_interview_details, name='get_interview_details'),
]