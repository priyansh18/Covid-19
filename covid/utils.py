import requests
import json
from datetime import datetime, timedelta

def fetch_covid_data():
    """Fetch COVID-19 data from the Disease.sh API"""
    try:
        # Global data
        global_url = "https://disease.sh/v3/covid-19/all"
        # Country-wise data
        countries_url = "https://disease.sh/v3/covid-19/countries?sort=cases"
        # Historical data for charts
        historical_url = "https://disease.sh/v3/covid-19/historical/all?lastdays=30"
        
        # Fetch all data
        response_global = requests.get(global_url)
        response_countries = requests.get(countries_url)
        response_historical = requests.get(historical_url)
        
        if all([response_global.ok, response_countries.ok, response_historical.ok]):
            return {
                'global': response_global.json(),
                'countries': response_countries.json(),
                'historical': response_historical.json()
            }
        return None
    except Exception as e:
        print(f"Error fetching COVID-19 data: {str(e)}")
        return None

def prepare_chart_data(historical_data):
    """Prepare chart data for rendering"""
    if not historical_data:
        return None
        
    # Prepare data for line chart
    cases = historical_data.get('cases', {})
    deaths = historical_data.get('deaths', {})
    recovered = historical_data.get('recovered', {})
    
    # Convert to lists for Chart.js
    dates = list(cases.keys())
    cases_data = list(cases.values())
    deaths_data = list(deaths.values())
    recovered_data = list(recovered.values())
    
    return {
        'labels': dates,
        'datasets': [
            {
                'label': 'Cases',
                'data': cases_data,
                'borderColor': 'rgba(54, 162, 235, 1)',
                'backgroundColor': 'rgba(54, 162, 235, 0.2)',
                'fill': True
            },
            {
                'label': 'Deaths',
                'data': deaths_data,
                'borderColor': 'rgba(255, 99, 132, 1)',
                'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                'fill': True
            },
            {
                'label': 'Recovered',
                'data': recovered_data,
                'borderColor': 'rgba(75, 192, 192, 1)',
                'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                'fill': True
            }
        ]
    }

def get_top_countries(countries_data, limit=5):
    """Get top N countries by number of cases"""
    if not countries_data:
        return []
    return sorted(countries_data, key=lambda x: x.get('cases', 0), reverse=True)[:limit]
