import requests
import json

def get_weather_data(place, api_key=None):
    if api_key is None:
        raise ValueError("API key is required")
    
    url = f'https://api.openweathermap.org/data/2.5/weather?q={place}&appid={api_key}&units=metric'
    
    response = requests.get(url)
    
    if response.status_code != 200:
        response.raise_for_status()

    data = response.json()

    city_name = data['name']
    country_code = data['sys']['country']
    lat = data['coord']['lat']
    lon = data['coord']['lon']
    feels_like = data['main']['feels_like']
    timezone = data['timezone']

    timezone_hours = timezone // 3600
    timezone_str = f"UTC{'+' if timezone_hours >= 0 else '-'}{abs(timezone_hours)}"

    result = {
        "name": city_name,
        "coord": {"lon": lon, "lat": lat},
        "country": country_code,
        "feels_like": feels_like,
        "timezone": timezone_str
    }

    return json.dumps(result, ensure_ascii=False, indent=4)
