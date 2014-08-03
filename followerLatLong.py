#!/usr/local/bin/python
# Application by Taylor Kline
# Gathers lat / long info on follwers from their most recently posted picture.
# Setting variables in ALL_CAPS is your responsibility.
from instagram.client import InstagramAPI
from instagram.bind import InstagramAPIError
import os
import errno
import httplib
from time import sleep
from time import localtime
from shutil import copy2,copytree
from webbrowser import open_new_tab

# reads access token from specified line in keyFile
ACCESS_TOKEN_LINE=1

# user specified variables to influence search
USERNAME = 'thelinq'
MAXPAGES = 19 #maximum number of approximately 100-user pages to process
# Note: This number is approximate, as some pages do not have the full 100 users
MAXTRIES = 7 #number of pictures to go through on users' timelines to attempt to find location
#upper limit is 20 pictures to go through

#Slow down the search to attempt to avoid rate limit?
SLEEPMODE = True

# track how many users we could get location from
publicUsers = 0

def main():
    initiateAPI()

    # Determines the userID from the username given
    userID = api.user_search(USERNAME)[0].id

    # generate files for writing
    outputJS = createDataFile("js")
    outputCSV = createDataFile("csv")

    initiateOutput(userID, outputJS)

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

    # Now that we've got the followers, find their most recent photo
    print "Finding most recent Lat/Long of each follower."
    sleep(4)
    for eachFollower in totalFollowers:
        saveLastLocation(outputJS, outputCSV, eachFollower.id)
    percentage = int(round(float(publicUsers) / len(totalFollowers) * 100))
    print
    print "==============================================="
    print str(publicUsers) + " followers have location enabled (" + str(percentage) + "%) and " \
            + str(len(totalFollowers) - publicUsers) + " followers have no location."

    concludeOutput(outputJS, outputCSV)

    workingDirectory = os.path.dirname(os.path.realpath(__file__))
    leafletDirectory = workingDirectory + '/leaflet-' + USERNAME + '/'
    copyIntoLeaflet(outputJS, leafletDirectory)

    print "\nSaved heatmap lat/long data to file:\n" + outputJS.name
    print "\nSaved lat/long CSV data to file:\n" + outputCSV.name

    # open leaflet heatmap
    heatmapLocation = leafletDirectory + 'heatmap.html'
    open_new_tab("file://" + heatmapLocation)

# initiates API from specified line in keyFile
def initiateAPI():
    keyFilename = 'keys'
    keyFile = open(keyFilename, 'r')
    for x in range (0,ACCESS_TOKEN_LINE-1):
        keyFile.readline()
    access_token = keyFile.readline().rstrip()
    global api
    api = InstagramAPI(access_token=access_token)

# output file to be used for html output and opened in web browser
def createDataFile(extension):
    currentTime = str(localtime().tm_year) + '-' + str(localtime().tm_mon) + '-' + str(localtime().tm_mday) + '-' + str(localtime().tm_hour) + '-' + str(localtime().tm_sec)
    workingDirectory = os.path.dirname(os.path.realpath(__file__))
    outputPath = workingDirectory + '/LatLongData/' + extension
    outputName = 'output_' + USERNAME + '_' + currentTime +  '.' + extension
    outputDirectory = workingDirectory + '/LatLongData/'
    try:
            os.makedirs(outputPath)
    except OSError as exception:
        if exception.errno != errno.EEXIST: raise
    return open(os.path.join(outputPath,outputName), 'w')

# initiates the .js data file
def initiateOutput(userID, outputJS):
    user = api.user(userID).username
    outputJS.write("var user = \"" + user + "\";\n")
    outputJS.write("var heatmapData = [")

# accepts a userID and gets the last location of the user based on recent photo, if available
def saveLastLocation(outputJS, outputCSV, userID):
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
                    outputCSV.flush()
                    outputJS.flush()
                    break
            #handle error if media has no lat/long
            except AttributeError:
                pass
            if SLEEPMODE: sleep(1)
            tries += 1
    #handle error if user has whole profile private
    except InstagramAPIError as e:
        if (e.status_code == 400):
            print "\nUser is set to private."
        #sometimes JSON screws up, proceed anyway
        elif (e.status_code == 502):
            pass
        else:
            raise
    #handle rare error with ResponseNotReady
    except httplib.ResponseNotReady:
        pass

# concludes the .js data file
def concludeOutput(outputJS, outputCSV):
    outputJS.write("\n}\n];\n")
    outputJS.write("var usersFound = \"" + str(publicUsers) + "\";\n")
    outputJS.close()
    outputCSV.close()

# copy the .js data file into leaflet source folder
def copyIntoLeaflet(outputJS, leafletDirectory):
    print "\nCreating a leaflet heatmap for " + USERNAME
    try:
        workingDirectory = os.path.dirname(os.path.realpath(__file__))
        copytree(workingDirectory + '/leaflet_source/',leafletDirectory)
    except OSError:
        print "Leaflet heatmap for " + USERNAME + " appears to already exist."
        print "Overwriting heatmap-data with newly gathered heatmap-data."
    print "\nCopying heatmap data to Leaflet directory:\n" + leafletDirectory
    copy2(outputJS.name, leafletDirectory + "/data/heatmap-data.js")
    
if __name__ == "__main__":
    main()
