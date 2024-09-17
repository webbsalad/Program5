import pytest
import json
from getweatherdata import get_weather_data

key = ''  

def test_without_key():
    with pytest.raises(ValueError, match="API key is required"):
        get_weather_data("Moscow")

def test_in_riga():
    data = json.loads(get_weather_data("Riga", api_key=key))
    assert data is not None

def test_type_of_res():
    data = get_weather_data("Riga", api_key=key)
    assert isinstance(data, str)

def test_args_error():
    with pytest.raises(ValueError, match="API key is required"):
        get_weather_data('')

def test_pos_arg_error():
    with pytest.raises(ValueError, match="API key is required"):
        get_weather_data('', api_key=key)

def test_coords_dim():
    data = json.loads(get_weather_data('Riga', api_key=key))
    assert len(data['coord']) == 2

def test_temp_type():
    data = json.loads(get_weather_data('Riga', api_key=key))
    assert isinstance(data['feels_like'], float)

inp_params_1 = "city, api_key, expected_country"
exp_params_countries = [("Chicago", key, 'US'),
                        ("Saint Petersburg", key, 'RU'), 
                        ("Dakka", key, 'BD')]

@pytest.mark.parametrize(inp_params_1, exp_params_countries)
def test_countries(city, api_key, expected_country):
    data = json.loads(get_weather_data(city, api_key=key))
    assert data['country'] == expected_country

inp_params_2 = "city, api_key, expected_time"
exp_params_timezones = [("Chicago", key, 'UTC-5'),
                        ("Saint Petersburg", key, 'UTC+3'),
                        ("Dakka", key, 'UTC+6')]

@pytest.mark.parametrize(inp_params_2, exp_params_timezones)
def test_utc_time(city, api_key, expected_time):
    data = json.loads(get_weather_data(city, api_key=key))
    assert data['timezone'] == expected_time
