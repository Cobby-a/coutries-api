from django.urls import path, re_path
from .views import (
    CountryRefreshView,
    CountryListView,
    CountryDetailView,
    StatusView,
    CountryImageView
)

app_name = 'countries'

urlpatterns = [
    path('refresh/', CountryRefreshView.as_view(), name='country-refresh'),
    
    path('', CountryListView.as_view(), name='country-list'),
    
    path('image/', CountryImageView.as_view(), name='country-image'),
    # path('<str:name>/', CountryDetailView.as_view(), name='country-detail'),

    re_path(r'^(?P<name>[^/]+)/?$', CountryDetailView.as_view(), name='country-detail'),
]

status_urlpatterns = [
    path('status/', StatusView.as_view(), name='status'),
]