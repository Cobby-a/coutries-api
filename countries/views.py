from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveDestroyAPIView, CreateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import FileResponse, Http404
from django.db.models import Q
from .models import Country, RefreshStatus
from .serializers import CountrySerializer, StatusResponseSerializer
from .services import CountryService
import os
from django.conf import settings


class CountryRefreshView(CreateAPIView):
    """
    POST /countries/refresh
    Fetch all countries and exchange rates, then cache them in the database
    """
    def create(self, request, *args, **kwargs):
        try:
            countries_processed = CountryService.refresh_countries()
            
            return Response({
                'message': 'Countries refreshed successfully',
                'countries_processed': countries_processed
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({
                'error': 'Failed to refresh countries',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CountryListView(ListAPIView):
    """
    GET /countries
    Get all countries from the DB with filters and sorting
    Supports:
    - ?region=Africa
    - ?currency=NGN
    - ?sort=gdp_desc (or gdp_asc, name_asc, name_desc, population_asc, population_desc)
    """
    serializer_class = CountrySerializer

    def get_queryset(self):
        queryset = Country.objects.all()

        # Filter by region
        region = self.request.query_params.get('region', None)
        if region:
            queryset = queryset.filter(region__iexact=region)

        # Filter by currency
        currency = self.request.query_params.get('currency', None)
        if currency:
            queryset = queryset.filter(currency_code__iexact=currency)

        # Sorting
        sort_param = self.request.query_params.get('sort', None)
        if sort_param:
            if sort_param == 'gdp_desc':
                queryset = queryset.order_by('-estimated_gdp')
            elif sort_param == 'gdp_asc':
                queryset = queryset.order_by('estimated_gdp')
            elif sort_param == 'name_asc':
                queryset = queryset.order_by('name')
            elif sort_param == 'name_desc':
                queryset = queryset.order_by('-name')
            elif sort_param == 'population_asc':
                queryset = queryset.order_by('population')
            elif sort_param == 'population_desc':
                queryset = queryset.order_by('-population')

        return queryset


class CountryDetailView(RetrieveDestroyAPIView):
    """
    GET /countries/:name - Get one country by name
    DELETE /countries/:name - Delete a country record
    """
    serializer_class = CountrySerializer
    lookup_field = 'name'
    lookup_url_kwarg = 'name'

    def get_queryset(self):
        return Country.objects.all()

    def get_object(self):
        """
        Override to perform case-insensitive lookup
        """
        name = self.kwargs.get('name')
        try:
            return Country.objects.get(name__iexact=name)
        except Country.DoesNotExist:
            raise Http404(f"Country '{name}' not found")


class StatusView(APIView):
    """
    GET /status
    Show total countries and last refresh timestamp
    """
    def get(self, request):
        total_countries = Country.objects.count()
        refresh_status = RefreshStatus.objects.first()
        
        if refresh_status:
            last_refreshed_at = refresh_status.last_refreshed_at
        else:
            last_refreshed_at = None

        data = {
            'total_countries': total_countries,
            'last_refreshed_at': last_refreshed_at
        }

        serializer = StatusResponseSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CountryImageView(APIView):
    """
    GET /countries/image
    Serve the generated summary image
    """
    def get(self, request):
        cache_dir = os.path.join(settings.BASE_DIR, 'cache')
        image_path = os.path.join(cache_dir, 'summary.png')

        if not os.path.exists(image_path):
            return Response({
                'error': 'Summary image not found'
            }, status=status.HTTP_404_NOT_FOUND)

        return FileResponse(open(image_path, 'rb'), content_type='image/png')