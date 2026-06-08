"""
URL configuration for foodlink project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from foodlinkApp import views # Import views from your app

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('', views.home_view, name='home'),
    path('about/', views.about_view, name='about'), # About page
    path('contact/', views.contact_view, name='contact'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboards paths
    path('donor-dashboard/', views.donor_dashboard_view, name='donor-dashboard'),
    path('ngo-dashboard/', views.ngo_dashboard_view, name='ngo-dashboard'),
    path('volunteer/', views.volunteer_dashboard_view, name='volunteer'),
    path('master-control/', views.master_admin_view, name='master-admin'),
    path('delete-donation/<int:donation_id>/', views.delete_donation_view, name='delete-donation'),
    path('accept-donation/<int:donation_id>/', views.accept_donation_view, name='accept-donation'),
    path('delete-message/<int:message_id>/', views.delete_message_view, name='delete-message'),
    path('toggle-user-status/<int:user_id>/', views.toggle_user_status_view, name='toggle-user-status'),
    path('delete-user/<int:user_id>/', views.delete_user_view, name='delete-user'),
    path('change-user-role/<int:user_id>/', views.change_user_role_view, name='change-user-role'),
    
    # Gemini API route
    path('api/chat/', views.gemini_chat_api, name='gemini_chat_api'),
]
