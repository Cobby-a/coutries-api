from django.db import models
from django.utils import timezone


class Country(models.Model):
    name = models.CharField(max_length=255, unique=True, db_index=True)
    capital = models.CharField(max_length=255, blank=True, null=True)
    region = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    population = models.BigIntegerField()
    currency_code = models.CharField(max_length=10, blank=True, null=True, db_index=True)
    exchange_rate = models.DecimalField(max_digits=15, decimal_places=4, blank=True, null=True)
    estimated_gdp = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    flag_url = models.URLField(blank=True, null=True)
    last_refreshed_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name_plural = "Countries"
        ordering = ['name']

    def __str__(self):
        return self.name


class RefreshStatus(models.Model):
    last_refreshed_at = models.DateTimeField(default=timezone.now)
    total_countries = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = "Refresh Status"

    def __str__(self):
        return f"Last refreshed: {self.last_refreshed_at}"