from django.urls import include, path
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('sns.urls')),
    path('box/',include('box.urls')),
    path('user/',include('user.urls')),
]
