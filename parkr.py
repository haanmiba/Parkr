import requests
import json
import math
import pandas as pd

## API Key to use the Google Maps API
api_key = open('api_keys.txt').readline()

address = input("Where in Buffalo do you want to go?\n")
google_maps_api_url = 'https://maps.googleapis.com/maps/api/geocode/json?address={}&key={}'

## Make a request to the Google Maps API to retrieve 
## the location's latitude and longitude coordinates.
google_api_request = requests.get(google_maps_api_url.format(address, api_key))
print(google_maps_api_url.format(address, api_key))
geocode = json.loads(google_api_request.content)
latitude = float(geocode['results'][0]['geometry']['location']['lat'])
longitude = float(geocode['results'][0]['geometry']['location']['lng'])

## Make a request to Socrata Open Data API for Buffalo, NY and fetch the parking violations.
socrata_location_query_url = 'https://data.buffalony.gov/resource/ux3f-ypyc.json?$where=within_circle(location_2, {}, {}, 600)'
socrata_api_request = requests.get(socrata_location_query_url.format(latitude, longitude))
parking_violations = json.loads(socrata_api_request.content)

## Fetch all of the coordinates of each parking violation
violation_latitudes = [float(entry['latitude']) for entry in parking_violations]
violation_longitudes = [float(entry['longitude']) for entry in parking_violations]

## Initialize the dictionary holding all of the data
test_points = {key : [] for key in ('x', 'y', 'count', 'distance')}

radius = (10 ** -3)

for multiplier in range(1, 6):
    for angle in range(0, 64):
        test_x = longitude + ((multiplier * radius) * math.cos(angle * (math.pi / 32)))
        test_y = latitude + ((multiplier * radius) * math.sin(angle * (math.pi / 32)))
        count = 0
        for long, lat in zip(violation_longitudes, violation_latitudes):
            for distance in (.015 ,.014 ,.013, .012 ,.011 ,.01, .009, .008, .007, .006, .005):
                if abs(test_x - long) < distance and abs(test_y - lat) < distance:
                    count += 1
        test_points['x'].append(test_x)
        test_points['y'].append(test_y)
        test_points['count'].append(count)
        test_points['distance'].append(multiplier)

pd_points = pd.DataFrame(test_points)

pd_points['parking_matrix'] = (pd_points['count'] ** 2) * (pd_points['distance'])

print(pd_points.sort_values('count', ascending=True))

print(pd_points[pd_points['count'] < pd_points['count'].mean()])
