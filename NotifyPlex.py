#!/usr/bin/env python
#
##############################################################################
### NZBGET POST-PROCESSING SCRIPT                                          ###

# Post-Processing Script to Update Plex Library and Notify PHT.
#
# This script triggers a targeted library update to your Plex Media Server and sends a GUI Notification to Plex Home Theater.
# Auto-Detection of NZBGet category and Plex sections is now supported. This script also works with Plex Home enabled.
#
# Copyright (C) 2019 mannibis
# Version 3.0.0
#
#
# NOTE: This script is compatible to Python 3.8 and above.
# NOTE: If using VideoSort or other Sort/Rename Scripts, run NotifyPlex after those scripts have sorted/renamed your files.

##############################################################################
### OPTIONS                                                                ###

## General

# Use Silent Failure Mode (yes, no).
#
# Activate if you want NZBGet to report a SUCCESS status regardless of errors, in cases where PMS is offline.
#silentFailure=no

## Plex Media Server

# Refresh Plex Library (yes, no).
#
# Activate if you want NotifyPlex to refresh your Plex library
#refreshLibrary=no

# Plex.tv Username [Required to generate Plex Auth-Token]
#PlexUser=

# Plex.tv Password [Required to generate Plex Auth-Token]
#PlexPassword=

# Authorize script with Plex server [Required if refreshLibrary is enabled].
#
# Once authorized, it will be visible in your Plex server settings as "NotifyPlex"
# in the "Authorized Devices" section.
#PlexAuthorize@Generate Plex Auth-Token

# Auth-Token for this script.
#
# Use the above button to authorize this script with Plex.tv
# NOTE: The Password can be safely removing when setting the Auth-Token.
#PlexAuthToken=

# Plex Media Server Host.
#
# IP or hostname of your Plex Media Server including port (only 1 server is supported)
#PlexHost=192.168.1.XXX:32400

# Library Refresh Mode (Auto, Custom, Both).
#
# Select Refresh Mode: Auto will automatically detect your NZBGet category and refresh the appropriate sections, Custom will only refresh the sections you input into the Custom sections setting below, Both will auto-detect and refresh the Custom Sections
#refreshMode=Auto

# NZBGet Movies Category/Categories [Required for Auto Mode].
#
# List the name(s) of your NZBGet categories (CategoryX.Name) that correspond to Movies (comma separated)
#moviesCat=Movies

# NZBGet TV Category/Categories [Required for Auto Mode].
#
# List the name(s) of your NZBGet categories (CategoryX.Name) that correspond to TV Shows (comma separated)
#tvCat=TV

# Custom Plex Section(s) you would like to update [Optional].
#
# Section Number(s) corresponding to your Plex library (comma separated). These sections will only refreshed if Library Refesh Mode is set to Custom or Both
#customPlexSection=

### NZBGET POST-PROCESSING SCRIPT                                          ###
##############################################################################

import os
import sys
import urllib.parse
import urllib.request
from xml.etree.ElementTree import fromstring

POSTPROCESS_SUCCESS = 93
POSTPROCESS_ERROR = 94
POSTPROCESS_NONE = 95

def get_auth_token(username, password):
	auth_url = 'https://my.plexapp.com/users/sign_in.xml'
	auth_params = {'user[login]': username, 'user[password]': password}
	headers = {
		'X-Plex-Platform': 'NZBGet',
		'X-Plex-Platform-Version': '21.0',
		'X-Plex-Provides': 'controller',
		'X-Plex-Product': 'NotifyPlex',
		'X-Plex-Version': '2.1.3',
		'X-Plex-Device': 'NZBGet',
		'X-Plex-Client-Identifier': '12287'
	}

	try:
		data = urllib.parse.urlencode(auth_params).encode('utf-8')
		req = urllib.request.Request(auth_url, headers=headers, data=data, method='POST')
		
		with urllib.request.urlopen(req) as response:
			if response.getcode() != 201:
				return None

			root = fromstring(response.read())
			return root.attrib.get('authToken')
	except Exception as ex:
		print('[INFO] NOTIFYPLEX: Auto-refreshing Plex Library', ex)
		pass

	return None


