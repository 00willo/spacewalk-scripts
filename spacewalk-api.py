#!/usr/bin/python

import xmlrpclib
import sys
import socket

SPACEWALK_URL = "http://spacewalk.host/rpc/api"
SPACEWALK_USERNAME = "user"
SPACEWALK_PASSWORD = "PASS"

# Set to 1 to see the XML and more
VERBOSE_LEVEL = 0

client = xmlrpclib.Server(SPACEWALK_URL, verbose=VERBOSE_LEVEL)


print('Attempting to connect to %s') % SPACEWALK_URL
try:
    key = client.auth.login(SPACEWALK_USERNAME, SPACEWALK_PASSWORD)
    print 'Login succeeded'
except xmlrpclib.Fault as e:
    print 'Failed Login'
    print "ERROR: Code:{0}.  String:{1}".format(err, strerr)
    sys.exit()
except socket.error as (err, strerr):
    print('ERROR: Code:{0}.  String:{1}').format(err, strerr)
    if err == 8:
        print('Seems like your hostname is incorrect.')
    sys.exit()

list = client.taskomatic.listActiveSatSchedules(key)
print list

client.auth.logout(key)
