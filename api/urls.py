from django.urls import path

from . import webhook
from . import views

urlpatterns = [
  path('webhook/event/', webhook.eventReceiver, name='eventReceiver'),
  path('activity/bulk/create/', views.bulkCreateActivities, name='bulkActivityCreate'),
]
