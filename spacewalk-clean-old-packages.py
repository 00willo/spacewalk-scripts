#!/usr/bin/python
# Script that uses RHN API to cleanup obsolete packages
# on Spacewalk server.
# Copyright (C) 2012  Nicolas PRADELLES
#
# Author: Nicolas PRADELLES (npradelles@eutelsat.fr)
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
#
# Version Information:
# 0.2 - 2012-08-27 - Script rewritten in Python to access Spacewalk XML RPC API
# 0.1 - 2012-04-17 - First Release


import xmlrpclib
import string
import os
import socket
import sys

# CONFIG
## URL of Spacewalk XML RPC server
SPACEWALK_URL = 'http://SPACEWALK-SRV/rpc/api'
## User with Org Admin role (required to delete package in Spacewalk)
SPACEWALK_USERNAME = 'XXXX'
SPACEWALK_PASSWORD = 'YYYY'

# Set to 1 to see the XML and more
VERBOSE_LEVEL = 0

# Open connection to XML RPC server
client = xmlrpclib.Server(SPACEWALK_URL, verbose=VERBOSE_LEVEL)
print('Attempting to connect to {}').format(SPACEWALK_URL)
try:
    key = client.auth.login(SPACEWALK_USERNAME, SPACEWALK_PASSWORD)
    print('Login succeeded')
except xmlrpclib.Fault as err:
    print('Failed Login')
    print('ERROR code: {}').format(err.faultCode)
    print('Message: {}').format(err.faultString)
    sys.exit()
except socket.error as (err, strerr):
    print('ERROR Code: {0}\tString: {1}').format(err, strerr)
    if err == 8:
        print('Seems like your hostname is incorrect.')
    sys.exit()

# extract spacewalk channels
list = client.channel.listAllChannels(key)

all_del_pkg = 0

# For each channel
for channel in list:
  print('################')
  print('{}').format(channel.get('label'))
  print('################')


  # extract all packages in channel
  print('### Getting list of all packages from channel')
  all_array = client.channel.software.listAllPackages(key, channel.get('label'))
  # extract latest packages in channel
  print('### Getting list of latest packages from channel')
  lst_array = client.channel.software.listLatestPackages(key, channel.get('label'))


  # Extract useful datas to find obsolete packages
  all_pkg = ()
  lst_pkg = ()

  # create a unique string to define a package, exemple:  java-1.6.0-sun-jdbc%1.6.0.31%1jpp.1.el6_2%58920
  for pkg in all_array:
    all_pkg = all_pkg + (pkg.get('name') + '%' + pkg.get('version') + '%' + pkg.get('release') + '%' + str(pkg.get('id')),)
  print('Packages in channel: {}').format(str(len(all_pkg)))
  
  for pkg in lst_array:
    lst_pkg = lst_pkg + (pkg.get('name') + '%' + pkg.get('version') + '%' + pkg.get('release') + '%' + str(pkg.get('id')),)


  # diff the two lists to find obsolete packages
  print('### Determining list of obsolete packages')
  old_pkg = set(all_pkg) - set(lst_pkg)

  del_pkg = 0

  # if we have found obsolete packages
  if len(old_pkg) > 0:
    print('### Processing list of obsolete packages')
    for pkg in old_pkg:
      pkg_params = string.split(pkg, '%')
      # check if the old package is installed on a managed client
      systems = client.system.listSystemsWithPackage(key, pkg_params[0], pkg_params[1], pkg_params[2])

      # if this package is not installed on a managed client
      if len(systems) == 0:
        # delete the package
        print('{0}-{1}').format(pkg_params[0], pkg_params[1])
        client.packages.removePackage(key, int(pkg_params[3]))
        del_pkg += 1

  all_del_pkg += del_pkg

  print('\nChannel cleanup summary')
  print('all: {0}, latest: {1}, old: {2}, deleted: {3}\n').format(str(len(all_pkg)), str(len(lst_pkg)), str(len(old_pkg)), str(del_pkg))


# Delete rpm files on disk
if all_del_pkg > 0:
  print('################\n\n')
  print('Cleaning up RPM files from filesystem')
  os.system('spacewalk-data-fsck -r -S -C -O')

print('Closing connection to {}').format(SPACEWALK_URL)
# disconnect
client.auth.logout(key)
