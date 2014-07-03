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
# TODO: Make variables

api = InstagramAPI(access_token=access_token)


