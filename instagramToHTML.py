#!/usr/local/bin/python
# Application by Taylor Kline
# Creates an html webpage based on Instagram photos at a certain location
# Setting variables in ALL_CAPS is your responsibility.
from instagram.client import InstagramAPI
import webbrowser
import os

# output file to be used for html output and opened in web browser
outputFilename = 'output.html'
outputFile = open(outputFilename, 'w')
outputFilepath = os.path.dirname(os.path.realpath(__file__))

# reads access token from specified line in keyFile
ACCESS_TOKEN_LINE=6
keyFilename = 'keys'
keyFile = open(keyFilename, 'r')
for x in range (0,ACCESS_TOKEN_LINE-1):
    keyFile.readline()
access_token = keyFile.readline().rstrip()

# user specified variables to influence search
LATITUDE=36.117590
LONGITUDE=-115.171589
DISTANCE=100 # Radial distance (in meters) to search from lat/long origin
MAXRESULTS=5

api = InstagramAPI(access_token=access_token)

# Given a media object, writes out to the webpage
def addImageHTML(media):
        outputFile.write("<a href=\"" + media.link + "\">")
        outputFile.write("<img style=\"height:auto; width:auto; max-width:300px; max-height:300px;\" src=\"" + media.images['standard_resolution'].url + "\" title=\" User: " + media.user.username + "\" alt=\"" + media.user.username + "\"></a>\n")

# Displays links of all photos at The Linq and embeds in html
theLinqPlaces = api.media_search(count=MAXRESULTS, lat=LATITUDE,lng=LONGITUDE, distance=DISTANCE)
print theLinqPlaces
print
for media in theLinqPlaces:
    print media
    print dir(media)
    print media.link
    print dir(media.user)
    print media.user.username
    print media.images['standard_resolution'].url # media.images is a dictionary
    addImageHTML(media)
    for comment in media.comments: # media.comments is an array, iterate through and print out each comment
        print "Image comment: " + comment.text

# Display photos of theLinq and nearby locations
# Not as useful as first search
outputFile.write("<br><h1>Second Search:<h1><br>\n")
theLinqPlaces = api.location_search(count=MAXRESULTS, lat=LATITUDE,lng=LONGITUDE, distance=DISTANCE)
# print theLinqPlaces
for eachLocation in theLinqPlaces:
    linqRecentMedia = api.location_recent_media(location_id=eachLocation.id)
    #print linqRecentMedia # prints id of each media
    for media in linqRecentMedia[0]: #first element of tuple contains media
        addImageHTML(media)

webbrowser.open_new_tab("file://" + outputFilepath + "/" + outputFilename)
