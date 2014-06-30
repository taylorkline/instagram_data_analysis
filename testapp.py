#!/usr/local/bin/python
from instagram.client import InstagramAPI

keyFilename = 'keys'
keyFile = open(keyFilename, 'r')
#access token is on 6th line
for x in range (0,5):
    keyFile.readline()
access_token = keyFile.readline().rstrip()

api = InstagramAPI(access_token=access_token)

# Displays the url of all popular images
"""
popular_media = api.media_popular(count=20)
for media in popular_media:
    print media.images['standard_resolution'].url
"""
# Displays links of all photos at The Linq
# TODO: Get images from these locations and output to html file?
# theLinqImages = api.location_search(lat=36.117590,lng=-115.171589, distance=2500)
theLinqPlaces = api.location_search(lat=36.1,lng=-115.1, distance=2500)
print theLinqPlaces
for eachLocation in theLinqPlaces:
    print eachLocation.id

"""
for media in theLinqImages:
    print media.images['standard_resolution'].url
"""
