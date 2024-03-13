#!/usr/bin/env python3
#
# Copyright (C) 2024 Denis <denis@nzbget.com>
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with the program.  If not, see <http://www.gnu.org/licenses/>.
#


import sys
from os.path import dirname
import os
import subprocess
import unittest
import http.server
import threading

POSTPROCESS_SUCCESS=93
POSTPROCESS_NONE=95
POSTPROCESS_ERROR=94

root = dirname(__file__)

plex_host = 'localhost'
plex_port = 4444
host = '127.0.0.1'
username = 'TestUser'
password = 'TestPassword'
port = '6789'

class MockServerRequestHandler(http.server.BaseHTTPRequestHandler):
	def do_GET(self):
		self.send_response(200)
		self.send_header('Content-type', 'text/xml')
		self.end_headers()
		response_content = (b'<?xml version="1.0" encoding="UTF-8"?>' +
		b'<MediaContainer size="3" allowSync="0" title1="Plex Library">' +
		b'<Directory allowSync="1" art="/:/resources/movie-fanart.jpg" ' +
		b'composite="/library/sections/2/composite/1709800247" filters="1" refreshing="0" '+
		b'thumb="/:/resources/movie.png" key="2" type="movie" title="Movies" agent="tv.plex.agents.movie" ' +
		b'scanner="Plex Movie" language="en-US" uuid="d495999b-6b8c-4676-9c1c-78e61175f0f5" ' +
		b'updatedAt="1709711552" createdAt="1709705968" scannedAt="1709800247" content="1" directory="1" contentChangedAt="1691" hidden="0">'
		b'<Location id="10" path="D:\Movies" />' +
		b'</Directory>' +
		b'<Directory allowSync="1" art="/:/resources/show-fanart.jpg" ' +
		b'composite="/library/sections/3/composite/1709799889" filters="1" refreshing="0" ' +
		b'thumb="/:/resources/show.png" key="3" type="show" title="Series" agent="tv.plex.agents.series" scanner="Plex TV Series" ' +
		b'language="en-US" uuid="b6df6bac-25d5-448b-9d81-a1ffa1d4db19" updatedAt="1709711531" createdAt="170">' +
		b'</Directory>' +
		b'</MediaContainer>')
		self.wfile.write(response_content)

def get_python(): 
	if os.name == 'nt':
		return 'python'
	return 'python3'

def run_script():
	sys.stdout.flush()
	proc = subprocess.Popen([get_python(), root + '/NotifyPlex.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=os.environ.copy())
	out, err = proc.communicate()
	proc.pid
	ret_code = proc.returncode
	return (out.decode(), int(ret_code), err.decode())

def set_defaults_env():
	# NZBGet global options
	os.environ['NZBOP_CONTROLPORT'] = port
	os.environ['NZBOP_CONTROLIP'] = host
	os.environ['NZBOP_CONTROLUSERNAME'] = username
	os.environ['NZBOP_CONTROLPASSWORD'] = password
	os.environ['NZBPP_TOTALSTATUS'] = 'SUCCESS'
	os.environ['NZBOP_VERSION'] = '23.0'
	os.environ['NZBPP_CATEGORY'] = 'Movies'

	# script options
	os.environ['NZBPO_SILENTFAILURE'] = 'no'
	os.environ['NZBPO_REFRESHLIBRARY'] = 'no'
	os.environ['NZBPO_PLEXUSER'] = 'user'
	os.environ['NZBPO_PLEXPASSWORD'] = 'password'
	os.environ['NZBPO_MOVIESCAT'] = 'Movies'
	os.environ['NZBPO_PLEXHOST'] = plex_host + ':' + str(plex_port)
	os.environ['NZBPO_REFRESHMODE'] = 'Both'
	os.environ['NZBPO_TVCAT'] = 'TV'
	os.environ['NZBPO_PLEXAUTHTOKEN'] = 'Token'
	os.environ['NZBPO_CUSTOMPLEXSECTION'] = 'Series'
	os.environ['NZBPP_NZBNAME'] = 'NzbName'
	os.environ['NZBPP_STATUS'] = 'SUCCESS/'


class Tests(unittest.TestCase):
	def test_refresh_auto(self):
		set_defaults_env()
		os.environ['NZBPO_REFRESHLIBRARY'] = 'yes'
		os.environ['NZBPO_REFRESHMODE'] = 'Auto'
		server = http.server.HTTPServer((plex_host, plex_port), MockServerRequestHandler)
		thread = threading.Thread(target=server.serve_forever)
		thread.daemon = True
		thread.start()
		[_, code, _] = run_script()
		server.shutdown()
		thread.join()
		self.assertEqual(code, POSTPROCESS_SUCCESS)
	
	def test_refresh_custom(self):
		set_defaults_env()
		os.environ['NZBPO_REFRESHLIBRARY'] = 'yes'
		os.environ['NZBPO_REFRESHMODE'] = 'Custom'
		server = http.server.HTTPServer((plex_host, plex_port), MockServerRequestHandler)
		thread = threading.Thread(target=server.serve_forever)
		thread.daemon = True
		thread.start()
		[_, code, _] = run_script()
		server.shutdown()
		thread.join()
		self.assertEqual(code, POSTPROCESS_SUCCESS)

	def test_refresh_both(self):
		set_defaults_env()
		os.environ['NZBPO_REFRESHLIBRARY'] = 'yes'
		os.environ['NZBPO_REFRESHMODE'] = 'Both'
		server = http.server.HTTPServer((plex_host, plex_port), MockServerRequestHandler)
		thread = threading.Thread(target=server.serve_forever)
		thread.daemon = True
		thread.start()
		[_, code, _] = run_script()
		server.shutdown()
		thread.join()
		self.assertEqual(code, POSTPROCESS_SUCCESS)


if __name__ == '__main__':
	unittest.main()
