from owm_key import owm_api_key
from getweatherdata import get_weather_data

def main():
    cities = ['Chicago', 'Saint Petersburg', 'Dakka']
    
    for city in cities:
        try:
            weather_data = get_weather_data(city, api_key=owm_api_key)
            print(f"Weather data for {city}: {weather_data}")
        except Exception as e:
            print(f"Error fetching weather data for {city}: {e}")

if __name__ == '__main__':
    main()
    