def refresh_auto(movie_cats, tv_cats):
	print('[INFO] NOTIFYPLEX: Auto-refreshing Plex Library')
	movie_cats = movie_cats.replace(' ', '')
	movie_cats_split = movie_cats.split(',')
	tv_cats = tv_cats.replace(' ', '')
	tv_cats_split = tv_cats.split(',')

	try:
		url = 'http://%s/library/sections' % plex_host
		params = {'X-Plex-Token': plex_auth_token}
		full_url = url + '?' + urllib.parse.urlencode(params)
		
		req = urllib.request.Request(full_url)
		with urllib.request.urlopen(req, timeout=10) as response:
			if response.getcode() == 200:
				section_response = response.read()
				root = fromstring(section_response)
				plex_sections = {'movie': [], 'show': []}

				for directory in root.findall('Directory'):
					directory_type = directory.get('type')
					section_id = directory.get('key')
					if directory_type in plex_sections.keys():
						plex_sections[directory_type].append(section_id)

				if nzb_cat in tv_cats_split:
					refresh_sections(plex_sections['show'], plex_auth_token)
				elif nzb_cat in movie_cats_split:
					refresh_sections(plex_sections['movie'], plex_auth_token)
				else:
					if silent_mode:
						print('[WARNING] NOTIFYPLEX: Category "%s" is not configured as a section to be refreshed. '
							  'Silent failure mode active' % nzb_cat)
						sys.exit(POSTPROCESS_SUCCESS)
					else:
						print('[ERROR] NOTIFYPLEX: Category "%s" is not configured as a section to be refreshed.' % nzb_cat)
						sys.exit(POSTPROCESS_ERROR)
	except urllib.error.URLError as e:
		if silent_mode:
			print('[WARNING] NOTIFYPLEX: Failed auto-detecting Plex sections. Silent failure mode active')
			sys.exit(POSTPROCESS_SUCCESS)
		else:
			print('[ERROR] NOTIFYPLEX: Failed auto-detecting Plex sections. '
				  'Check Network Connection, Plex server settings, Auth-Token and section numbers.')
			print('[ERROR] NOTIFYPLEX: %s' % e)
			sys.exit(POSTPROCESS_ERROR)


def refresh_custom_sections(raw_custom_section_ids):
	print('[INFO] NOTIFYPLEX: Refreshing custom sections')
	custom_section_ids = raw_custom_section_ids.replace(' ', '')
	custom_section_ids = custom_section_ids.split(',')
	refresh_sections(custom_section_ids, plex_auth_token)


def refresh_sections(plex_sections, auth_token):
	params = {'X-Plex-Token': auth_token}

	for section_id in plex_sections:
		refresh_url = 'http://%s/library/sections/%s/refresh' % (plex_host, section_id)
		full_url = refresh_url + '?' + urllib.parse.urlencode(params)

		try:
			req = urllib.request.Request(full_url)
			with urllib.request.urlopen(req, timeout=10) as response:
				if response.getcode() == 200:
					print('[INFO] NOTIFYPLEX: Targeted Plex update for section %s complete' % section_id)
				else:
					raise urllib.error.URLError('HTTP Error: %d' % response.getcode())
		except urllib.error.URLError as e:
			if silent_mode:
				print('[WARNING] NOTIFYPLEX: Failed updating section %s. Silent failure mode active' % section_id)
				sys.exit(POSTPROCESS_SUCCESS)
			else:
				print('[ERROR] NOTIFYPLEX: Failed updating section %s. ' +
						'Check Network Connection, Plex server settings, Auth-Token and section numbers.' % section_id)
				print('[ERROR] NOTIFYPLEX: %s' % e)
				sys.exit(POSTPROCESS_ERROR)

