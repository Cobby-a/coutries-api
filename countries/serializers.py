from rest_framework import serializers
from .models import Country, RefreshStatus


class CountrySerializer(serializers.ModelSerializer):
    """
    Serializer for Country model with all fields
    """
    class Meta:
        model = Country
        fields = [
            'id',
            'name',
            'capital',
            'region',
            'population',
            'currency_code',
            'exchange_rate',
            'estimated_gdp',
            'flag_url',
            'last_refreshed_at'
        ]
        read_only_fields = ['id', 'estimated_gdp', 'last_refreshed_at']

    def validate(self, data):
        """
        Validate that required fields are present
        """
        if not data.get('name'):
            raise serializers.ValidationError({
                'name': 'is required'
            })
        
        if not data.get('population'):
            raise serializers.ValidationError({
                'population': 'is required'
            })
        
        return data


class RefreshStatusSerializer(serializers.ModelSerializer):
    """
    Serializer for refresh status
    """
    class Meta:
        model = RefreshStatus
        fields = ['total_countries', 'last_refreshed_at']


class StatusResponseSerializer(serializers.Serializer):
    """
    Serializer for status endpoint response
    """
    total_countries = serializers.IntegerField()
    last_refreshed_at = serializers.DateTimeField()