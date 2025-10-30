import requests
import random
from decimal import Decimal
from django.utils import timezone
from django.db import transaction
from .models import Country, RefreshStatus
from PIL import Image, ImageDraw, ImageFont
import os
from django.conf import settings


class CountryService:
    """
    Service class to handle country data fetching and processing
    """
    COUNTRIES_API = "https://restcountries.com/v2/all?fields=name,capital,region,population,flag,currencies"
    EXCHANGE_RATE_API = "https://open.er-api.com/v6/latest/USD"

    @staticmethod
    def fetch_countries():
        """
        Fetch countries from external API
        """
        try:
            response = requests.get(CountryService.COUNTRIES_API, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch countries: {str(e)}")

    @staticmethod
    def fetch_exchange_rates():
        """
        Fetch exchange rates from external API
        """
        try:
            response = requests.get(CountryService.EXCHANGE_RATE_API, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data.get('rates', {})
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch exchange rates: {str(e)}")

    @staticmethod
    def calculate_gdp(population, exchange_rate):
        """
        Calculate estimated GDP: population × random(1000-2000) ÷ exchange_rate
        """
        if not exchange_rate or exchange_rate == 0:
            return Decimal('0')
        
        random_multiplier = random.uniform(1000, 2000)
        gdp = (population * random_multiplier) / float(exchange_rate)
        return Decimal(str(round(gdp, 2)))

    @staticmethod
    def extract_currency_code(currencies):
        """
        Extract first currency code from currencies array
        Returns None if array is empty
        """
        if not currencies or len(currencies) == 0:
            return None
        
        # Get first currency code
        first_currency = currencies[0]
        return first_currency.get('code')

    @staticmethod
    @transaction.atomic
    def refresh_countries():
        """
        Main method to fetch, process and store country data
        """
        # Fetch data from external APIs
        countries_data = CountryService.fetch_countries()
        exchange_rates = CountryService.fetch_exchange_rates()

        countries_processed = 0
        now = timezone.now()

        for country_data in countries_data:
            name = country_data.get('name')
            if not name:
                continue

            capital = country_data.get('capital', '')
            region = country_data.get('region', '')
            population = country_data.get('population', 0)
            flag_url = country_data.get('flag', '')
            currencies = country_data.get('currencies', [])

            # Extract currency code
            currency_code = CountryService.extract_currency_code(currencies)


            # Update or create country record
            exchange_rate = None
            estimated_gdp = Decimal('0')

            if currency_code:
                rate_value = exchange_rates.get(currency_code)
                if rate_value is not None:
                    # store as Decimal
                    exchange_rate = Decimal(str(rate_value))
                    estimated_gdp = CountryService.calculate_gdp(population, exchange_rate)
                else:
                    # currency_code provided but not found in rates
                    exchange_rate = None
                    estimated_gdp = Decimal('0')
            else:
                # no currency array or empty -> currency_code stays None and estimated_gdp zero
                exchange_rate = None
                estimated_gdp = Decimal('0')

            # Update or create country record using case-insensitive match on name
            existing = Country.objects.filter(name__iexact=name).first()

            if existing:
                # update fields
                existing.capital = capital
                existing.region = region
                existing.population = population
                existing.currency_code = currency_code
                existing.exchange_rate = exchange_rate
                existing.estimated_gdp = estimated_gdp
                existing.flag_url = flag_url
                existing.last_refreshed_at = now
                existing.save()
            else:
                Country.objects.create(
                    name=name,
                    capital=capital,
                    region=region,
                    population=population,
                    currency_code=currency_code,
                    exchange_rate=exchange_rate,
                    estimated_gdp=estimated_gdp,
                    flag_url=flag_url,
                    last_refreshed_at=now
                )

            countries_processed += 1

        # Update refresh status
        RefreshStatus.objects.all().delete()
        RefreshStatus.objects.create(
            total_countries=countries_processed,
            last_refreshed_at=now
        )

        # Generate summary image
        CountryService.generate_summary_image()

        return countries_processed

    @staticmethod
    def generate_summary_image():
        """
        Generate a summary image with country statistics
        """
        # Get statistics
        total_countries = Country.objects.count()
        top_countries = Country.objects.order_by('-estimated_gdp')[:5]
        refresh_status = RefreshStatus.objects.first()
        last_refreshed = refresh_status.last_refreshed_at if refresh_status else timezone.now()

        # Create image
        img_width = 800
        img_height = 600
        img = Image.new('RGB', (img_width, img_height), color='white')
        draw = ImageDraw.Draw(img)

        # Try to use a better font, fallback to default
        try:
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
            text_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
            small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
        except:
            title_font = ImageFont.load_default()
            text_font = ImageFont.load_default()
            small_font = ImageFont.load_default()

        # Draw title
        title = "Country Statistics Summary"
        draw.text((50, 30), title, fill='black', font=title_font)

        # Draw total countries
        y_position = 100
        draw.text((50, y_position), f"Total Countries: {total_countries}", fill='blue', font=text_font)

        # Draw top 5 countries
        y_position += 60
        draw.text((50, y_position), "Top 5 Countries by Estimated GDP:", fill='black', font=text_font)
        
        y_position += 40
        for idx, country in enumerate(top_countries, 1):
            gdp_formatted = f"{country.estimated_gdp:,.2f}"
            text = f"{idx}. {country.name}: ${gdp_formatted}"
            draw.text((70, y_position), text, fill='darkgreen', font=small_font)
            y_position += 35

        # Draw timestamp
        y_position += 30
        timestamp_text = f"Last Refreshed: {last_refreshed.strftime('%Y-%m-%d %H:%M:%S UTC')}"
        draw.text((50, y_position), timestamp_text, fill='gray', font=small_font)

        # Create cache directory if it doesn't exist
        cache_dir = os.path.join(settings.BASE_DIR, 'cache')
        os.makedirs(cache_dir, exist_ok=True)

        # Save image
        image_path = os.path.join(cache_dir, 'summary.png')
        img.save(image_path)

        return image_path