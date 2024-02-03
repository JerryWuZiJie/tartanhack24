import googlemaps
import configparser
from pprint import pprint


# def get_address( )

# load in api key from config
config = configparser.ConfigParser()
config.read('config.ini')
api_key = config.get("APIs", "google_api")

gmaps = googlemaps.Client(key=api_key)

# Geocoding an address
geocode_result = gmaps.geocode('Squirrel Hill North')
pprint(geocode_result)

# # Look up an address with reverse geocoding
# reverse_geocode_result = gmaps.reverse_geocode((40.714224, -73.961452))
# pprint(reverse_geocode_result)

# # Request directions via public transit
# now = datetime.now()
# directions_result = gmaps.directions("Sydney Town Hall",
#                                      "Parramatta, NSW",
#                                      mode="transit",
#                                      departure_time=now)
# pprint(directions_result)

# # Validate an address with address validation
# addressvalidation_result =  gmaps.addressvalidation(['1600 Amphitheatre Pk'], 
#                                                     regionCode='US',
#                                                     locality='Mountain View', 
#                                                     enableUspsCass=True)
# pprint(addressvalidation_result)

# parsing the json response
address = geocode_result[0]['formatted_address']
geo_location = geocode_result[0]['geometry']['location']
lat = geo_location['lat']
lng = geo_location['lng']
print(address)
print(lat)
print(lng)