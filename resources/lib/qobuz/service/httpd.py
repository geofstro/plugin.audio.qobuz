#import string,cgi,time
#from os import curdir, sep
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import socket
import re
import sys
import urllib2

VERSION = '0.0.1'

username = password = base_path = stream_type = stream_format = None
cache_duration_long = 60*60*24*365
cache_duration_middle = 60*60*24*365
stream_format = 5
__image__ = ''


import xbmcaddon, xbmcplugin, xbmc

import os
pluginId = 'plugin.audio.qobuz'
__addon__ = xbmcaddon.Addon(id=pluginId)
__addonversion__ = __addon__.getAddonInfo('version')
__addonid__ = __addon__.getAddonInfo('id')
__cwd__ = __addon__.getAddonInfo('path')
__addondir__ = __addon__.getAddonInfo('path')
__libdir__ = xbmc.translatePath(os.path.join(__addondir__, 'resources', 'lib'))
__qobuzdir__ = xbmc.translatePath(os.path.join(__libdir__, 'qobuz'))
sys.path.append(__libdir__)
sys.path.append(__qobuzdir__)

from bootstrap import QobuzBootstrap
__handle__ = -1
boot = QobuzBootstrap(__addon__, __handle__)
boot.bootstrap_directories()

def try_get_settings():
    global username, password
    username = __addon__.getSetting('username')
    password = __addon__.getSetting('password')
    if username and password:
        return True
    return False

while not (try_get_settings()):
    xbmc.sleep(5000)
        # raise Exception("Missing Mandatory Parameter")

print "USERNAME %s " % (username)
import qobuz
from api import api
from cache import cache
cache.base_path = qobuz.path.cache
api.login(username, password)


stream_format = 6 if __addon__.getSetting('streamtype') == 'flac' else 5
cache_durationm_middle = int(__addon__.getSetting('cache_duration_middle')) * 60
cache_duration_long = int(__addon__.getSetting('cache_duration_long')) * 60

if stream_format == 6:
    stream_mime = 'audio/flac'
else:
    stream_mime = 'audio/mpeg'
    
from debug import log
from node import getNode, Flag


class XbmcAbort(Exception):
    def __init__(self, *a, **ka):
        super(XbmcAbort, self).__init__(*a, **ka)
 
class BadRequest(Exception):
    def __init__(self, *a, **ka):
        self.code = 400
        self.message = 'Bad Request '
        super(BadRequest, self).__init__(*a, **ka)
               
class Unauthorized(Exception):
    def __init__(self, *a, **ka):
        self.code = 401
        self.message = 'Unauthorized '
        super(Unauthorized, self).__init__(*a, **ka)

class RequestFailed(Exception):
    def __init__(self, *a, **ka):
        self.code = 402
        self.message = 'Request Failed'
        super(RequestFailed, self).__init__(*a, **ka)
        
class ServerErrors(Exception):
    def __init__(self, *a, **ka):
        self.code = 500
        self.message = 'Server errors'
        super(ServerErrors, self).__init__(*a, **ka)

class QobuzResponse:
    
    def __init__(self, request):
        self.request = request
        if not self.__parse_path(request.path):
            raise RequestFailed()

    @property
    def path(self):
        return self._path
    @path.getter
    def path(self):
        return self._path
    @path.setter
    def path(self, value):    
        self.reset_request()
        self.__parse_path(value)
        self._path = value

    def reset_request(self):
        self.path = None
        self.request = None
        self.fileExt = None
        self.track_id = None
        self.album_id = None
        self.artist_id = None
        self.fileWanted = None

    def __parse_path(self, path):
        m = re.search('^/qobuz/(\d+)/(.*)$', path)
        if not m:
            return False
        self.artist_id = m.group(1)
        print "ArtistID: %s" % (str(self.artist_id))
        if m.group(2) == 'artist.nfo':
            self.fileWanted = 'artist.nfo'
            return True
        m = re.search('^(\d+)/(.*)$', m.group(2))
        if not m:
            return False
        self.album_id = m.group(1)
        print "AlbumID: %s" % (str(self.album_id))
        if m.group(2) == 'album.nfo':
            self.fileWanted = 'album.nfo'
            print "Serve album.nfo"
            return True
        if not m.group(2):
            self.fileWanted = 'dir'
            return True
        m = re.search('^(\d+|cdart)\.(mp3|mpc|flac|png)', m.group(2))
        if not m:
            return False
        if m.group(1) == 'cdart':
            print "GOT COVER ???"
            self.fileWanted = 'cover'
            self.fileExt = 'png'
            return True
        self.track_id = m.group(1)
        self.fileExt = m.group(2)
        self.fileWanted = 'music'
#        print "TrackID: %s" % (self.track_id)
        return True
    
