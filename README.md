# Country Currency & Exchange Rate API

A Django REST API that fetches country data and exchange rates, calculates estimated GDP, and provides CRUD operations with filtering and sorting.

## Setup Instructions

### 1. Clone and Navigate
```bash
git clone https://github.com/Cobby-a/coutries-api.git
cd country_api
```

### 2. Create Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate # On mac and linux: source venv/bin/activate  
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Start Server
```bash
python manage.py runserver
```

Server runs at `http://localhost:8000`

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/countries/refresh/` | Fetch and cache country data |
| GET | `/countries/` | List all countries |
| GET | `/countries/:name/` | Get single country |
| DELETE | `/countries/:name/` | Delete country |
| GET | `/countries/image/` | Get summary image |
| GET | `/status/` | API status |

## Quick Start

### 1. Refresh Data (Required First)
```bash
curl -X POST http://localhost:8000/countries/refresh/
```

### 2. Get Countries
```bash
curl http://localhost:8000/countries/
```

### 3. Filter by Region
```bash
curl "http://localhost:8000/countries/?region=Africa"
```

### 4. Sort by GDP
```bash
curl "http://localhost:8000/countries/?sort=gdp_desc"
```

## Query Parameters

**Filters:**
- `?region=Africa` - Filter by region
- `?currency=NGN` - Filter by currency

**Sorting:**
- `?sort=gdp_desc` - Sort by GDP descending
- `?sort=gdp_asc` - Sort by GDP ascending
- `?sort=name_asc` - Sort by name A-Z
- `?sort=population_desc` - Sort by population

## Technologies

- Django 4.2+
- Django REST Framework 3.14+
- SQLite (default)
- Requests
- Pillow

## Requirements
```
Django>=4.2.0
djangorestframework>=3.14.0
requests>=2.31.0
Pillow>=10.0.0
python-decouple>=3.8
```