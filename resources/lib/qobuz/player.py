#     Copyright 2011 Joachim Basmaison, Cyril Leclerc
#
#     This file is part of xbmc-qobuz.
#
#     xbmc-qobuz is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     xbmc-qobuz is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.   See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with xbmc-qobuz.   If not, see <http://www.gnu.org/licenses/>.

import xbmc
import xbmcplugin
import xbmcgui

import qobuz
from debug import warn, debug, log
from gui.util import notifyH, isFreeAccount, lang

from node.track import Node_track


class QobuzPlayer(xbmc.Player):

    def __init__(self, *a, **ka):
        ka['type'] = xbmc.PLAYER_CORE_AUTO
        super(QobuzPlayer, self).__init__()
        self.track_id = None
        self.total = None
        self.elapsed = None

    def sendQobuzPlaybackEnded(self, track_id, total, elapsed):
        duration = (total - elapsed) / 10
        if not (track_id and total and duration):
            return False
        # self.sendQobuzPlaybackEnded(self.track_id, (self.total -
        # self.elapsed) / 10)
        print "PLAYBACK END"
        qobuz.api.report_streaming_stop(track_id, duration)

    def onPlayBackEnded(self):
        if not (self.track_id and self.total and self.elapsed):
            return False
        self.sendQobuzPlaybackEnded(
            self.track_id, (self.total - self.elapsed) / 10)
        return True

    def OnQueueNextItem(self):
        return True

    def onPlayBackStopped(self):
        if not (self.track_id and self.total and self.elapsed):
            return False
        self.sendQobuzPlaybackEnded(
            self.track_id, (self.total - self.elapsed) / 10)
        return True

    def onPlaybackStarted(self):
        print "PLAYBACK STARTED"

    def play(self, ID):
        node = Node_track()
        node.id = ID
        xbmcgui.Window(10000).setProperty("NID",ID) 
        data = qobuz.registry.get(name='track', id=ID)['data']
        label = None
        item = None
        if not data:
            warn(self, "Cannot get track data")
            label = "Maybe an invalid track id"
            item = xbmcgui.ListItem("No track information",
                                    '',
                                    '',
                                    '',
                                    '')
        else:
            node.data = data
            item = node.make_XbmcListItem()
        mimetype = node.get_mimetype()
        if not mimetype:
            warn(self, "Cannot get track stream url")
            return False
        item.setProperty('mimetype', mimetype)
        # print 'Mime: ' + mimetype
        streaming_url = node.get_streaming_url()
        # some tracks are not authorized for stream and a 60s sample is
        # returned, in that case we overwrite the song duration
        if node.is_sample():
            item.setInfo(
                'music', infoLabels={
                'duration': 60,
                })
            # don't warn for free account (all songs except purchases are 60s
            # limited)
            if not isFreeAccount():
                notifyH("Qobuz", "Sample returned")
        item.setPath(streaming_url)
        '''
            PLaying track
        '''
        if qobuz.addon.getSetting('notification_playingsong') == 'true':
            notifyH(lang(34000), node.get_label(), node.get_image())

        '''
            We are called from playlist...
        '''

        if qobuz.boot.handle == -1:
            super(QobuzPlayer, self).play(streaming_url, item, False)
        else:
            xbmcplugin.setResolvedUrl(
                handle=qobuz.boot.handle,
                succeeded=True,
                listitem=item)

        #'''
        #    Waiting for song to start
        #'''
        #timeout = 10
        #debug(self, "Waiting song to start")
        #while timeout > 0:
        #    if not self.isPlayingAudio() or self.getPlayingFile() != streaming_url:
        #        xbmc.sleep(250)
        #        timeout -= 0.250
        #    else:
        #        break
        #if timeout <= 0:
        #    warn(self, "Player can't play track: " + item.getLabel())
        #    return False
        #return self.watch_playing(node, streaming_url)

    def isPlayingAudio(self):
        try:
            return super(QobuzPlayer, self).isPlayingAudio()
        except:
            warn(self, "EXCEPTION: isPlayingAudio")
        return False

    def getPlayingFile(self):
        try:
            return super(QobuzPlayer, self).getPlayingFile()
        except:
            warn(self, "EXCEPTION: getPlayingFile")
        return None

    def getTotalTime(self):
        try:
            return super(QobuzPlayer, self).getTotalTime()
        except:
            warn(self, "EXCEPTION: getTotalTime")
        return -1

    def watch_playing(self, node, streaming_url):
        start = None
        self.elapsed = None
        self.total = self.getTotalTime()
        while self.isPlayingAudio() and self.getPlayingFile() == streaming_url:
            log(self, 'Watching playback')
            self.elapsed = self.getTime()
            if not start and self.elapsed >= 5:
                self.sendQobuzPlaybackStarted(node.id)
                start = True
            xbmc.sleep(500)
        self.sendQobuzPlaybackEnded(node.id, self.total, self.elapsed)
        return True
