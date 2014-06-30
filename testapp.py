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
theLinqPlaces = api.media_search(lat=36.117590,lng=-115.171589, distance=5)
print theLinqPlaces
print
for media in theLinqPlaces:
    print media
    print dir(media)
    print media.link
    print media.images['standard_resolution'].url # media.images is a dictionary
    for comment in media.comments: # media.comments is an array, iterate through and print out each comment
       print comment.text

"""
# Display photos of theLinq and nearby locations
theLinqPlaces = api.location_search(lat=36.1,lng=-115.1, distance=50)
# print theLinqPlaces
for eachLocation in theLinqPlaces:
    linqRecentMedia = api.location_recent_media(location_id=eachLocation.id)
    print linqRecentMedia # prints id of each media
    # TODO: get info about everything in this list
#    for media in linqRecentMedia:
#        print media.images['standard_resolution'].url
# TODO: try a location that has so many images it requires pagination
"""

"""
for media in theLinqImages:
    print media.images['standard_resolution'].url
"""
