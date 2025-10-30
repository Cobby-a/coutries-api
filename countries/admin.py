from django.contrib import admin
from .models import Country, RefreshStatus


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ['name', 'capital', 'region', 'population', 'currency_code', 'exchange_rate', 'estimated_gdp', 'last_refreshed_at']
    list_filter = ['region', 'currency_code']
    search_fields = ['name', 'capital', 'region', 'currency_code']
    ordering = ['name']
    readonly_fields = ['estimated_gdp', 'last_refreshed_at']


@admin.register(RefreshStatus)
class RefreshStatusAdmin(admin.ModelAdmin):
    list_display = ['total_countries', 'last_refreshed_at']
    readonly_fields = ['total_countries', 'last_refreshed_at']