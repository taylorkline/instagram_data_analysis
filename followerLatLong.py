#!/usr/local/bin/python
# Application by Taylor Kline
# Gathers lat / long info on follwers from their most recently posted picture.
# Setting variables in ALL_CAPS is your responsibility.
from instagram.client import InstagramAPI
from instagram.bind import InstagramAPIError
import os
import errno
from time import sleep
from time import localtime
from shutil import copy2,copytree
from webbrowser import open_new_tab

# reads access token from specified line in keyFile
ACCESS_TOKEN_LINE=1
keyFilename = 'keys'
keyFile = open(keyFilename, 'r')
for x in range (0,ACCESS_TOKEN_LINE-1):
    keyFile.readline()
access_token = keyFile.readline().rstrip()

# user specified variables to influence search
USERNAME = 'thelinq'
MAXPAGES = 1 #maximum number of approximately 100-user pages to process
# Note: This number is approximate, as some pages do not have the full 100 users
MAXTRIES = 2 #number of pictures to go through on users' timelines to attempt to find location
#upper limit is 20 pictures to go through

# output file to be used for html output and opened in web browser
currentTime = str(localtime().tm_year) + '-' + str(localtime().tm_mon) + '-' + str(localtime().tm_mday) + '-' + str(localtime().tm_hour) + '-' + str(localtime().tm_sec)
outputFilename = 'output_' + USERNAME + '_' + currentTime +  '.js'
workingDirectory = os.path.dirname(os.path.realpath(__file__))
outputDirectory = workingDirectory + '/LatLongData/'
try:
        os.makedirs(outputDirectory)
except OSError as exception:
    if exception.errno != errno.EEXIST:
        raise
outputFile = open(os.path.join(outputDirectory, outputFilename), 'w')

# initiate the api
api = InstagramAPI(access_token=access_token)

# track how many users we could get location from
publicUsers = 0

# initiates the .js data file
def initiateOutput():
    outputFile.write("var heatmapData = [")

# accepts a userID and gets the last location of the user based on recent photo, if available
def getLastLocation(userID):
    global publicUsers
    try:
        userFeed = api.user_recent_media(user_id=userID)[0]
        print "\nUser's feed contains: " + str(len(userFeed)) + " Media."

        #Search through a user's feed for location
        tries = 0
        for eachMedia in userFeed:
            if (tries >= MAXTRIES):
                break
            print "Checking for location in feed: " + str(eachMedia)
            try:
                print "Found location: " + str(api.media(eachMedia.id).location.point)
                #Conclude the last entry and prepare for the next
                if (publicUsers > 0):
                    outputFile.write("\n},")
                outputFile.write("\n{\n\tlat: " + str(api.media(eachMedia.id).location.point.latitude) + 
                        ",\n\tlon: " + str(api.media(eachMedia.id).location.point.longitude) + ",\n\t" +
                        "value: 1")
                publicUsers += 1
                break
            #handle error if media has no lat/long
            except AttributeError:
                pass
            sleep(2)
            tries += 1
    #handle error if user has whole profile private
    except InstagramAPIError as e:
        print "\nUser is set to private."

# concludes the .js data file
def concludeOutput():
    outputFile.write("\n}\n];")
    outputFile.close()
    #TODO: Add some legend data to the map

# copy the .js data file into leaflet source folder
def copyIntoLeaflet(leafletDirectory):
    copytree(workingDirectory + '/leaflet_source/',leafletDirectory)
    print "\nCopying heatmap data to Leaflet directory:\n" + leafletDirectory
    copy2(outputFile.name, leafletDirectory + 'maps/' + "heatmap-data.js")
    
initiateOutput()

# Determines the userID from the username given
userID = api.user_search(USERNAME)[0].id

# Get each follower of the user
followers, nextURL = api.user_followed_by(count = 100, user_id=userID) #count max is 100
totalFollowers = list(followers)
counter = 1

while nextURL and counter < (MAXPAGES): #paginate until there are no more URLs or counter limit is hit
    followers, nextURL = api.user_followed_by(count = 100, user_id=userID, with_next_url=nextURL)
    totalFollowers += list(followers)
    counter += 1
totalFollowers = tuple(totalFollowers) #convert back to immutable tuple
print "Found " + str(len(totalFollowers)) + " followers."
print "Finding most recent Lat/Long of each follower."
sleep(4)

# Now that we've got the followers, find their most recent photo
for eachFollower in totalFollowers:
    getLastLocation(eachFollower.id)
    sleep(2)
percentage = int(round(float(publicUsers) / len(totalFollowers) * 100))
print
print str(publicUsers) + " followers have location enabled (" + str(percentage) + "%) and " \
        + str(len(totalFollowers) - publicUsers) + " followers have no location."

concludeOutput()

leafletDirectory = workingDirectory + '/leaflet-' + USERNAME + '/'
copyIntoLeaflet(leafletDirectory)

print "\nSaved lat/long data to file:\n" + outputFile.name

# open leaflet heatmap
heatmapLocation = leafletDirectory + 'maps/heatmap.html'
open_new_tab("file://" + heatmapLocation)
#TODO: Make new leaflet directory by location name
#e.g. lflt-TheLinq
