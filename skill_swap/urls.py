"""
URL configuration for skill_swap project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from skillapp import views
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.register, name='home'),
    path('register/', views.register, name='register'),
    path('tutor-register/', views.tutor_register, name='tutor_register'),
    path('login/', views.login, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('profile/<int:user_id>/', views.view_profile, name='view_profile'),
    path('logout/', views.logout, name='logout'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('send-request/', views.send_request, name='send_request'),
    path('tutor-register/', views.tutor_register,name='tutor_register'),
    path('user-register/', views.user_register,name='user_register'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('tutor-dashboard/', views.tutor_dashboard, name='tutor_dashboard'),
    path("swap-requests/",views.swap_requests,name="swap_requests"),
    path("swap-request/<int:request_id>/accept/",views.accept_swap_request,name="accept_swap_request"),
    path("swap-request/<int:request_id>/reject/",views.reject_swap_request,name="reject_swap_request"),
    path("swap-request/<int:request_id>/schedule/",views.schedule_meeting,name="schedule_meeting"),
    path("tutor/create-mock-test/",views.create_mock_test,name="create_mock_test"),
    path("tutor/mock-test/<int:test_id>/questions/",views.add_mock_questions,name="add_mock_questions"),
    path("tutor/mock-test/<int:test_id>/publish/",views.publish_mock_test,name="publish_mock_test" ),
    path("mock-test/<int:test_id>/preview/",views.preview_mock_test,name="preview_mock_test"),
    path("mock-test/<int:test_id>/attempt/",views.attempt_mock_test,name="attempt_mock_test"),
    path("mock-test/<int:test_id>/attempt/",views.attempt_mock_test,name="attempt_mock_test"),
    path("my-test-attempts/",views.my_test_attempts,name="my_test_attempts"),
    path("test-results/<int:test_id>/",views.view_test_results,name="view_test_results"),
    path("request-certificate/<int:test_id>/",views.request_certificate,name="request_certificate"),
    path("request-certificate/<int:test_id>/",views.request_certificate,name="request_certificate"),
    path("tutor/certificate-requests/",views.tutor_certificate_requests,name="tutor_certificate_requests"),
    path("tutor/approve-certificate/<int:request_id>/",views.approve_certificate_request,name="approve_certificate_request"),
    path("tutor/reject-certificate/<int:request_id>/",views.reject_certificate_request,name="reject_certificate_request"),
    path("certificate-payment/<int:request_id>/",views.certificate_payment,name="certificate_payment"),
    path("process-certificate-payment/<int:request_id>/",views.process_certificate_payment,name="process_certificate_payment"),
    path("generate-certificate/<int:request_id>/",views.generate_certificate,name="generate_certificate"),
    path("view-certificate/<int:request_id>/",views.view_certificate,name="view_certificate"),


]