"""
URL configuration for email_marketing app
"""

from django.urls import path
from . import views

app_name = 'email_marketing'

urlpatterns = [
    # Email tracking URLs
    path('track/open/<str:tracking_token>/', views.email_tracking_pixel, name='email_tracking_pixel'),
    path('track/click/<str:tracking_token>/', views.email_click_tracking, name='email_click_tracking'),
    
    # Unsubscribe URLs
    path('unsubscribe/<int:recipient_id>/', views.unsubscribe_recipient, name='unsubscribe_recipient'),
    
    # Email preview
    path('preview/<int:template_id>/', views.email_preview, name='email_preview'),
    
    # Campaign analytics
    path('analytics/<int:campaign_id>/', views.campaign_analytics, name='campaign_analytics'),
]