class QobuzHttpResolver_Handler(BaseHTTPRequestHandler):

    def __init__(self, request, client_address, server):
        BaseHTTPRequestHandler.__init__(self, request, client_address, server)
        self.server_version = 'QobuzXbmcHTTP/0.0.1'

    def __write_album_nfo(self, node):
        w = self.wfile
        w.write("<album>")
        w.write(u"<title>"+node.get_label()+u"</title>")
        w.write(u"<artist>"+node.get_artist()+u"</artist>")
        w.write("<genre>"+node.get_genre()+"</genre>")
        w.write("<year>"+node.get_year()+"</year>")
        w.write("<thumb>"+node.get_image()+"</thumb>")
        w.write("</album>")
        w.close()

    def __write_dir(self, node):
        w = self.wfile
        for track in node.data['tracks']['items']:
            ntrack = getNode(Flag.TRACK, {'parent': node})
            ntrack.data = track
            w.write(str(ntrack.get_track_number()) + ' - ' + ntrack.get_artist() + '- ' + ntrack.get_label() + '.flac<br>\n')
        w.close()
    
    def __GET_track(self, request):
        api.login(api.username, api.password)
        node = getNode(Flag.TRACK, {'nid': request.track_id})
        streaming_url = node.get_streaming_url()
        if not streaming_url:
            raise RequestFailed()
        self.send_response(303, "Resolved")
        self.send_header('content-type', stream_mime)
        self.send_header('location', streaming_url)
        self.end_headers()
        
    def __GET_cover(self, request):
        node = getNode(Flag.ALBUM, {'nid': request.album_id})
        node.fetch(None, None, None, None)
        self.send_response(200, "Ok")
        self.send_header('content-type', 'image/png')
        self.end_headers()
        self.wfile.write(urllib2.urlopen(node.get_image()).read())
        self.wfile.close()
        return True
        
    def __GET_album_nfo(self, request):
        print "Serving album.nfo for %s" % (request.album_id)
        node = getNode(Flag.ALBUM, {'nid': request.album_id})
        if not node.fetch(None, None, None, Flag.NONE):
            raise RequestFailed()
        self.send_response(200, "Ok")
        self.send_header('content-type', 'text/html')
        self.end_headers()
        self.__write_album_nfo(node)
        return True
    
    def __GET_dir(self, request):
        print "Serving dir for %s" % (request.album_id)
        node = getNode(Flag.ALBUM, {'nid': request.album_id})
        if not node.fetch(None, None, None, Flag.NONE):
            raise RequestFailed()
        self.send_response(200, "Ok")
        self.send_header('content-type', 'x-directory/normal')
        self.end_headers()
        self.__write_dir(node)
        return True        
    
    def do_GET(self):
        try:
            request = QobuzResponse(self)
            if request.fileWanted == 'dir':
                return self.__GET_dir(request)
            elif request.fileWanted == 'album.nfo':
                return self.__GET_album_nfo(request)
            elif request.fileWanted == 'cover':
                return self.__GET_cover(request)
            elif request.fileWanted == 'music':
                return self.__GET_track(request)
            else:
                raise BadRequest()
        except BadRequest as e:
            self.send_error(e.code, e.message)
        except Unauthorized as e:
            self.send_error(e.code, e.message)
        except RequestFailed as e:
            self.send_error(e.code, e.message)
        except Exception as e:
            msg = 'Server errors (%s / %s)\n%s' % (
                                                  sys.exc_type, sys.exc_value,
                                                  repr(e))
            self.log_message(msg)
            self.send_error(500, msg)

    def do_HEAD(self):
        try:
            request = QobuzResponse(self)
            if request.fileWanted == 'dir':
                self.send_response(200, "Ok ;)")
                self.send_header('content-type', 'x-directory/normal')
                self.end_headers()
                return True
            elif request.fileWanted == 'album.nfo':
                    self.send_response(200, "Ok ;)")
                    self.send_header('content-type', 'text/html')
                    self.end_headers()
                    return True
            elif request.fileWanted == 'cover':
                    self.send_response(200, "Ok ;)")
                    self.send_header('content-type', 'image/png')
                    self.send_header('content-length', 1024)
                    self.end_headers()
                    return True
            elif request.fileWanted == 'music':
                self.send_response(200, "Ok ;)")
                self.send_header('content-type', stream_mime)
                self.end_headers()
                return True
            else:
                raise BadRequest()
        except BadRequest as e:
            self.send_error(e.code, e.message)
        except Unauthorized as e:
            self.send_error(e.code, e.message)
        except RequestFailed as e:
            self.send_error(e.code, e.message)
        except socket.error:
            print "Socket error..."
        except Exception as e:
            msg = 'Server errors (%s / %s)\n%s' % (
                                                  sys.exc_type, sys.exc_value,
                                                  repr(e))
            self.log_message(msg)
            self.send_error(500, msg)

class QobuzHttpResolver(HTTPServer):

    def __init__(self, server_address, RequestHandlerClass):
        self.alive = True
        HTTPServer.__init__(self, server_address, RequestHandlerClass)
    
    def get_request(self):
        """Get the request and client address from the socket."""
        # 10 second timeout

        self.socket.settimeout(2.0)
        result = None
        while result is None:
            print "Waiting for request"
            if not self.alive:
                self.shutdown()
                raise KeyboardInterrupt()
            try:
                result = self.socket.accept()
            except socket.timeout:
                pass
        # Reset timeout on the new socket
        result[0].settimeout(None)
        return result

    def verify_request(self, path, client_address): 
        host, port = client_address
        if host == '127.0.0.1': 
            return True
        return False

import threading

class MonitorThread(threading.Thread, xbmc.Monitor):

    def __init__(self, httpd):        
        self._stopevent = threading.Event()
        threading.Thread.__init__(self)
        xbmc.Monitor.__init__(self)
        self.httpd = httpd
        self.alive = True

    def run(self):
        while self.alive:
            self._stopevent.wait(2)
        self.httpd.shutdown()

    def onAbortRequested(self):
        self.alive = True

class QobuzXbmcHttpResolver(QobuzHttpResolver):

    def __init__(self):
        self.monitor = MonitorThread(self)
        self.monitor.setDaemon(True)
        self.monitor.start()
        QobuzHttpResolver.__init__(self, ('127.0.0.1', 33574), 
                                                    QobuzHttpResolver_Handler)

def main():
    server = None
    try:
        server = QobuzXbmcHttpResolver()
        log(server, 'Qobuz http resolver Starting...')
        server.serve_forever()
    except KeyboardInterrupt:
        print '^C received, shutting down server'
    except XbmcAbort:
        log(server, 'Received xbmc abort... closing')
    finally:
        if server:
            server.socket.close()
            server = None

if __name__ == '__main__':
    main()
