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

#list = client.user.list_users(key)
#for user in list:
#    print user.get('login')

#ver = client.api.get_api_namespace_call_list(key,'api')
#ver = client.api.get_api_namespaces(key)
#ver = client.api.getApiNamespaces(key)
#print ver

#list = client.schedule.listInProgressActions(key)
#for action in list:
#    print action.get('id')
#    print action.get('name')
#    print action.get('type')
#    print action.get('scheduler')
#    print action.get('earliest')
#    print

# These next couple commented don't work
#ver = client.api.get_version(key)
#ver = client.api.getversion(key)

#print ver

list = client.taskomatic.listActiveSatSchedules(key)
print list

client.auth.logout(key)