NZBGetVersion = os.environ['NZBOP_VERSION']
if NZBGetVersion[0:5] < '11.1':
	print('[ERROR] This script requires NZBGet 11.1 or newer. Please update NZBGet')
	sys.exit(POSTPROCESS_ERROR)

required_options = ('NZBPO_SILENTFAILURE', 'NZBPO_REFRESHLIBRARY')
for optname in required_options:
	if optname not in os.environ:
		print('[ERROR] NOTIFYPLEX: Option %s is missing in configuration file. ' +
				'Please check script settings' % optname[6:])
		sys.exit(POSTPROCESS_ERROR)


refresh_library = os.environ['NZBPO_REFRESHLIBRARY'] == 'yes'
silent_mode = os.environ['NZBPO_SILENTFAILURE'] == 'yes'

# Check if the script is executed from settings page with a custom command
command = os.environ.get('NZBCP_COMMAND')
authorize_mode = command == 'PlexAuthorize'
if command is not None and not authorize_mode:
	print('[ERROR] NOTIFYPLEX: Invalid command ' + command)
	sys.exit(POSTPROCESS_ERROR)

if authorize_mode:
	required_options = ('NZBPO_PLEXUSER', 'NZBPO_PLEXPASSWORD')
	for optname in required_options:
		if optname not in os.environ:
			print('[ERROR] NOTIFYPLEX: Option %s is missing in configuration file. ' +
					'Please check script settings' % optname[6:])
			sys.exit(POSTPROCESS_ERROR)

	plex_username = os.environ['NZBPO_PLEXUSER']
	plex_password = os.environ['NZBPO_PLEXPASSWORD']
	plex_auth_token = get_auth_token(plex_username, plex_password)

	if plex_auth_token is not None:
		print('[INFO] Authorization to Plex.tv successful.')
		print('[INFO] Copy & paste into PlexAuthToken, then save and reload.')
		print('[INFO] Auth-Token: %s' % plex_auth_token)
		sys.exit(POSTPROCESS_SUCCESS)
	else:
		print('[ERROR] Authorization to Plex.tv failed. Please check your Username and Password.')
		sys.exit(POSTPROCESS_ERROR)

required_options = ('NZBPO_MOVIESCAT', 'NZBPO_PLEXAUTHTOKEN', 'NZBPO_PLEXHOST', 'NZBPO_REFRESHMODE', 'NZBPO_TVCAT')
for optname in required_options:
	if os.environ.get(optname) in (None, ''):
		print('[ERROR] NOTIFYPLEX: Option "%s" is missing or empty in configuration file. ' +
				'Please check script settings' % optname[6:])
		sys.exit(POSTPROCESS_ERROR)

raw_custom_section_ids = os.environ['NZBPO_CUSTOMPLEXSECTION']
movie_cats = os.environ['NZBPO_MOVIESCAT']
plex_auth_token = os.environ['NZBPO_PLEXAUTHTOKEN']
plex_host = os.environ['NZBPO_PLEXHOST']
refresh_mode = os.environ['NZBPO_REFRESHMODE']
tv_cats = os.environ['NZBPO_TVCAT']

# Get variables provided by NZBGet
nzb_cat = os.environ['NZBPP_CATEGORY']
nzb_name = os.environ['NZBPP_NZBNAME']
nzb_status = os.environ['NZBPP_STATUS']

# Check to see if download was successful
if nzb_status.startswith('SUCCESS/'):
	if refresh_library:
		if refresh_mode == 'Custom':
			refresh_custom_sections(raw_custom_section_ids)
		elif refresh_mode == 'Auto':
			refresh_auto(movie_cats, tv_cats)
		else:
			refresh_custom_sections(raw_custom_section_ids)
			refresh_auto(movie_cats, tv_cats)

	sys.exit(POSTPROCESS_SUCCESS)
else:
	print('[WARNING] NOTIFYPLEX: Skipping Plex update because download failed')
	sys.exit(POSTPROCESS_NONE)
