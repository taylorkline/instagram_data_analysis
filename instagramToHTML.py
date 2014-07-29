#!/usr/local/bin/python
# Application by Taylor Kline
# Creates an html webpage based on Instagram photos at a certain location
# Setting variables in ALL_CAPS is your responsibility.
from instagram.client import InstagramAPI
from geopy.geocoders import GoogleV3
import os
import errno
from sys import exit
from time import sleep
from time import localtime
from webbrowser import open_new_tab

# reads access token from specified line in keyFile
ACCESS_TOKEN_LINE=1
keyFilename = 'keys'
keyFile = open(keyFilename, 'r')
for x in range (0,ACCESS_TOKEN_LINE-1):
    keyFile.readline()
access_token = keyFile.readline().rstrip()

# geolocator variables
geolocator = GoogleV3()

# user specified variables to influence search
DESTINATION="3545 S Las Vegas Blvd"
DISTANCE=100 # Radial distance (in meters) to search from lat/long origin

# Max number of pictures to find at specific destination
# the max number of results possible is 80
MAXRESULTS=80 

# how many recent pictures to look for in nearby locations
# Keep this one low or risk rate limiting
PERLOCATION=16
FOURSQUAREID="" # Foursquare ID of landmark (can leave blank to skip search)

try: 
    address, (latitude, longitude) = geolocator.geocode(DESTINATION)
except Exception:
    print "Sorry, but your destination was not able to be found."
    print ("Please check your internet connection or retry with a new landmark or specific, valid"
       " address from Google Maps.")
    sleep(2)
    exit()

# output file to be used for html output and opened in web browser
currentTime = str(localtime().tm_year) + '-' + str(localtime().tm_mon) + '-' + str(localtime().tm_mday) + '-' + str(localtime().tm_hour) + '-' + str(localtime().tm_sec)
outputFilename = 'output_' + DESTINATION + '_' + currentTime +  '.html'
outputDirectory = os.path.dirname(os.path.realpath(__file__)) + '/html_output/'
try:
    os.makedirs(outputDirectory)
except OSError as exception:
    if exception.errno != errno.EEXIST:
        raise
outputFile = open(os.path.join(outputDirectory, outputFilename), 'w')
outputFileLocation = outputFile.name

print "Begining search for pictures within " + str(DISTANCE) + " meters of destination: "
print address, latitude, longitude
print "If this is not correct, please reset the variables in ALL CAPS."
sleep(5)

api = InstagramAPI(access_token=access_token)

# Creates the header for the webpage
def createHTMLTemplate():
    outputFile.write("<!DOCTYPE html PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">"
           + "<head>\n<style type=\"text/css\">\nbody {\n\tbackground-color: DarkSlateGray;\n\t"
           + "font-family: 'Arial',Helvetica, Sans-Serif;\n\tcolor: white;\n\ttext-align: center;"
           + "\n}\n</style>\n<title>Instagram Data Analysis</title>\n</head>\n<body>\n"
           + "<h1>Images from " + str(DESTINATION) + "</h1>\n"
           + "<h2>(click thumbnail for direct Instagram page)</h2>")

# Given a media object, writes out to the webpage
def addImageHTML(media):
    #print dir(media)
    print (str(media.user) + " posted this " + media.type + " during date: " \
            + str(media.created_time) + "\n" + "at " + str(media.location.point)
            + " and received " + str(media.like_count) + " likes.\n")
    outputFile.write("<a href=\"" + media.link + "\">")
    outputFile.write("<img style=\"height:auto; width:auto; max-width:300px; max-height:300px;padding: 10px;\""
                + "src=\"" + media.images['standard_resolution'].url + "\" title=\" User: " 
                + media.user.username + "\" alt=\"" + media.user.username + "\"></a>\n")
    sleep(1)

# Prints out pictures in each location in locationResults
def findMediaAtLocation(locationResults):
    for eachLocation in locationResults:
        #Inform user of location to be searched
        print "Searching for up to " + str(PERLOCATION) + " pictures near " + eachLocation.name

        recentMedia, nextURL = api.location_recent_media(count=PERLOCATION, location_id=eachLocation.id)
        totalFollowers = recentMedia
        sleep(2)

        while nextURL and (len(totalFollowers) < PERLOCATION):
            recentMedia, nextURL = api.location_recent_media(count=(PERLOCATION - len(totalFollowers)),
                    location_id=eachLocation.id, with_next_url=nextURL)

            # location_recent_media is returning too many results, narrow if necessary
            if (len(totalFollowers) + len(recentMedia)) < PERLOCATION:
                totalFollowers += recentMedia
            else:
                additional = PERLOCATION - len(totalFollowers)
                for each in range(0, additional):
                    totalFollowers.append(recentMedia[each])
            sleep(1)

        assert len(totalFollowers) <= PERLOCATION

        print str(len(totalFollowers)) + " pictures found at location."
        sleep(2)

        if len(totalFollowers) > 0:
            #Add in a divider for each location.
            outputFile.write("<br><b>Nearby Location: " + eachLocation.name + ".</b><br>")

            #Print the media to the html code
            for media in totalFollowers: #first element of tuple contains media
                addImageHTML(media)

createHTMLTemplate()

# Embed links of all photos at lat/long location in html
searchResults = api.media_search(count=MAXRESULTS, lat=latitude,lng=longitude, distance=DISTANCE)
for media in searchResults:
    addImageHTML(media)

# Get photos from location based on foursquareID
if FOURSQUAREID: 
    outputFile.write("<br><h1>Second Search (based on foursquare ID):</h1><br>\n")
    searchResults = api.location_search(count=MAXRESULTS, foursquare_v2_id=FOURSQUAREID,
                                distance=DISTANCE)
    findMediaAtLocation(searchResults)
if not FOURSQUAREID:
    print "No FOURSQUAREID given - skipping search by Foursquare location"
    sleep(2)

# Embed photos of lat/long and nearby locations
# Not as useful as first search
if FOURSQUAREID: 
    outputFile.write("<br><h1>Third Search (based on points of interest):</h1><br>\n")
if not FOURSQUAREID: 
    outputFile.write("<br><h1>Second Search (based on points of interest):</h1><br>\n")
searchResults = api.location_search(count=MAXRESULTS, lat=latitude,lng=longitude, distance=DISTANCE)
print "Found " + str(len(searchResults)) + " nearby landmarks to check for pictures near."
findMediaAtLocation(searchResults)

#Conclude the file and open it
outputFile.write("</body>\n</html>")
open_new_tab("file://" + outputFileLocation)
