from django.contrib import admin
from django.urls import path, include

urlpatterns = [
  path('', include('app.urls')),
  path('api/', include('api.urls')),
  path('graph/', include('graph.urls')),
  path('user/', include('django.contrib.auth.urls')),
  path('admin/', admin.site.urls),
]
