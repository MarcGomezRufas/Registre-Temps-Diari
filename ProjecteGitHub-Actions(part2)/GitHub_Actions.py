import openmeteo_requests
from datetime import datetime
import json
import pandas as pd
import requests_cache
from retry_requests import retry

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
url = "https://api.open-meteo.com/v1/forecast"
params = {
	"latitude": 41.7281,
	"longitude": 1.824,
	"hourly": "temperature_2m"
}
responses = openmeteo.weather_api(url, params=params)

# Process first location. Add a for-loop for multiple locations or weather models
response = responses[0]
print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
print(f"Elevation {response.Elevation()} m asl")
print(f"Timezone {response.Timezone()}{response.TimezoneAbbreviation()}")
print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

# Process hourly data. The order of variables needs to be the same as requested.
hourly = response.Hourly()
hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()

hourly_data = {"date": pd.date_range(
	start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
	end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
	freq = pd.Timedelta(seconds = hourly.Interval()),
	inclusive = "left"
)}

hourly_data["temperature_2m"] = hourly_temperature_2m

hourly_dataframe = pd.DataFrame(data = hourly_data)
print(hourly_dataframe)


#################################

def calcula_max_min_mitjana(data):
    
    temperatura_maxima = data[0]
    tempreatura_minima = data[0]
    suma = 0
    
    for temps in data:
        
        if temps > temperatura_maxima:
            temperatura_maxima = temps
        if temps < tempreatura_minima:
            tempreatura_minima = temps
        suma = suma + temps
    mitjana = round(suma / len(data), 2)
    return temperatura_maxima, tempreatura_minima, mitjana

maxima, minima, mitjana = calcula_max_min_mitjana(hourly_temperature_2m)



avui = datetime.now().strftime("%Y-%m-%d")
nom_fitxer = f"temperatures_{datetime.now().strftime('%Y%m%d')}.json"

dades = {
    "data": avui,
    "temperatura_maxima": float(maxima),
    "temperatura_minima": float(minima),
    "temperatura_mitjana": float(mitjana)
}


with open(nom_fitxer, "w") as fitxer:
    json.dump(dades, fitxer, indent=4)

print(f"Fitxer {nom_fitxer} creat!")