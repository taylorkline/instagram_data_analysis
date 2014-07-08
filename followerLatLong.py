#!/usr/local/bin/python
# Application by Taylor Kline
# Gathers lat / long info on follwers from their most recently posted picture.
# Setting variables in ALL_CAPS is your responsibility.
from instagram.client import InstagramAPI
import os

# output file to be used for html output and opened in web browser
outputFilename = 'followers.data'
outputFile = open(outputFilename, 'w')

# reads access token from specified line in keyFile
ACCESS_TOKEN_LINE=6
keyFilename = 'keys'
keyFile = open(keyFilename, 'r')
for x in range (0,ACCESS_TOKEN_LINE-1):
    keyFile.readline()
access_token = keyFile.readline().rstrip()

# user specified variables to influence search
USERNAME = 'thelinq'
MAXPAGES = 100 #maximum number of approximately 100-user pages to process
# Note: This number is approximate, as some pages do not have the full 100 users

api = InstagramAPI(access_token=access_token)

# accepts a userID and gets the last location of the user based on recent photo, if available
def getLastLocation(userID):
    try:
        userFeed = api.user_recent_media(user_id=userID)[0]
        #TODO: get lat / long of most recent user feed
        print userFeed
    except Exception:
        print "User is set to private."

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
# TODO: Print (out of xxxx followers)

# Now that we've got the followers, find their most recent photo
for eachFollower in totalFollowers:
    getLastLocation(eachFollower.id)

    #TODO: Print out stats of how many followers there are vs how much location data is available
