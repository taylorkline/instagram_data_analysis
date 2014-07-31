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
MAXTRIES = 1 #number of pictures to go through on users' timelines to attempt to find location
#upper limit is 20 pictures to go through

#Slow down the search to attempt to avoid rate limit?
SLEEPMODE = False

# output file to be used for html output and opened in web browser
currentTime = str(localtime().tm_year) + '-' + str(localtime().tm_mon) + '-' + str(localtime().tm_mday) + '-' + str(localtime().tm_hour) + '-' + str(localtime().tm_sec)
workingDirectory = os.path.dirname(os.path.realpath(__file__))
outputJSpath = workingDirectory + '/LatLongData/JS'
outputJSname = 'output_' + USERNAME + '_' + currentTime +  '.js'
outputCSVpath = workingDirectory + '/LatLongData/csv'
outputCSVname = 'output_' + USERNAME + '_' + currentTime +  '.csv'
outputDirectory = workingDirectory + '/LatLongData/'
try:
        os.makedirs(outputJSpath)
        os.makedirs(outputCSVpath)
except OSError as exception:
    if exception.errno != errno.EEXIST: raise
outputJS = open(os.path.join(outputJSpath,outputJSname), 'w')
outputCSV = open(os.path.join(outputCSVpath,outputCSVname), 'w')

# initiate the api
api = InstagramAPI(access_token=access_token)

# track how many users we could get location from
publicUsers = 0

# initiates the .js data file
def initiateOutput():
    outputJS.write("var user = \"" + USERNAME + "\";")
    outputJS.write("var heatmapData = [")

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
                username = eachMedia.user.username
                userPoint = api.media(eachMedia.id).location.point
                userLat = userPoint.latitude
                userLong = userPoint.longitude

                #Sometimes a valid, yet empty, point is returned with value "none." Treat as error.
                if not userPoint: raise(AttributeError)
                else:
                    print "Found location: " + str(userPoint)
                    #Conclude the last entry and prepare for the next
                    outputCSV.write(username + ", " + str(userLat) + ", " + str(userLong) +"\n")
                    if (publicUsers > 0):
                        outputJS.write("\n},")
                    outputJS.write("\n{\n\tlat: " + str(userLat) + 
                            ",\n\tlon: " + str(userLong) + ",\n\t" +
                            "value: 1")
                    publicUsers += 1
                    break
            #handle error if media has no lat/long
            except AttributeError:
                pass
            if SLEEPMODE: sleep(2)
            tries += 1
    #handle error if user has whole profile private
    except InstagramAPIError as e:
        print "\nUser is set to private."

# concludes the .js data file
def concludeOutput():
    outputJS.write("\n}\n];")
    outputJS.write("var usersFound = \"" + str(publicUsers) + "\";")
    outputJS.close()
    outputCSV.close()

# copy the .js data file into leaflet source folder
def copyIntoLeaflet(leafletDirectory):
    print "\nCreating a leaflet heatmap for " + USERNAME
    try:
        copytree(workingDirectory + '/leaflet_source/',leafletDirectory)
    except OSError:
        print "Leaflet heatmap for " + USERNAME + " appears to already exist."
        print "Overwriting heatmap-data with newly gathered heatmap-data."
    print "\nCopying heatmap data to Leaflet directory:\n" + leafletDirectory
    copy2(outputJS.name, leafletDirectory + "/data/heatmap-data.js")
    
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
#Note: not possible to say "out of xxxx followers"
print "Finding most recent Lat/Long of each follower."
sleep(4)

# Now that we've got the followers, find their most recent photo
for eachFollower in totalFollowers:
    getLastLocation(eachFollower.id)
    if SLEEPMODE: sleep(2)
percentage = int(round(float(publicUsers) / len(totalFollowers) * 100))
print
print "==============================================="
print str(publicUsers) + " followers have location enabled (" + str(percentage) + "%) and " \
        + str(len(totalFollowers) - publicUsers) + " followers have no location."

concludeOutput()

leafletDirectory = workingDirectory + '/leaflet-' + USERNAME + '/'
copyIntoLeaflet(leafletDirectory)

print "\nSaved heatmap lat/long data to file:\n" + outputJS.name
print "\nSaved lat/long CSV data to file:\n" + outputCSV.name

# open leaflet heatmap
heatmapLocation = leafletDirectory + 'heatmap.html'
open_new_tab("file://" + heatmapLocation)
