#!/usr/local/bin/python
from instagram.client import InstagramAPI
import webbrowser
import os

# output file to be used for html output and opened in web browser
outputFilename = 'output.html'
outputFile = open(outputFilename, 'w')
outputFilepath = os.path.dirname(os.path.realpath(__file__))

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

# Displays links of all photos at The Linq and embeds in html
# theLinqImages = api.location_search(lat=36.117590,lng=-115.171589, distance=2500)
theLinqPlaces = api.media_search(lat=36.117590,lng=-115.171589, distance=50)
print theLinqPlaces
print
for media in theLinqPlaces:
    print media
    print dir(media)
    print media.link
    outputFile.write("<a href=\"" + media.link + "\">")
    print media.images['standard_resolution'].url # media.images is a dictionary
    outputFile.write("<img src=\"" + media.images['standard_resolution'].url + "\"></a>\n")
    for comment in media.comments: # media.comments is an array, iterate through and print out each comment
        print "Image comment: " + comment.text

outputFile.write("<br> <h1>Second Search:<h1><br>\n")
    
# Display photos of theLinq and nearby locations
theLinqPlaces = api.location_search(lat=36.1,lng=-115.1, distance=50)
# print theLinqPlaces
for eachLocation in theLinqPlaces:
    linqRecentMedia = api.location_recent_media(location_id=eachLocation.id)
    #print linqRecentMedia # prints id of each media
    for media in linqRecentMedia[0]: #first element of tuple contains media
        outputFile.write("<a href=\"" + media.link + "\">")
        outputFile.write("<img src=\"" + media.images['standard_resolution'].url + "\"></a>\n")
# TODO: try a location that has so many images it requires pagination

webbrowser.open_new_tab("file://" + outputFilepath + "/" + outputFilename)
