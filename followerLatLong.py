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

# reads access token from specified line in keyFile
ACCESS_TOKEN_LINE=1
keyFilename = 'keys'
keyFile = open(keyFilename, 'r')
for x in range (0,ACCESS_TOKEN_LINE-1):
    keyFile.readline()
access_token = keyFile.readline().rstrip()

# user specified variables to influence search
USERNAME = 'thelinq'
MAXPAGES = 10 #maximum number of approximately 100-user pages to process
# Note: This number is approximate, as some pages do not have the full 100 users
MAXTRIES = 5 #number of pictures to go through on users' timelines to attempt to find location
#upper limit is 20 pictures to go through

# output file to be used for html output and opened in web browser
currentTime = str(localtime().tm_year) + '-' + str(localtime().tm_mon) + '-' + str(localtime().tm_mday) + '-' + str(localtime().tm_hour) + '-' + str(localtime().tm_sec)
outputFilename = 'output_' + USERNAME + '_' + currentTime +  '.js'
outputDirectory = os.path.dirname(os.path.realpath(__file__)) + '/LatLongData/'
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
"""
Example lat/long search:
print api.media('762502306767443277_398424740').location.point.latitude
print api.media('762502306767443277_398424740').location.point.longitude
"""
def getLastLocation(userID):
    global publicUsers
    try:
        userFeed = api.user_recent_media(user_id=userID)[0]
        print "\nUser's feed contains: " + str(len(userFeed)) + " Media."

        #Search through a user's feed for location
        tries = 0
        for index in userFeed:
            if (tries >= MAXTRIES):
                break
            print "Checking index of feed: " + str(index)
            try:
                print "Found location: " + str(api.media(index.id).location.point)
                #Conclude the last entry and prepare for the next
                if (publicUsers > 0):
                    outputFile.write("\n},")
                outputFile.write("\n{\n\tlat: " + str(api.media(index.id).location.point.latitude) + 
                        ",\n\tlon: " + str(api.media(index.id).location.point.longitude) + ",\n\t" +
                        "value: 1")
                outputFile.flush()
                publicUsers += 1
                break
            #handle error if media has no lat/long
            except AttributeError:
                pass
            tries += 1
    #handle error if user has whole profile private
    except InstagramAPIError as e:
        print "\nUser is set to private."
    """
    #this error shouldn't be encountered anymore
    except IndexError:
        #TODO: Avoid IndexError with while loop
        pass
    """

# concludes the .js data file
def concludeOutput():
    outputFile.write("\n}\n];")
    outputFile.close()

initiateOutput()
print "Saving lat/long data to file:\n" + outputFile.name

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
percentage = int(round(float(publicUsers) / len(totalFollowers) * 100))
print str(publicUsers) + " followers have location enabled (" + str(percentage) + "%) and " \
        + str(len(totalFollowers) - publicUsers) + " followers have no location."

concludeOutput()
