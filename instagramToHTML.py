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
MAXRESULTS=80 #max is 80, no pagination supported
FOURSQUAREID="52e032d211d2cd200fa5f9d9" # Foursquare ID of landmark

api = InstagramAPI(access_token=access_token)

# Creates the header for the webpage
def createHTMLTemplate():
    outputFile.write("<!DOCTYPE html PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">"
            + "<head>\n<style type=\"text/css\">\nbody {\n\tbackground-color: DarkSlateGray;\n\t"
           + "font-family: 'Arial',Helvetica, Sans-Serif;\n\tcolor: white;\n\ttext-align: center;"
           + "\n}\n</style>\n<title>Instagram Data Analysis</title>\n</head>\n<body>\n"
           + "<h1>Images from " + str(LATITUDE) + "/" + str(LONGITUDE) + "</h1>\n"
           + "<h2>(click thumbnail for direct Instagram page)</h2>")

# Given a media object, writes out to the webpage
def addImageHTML(media):
    #print dir(media)
    print str(media.user) + " posted this " + media.type + " during date: " \
            + str(media.created_time) + "\n" + "at " + str(media.location.point) + " and received " \
            + str(media.like_count) + " likes.\n"
    outputFile.write("<a href=\"" + media.link + "\">")
    outputFile.write("<img style=\"height:auto; width:auto; max-width:300px; max-height:300px;padding: 10px;\""
                + "src=\"" + media.images['standard_resolution'].url + "\" title=\" User: " 
                + media.user.username + "\" alt=\"" + media.user.username + "\"></a>\n")

def findMediaAtLocation(locationResults):
    for eachLocation in locationResults:
        recentMedia = api.location_recent_media(count=MAXRESULTS, location_id=eachLocation.id)
        #TODO: Pagination of recentMedia
        print recentMedia
        asdf
        for media in recentMedia[0]: #first element of tuple contains media
            addImageHTML(media)



createHTMLTemplate()

# Embed links of all photos at lat/long location in html
searchResults = api.media_search(count=MAXRESULTS, lat=LATITUDE,lng=LONGITUDE, distance=DISTANCE)
for media in searchResults:
    addImageHTML(media)

# Get photos from location based on foursquareID
outputFile.write("<br><h1>Second Search (based on foursquare ID):</h1><br>\n")
searchResults = api.location_search(count=MAXRESULTS, foursquare_v2_id=FOURSQUAREID,
                                distance=DISTANCE)

findMediaAtLocation(searchResults)

# Embed photos of lat/long and nearby locations
# Not as useful as first search
outputFile.write("<br><h1>Third Search (based on points of interest):</h1><br>\n")
searchResults = api.location_search(count=MAXRESULTS, lat=LATITUDE,lng=LONGITUDE, distance=DISTANCE)
findMediaAtLocation(searchResults)

#Conclude the file and open it
outputFile.write("</body>\n</html>")
webbrowser.open_new_tab("file://" + outputFilepath + "/" + outputFilename)
