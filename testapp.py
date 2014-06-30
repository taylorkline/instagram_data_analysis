#!/usr/local/bin/python
from instagram.client import InstagramAPI

keyFilename = 'keys'
keyFile = open(keyFilename, 'r')
#access token is on 6th line
for x in range (0,5):
    keyFile.readline()
access_token = keyFile.readline().rstrip()

# Displays the url of all popular images
api = InstagramAPI(access_token=access_token)
popular_media = api.media_popular(count=20)
for media in popular_media:
    print media.images['standard_resolution'].url
