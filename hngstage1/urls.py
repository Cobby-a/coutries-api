from django.contrib import admin
from django.urls import path, include
from countries.views import StatusView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('status/', StatusView.as_view(), name='status'),
    path('countries/', include('countries.urls')),
]