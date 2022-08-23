from django.urls import path
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    # TO DO convert to as_view
    path('', TemplateView.as_view(template_name='home/home.html'), name='home'),
    path('privacy', TemplateView.as_view(template_name='home/privacy_policy.html'), name='privacy'),
    
    path('account', views.account, name='account'),
    path('register', views.register, name='register'),
    path('connect-to-strava', views.connect_to_strava, name='connect-to-strava'),
    
    path('activity/<int:activityId>', views.viewActivity, name='viewActivity'),
    path('heatmap', views.viewHeatmap, name='viewHeatmap'),
]
