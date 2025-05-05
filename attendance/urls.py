from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from.views import splash_view

urlpatterns = [
    path('face_recognition/', views.face_recognition_view, name='face_recognition'),  
    path('',views.splash_view, name='splash'),
    path('', views.home_view, name='home'), 
    path('attendance/', views.attendance_view, name='attendance'),
    path("report/", views.report_view, name="report"),
    path("generate_attendance_report/", views.generate_attendance_report, name="generate_attendance_report"),
    path("download_attendance_report/", views.download_attendance_report, name="download_attendance_report"),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)