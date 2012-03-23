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
import sys
import pprint

import xbmcgui

import qobuz
from constants import Mode
from flag import NodeFlag
from node import Node
from cache.track import Cache_track
from cache.track_stream_url import Cache_track_stream_url
from debug import error, debug, warn
#from gettext import re
'''
    NODE TRACK
'''

class Node_track(Node):

    def __init__(self, parent = None, parameters = None):
        super(Node_track, self).__init__(parent, parameters)
        self.type = NodeFlag.TYPE_NODE | NodeFlag.TYPE_TRACK
        self.set_content_type('songs')
        self.qobuz_context_type = 'playlist'
        self.set_is_folder(False)
        self.cache = None
        self.cache_url = None

    def _build_down(self, xbmc_directory, lvl, flag = None):
        if flag & NodeFlag.DONTFETCHTRACK:
            return False
        else:
            self.set_cache(xbmc_directory.Progress)
            self.set_data(self.cache.fetch_data())
            xbmc_directory.add_node(self)
            return True

    def set_cache(self, progress = None):
        id = self.get_id()
        if not id:
            try:
                id = self.get_parameter('nid')
            except: pass
        if not id:
            error(self, "Cannot set cache without id")
            return False
        self.cache = Cache_track(id, self.qobuz_context_type, False)
        return True

    def make_url(self, mode = Mode.PLAY):
        return super(Node_track, self).make_url(mode)

    def get_label(self):
        return "%s - %s" % (self.get_artist(), self.get_title())

    def is_sample(self):
        streamtype = self.get_property('streamtype')
        if 'full' in streamtype:
            return True
        return False

    def get_composer(self):
        return self.db_row['composer_name']

    def get_interpreter(self):
        return self.db_row['interpreter_name']

    def get_album(self):
        return ''
        album = self.get_property(('album', 'title'))
        if album: return album
        if not self.parent: return ''
        if self.parent.get_type() & NodeFlag.TYPE_PRODUCT:
            return self.parent.get_title()
        return ''

    def get_image(self):
        image = self.get_property(('album', 'image', 'large'))
        image = self.db_row['image']
        if image: return image.replace('_230.', '_600.')
        if not self.parent: return ''
        if self.parent.get_type() & (NodeFlag.TYPE_PRODUCT | NodeFlag.TYPE_PLAYLIST):
            return self.parent.get_image()

    def get_playlist_track_id(self):
        return self.get_property(('playlist_track_id'))

    def get_streaming_type(self):
        if self.cache_url:
            return self.cache_url.get_data()['streaming_type']
        return self.get_property(('streaming_type'))

    def get_position(self):
        return self.get_property(('position'))

    def get_title(self):
        return self.db_row['title']

    def get_genre(self):
        genre = self.get_property(('album', 'genre', 'name'))
        if genre: return genre
        if not self.parent: return ''
        if self.parent.get_type() & NodeFlag.TYPE_PRODUCT:
            return self.parent.get_genre()
        return ''

    def get_streaming_url(self):
        self._set_cache_streaming_url()
        data = self.cache_url.get_data()
        if not data: return None
        return data['streaming_url']

    def get_artist(self):
        types = ['artist_name', 'interpreter_name', 'composer_name']
        for type in types:
            print "Type: " + type
            if type in self.db_row.keys() and self.db_row[type]:
                print "GABOUGGGGGGGGGGGGGGG"
                return self.db_row[type]
        return 'Unknow artist'

    def get_artist_id(self):
        #s = self.get_property(('artist', 'id'))
        s = self.db_row['artist_id']
        if s: return int(s)
        #s = self.get_property(('composer', 'id'))
        s = self.db_row['composer_id']
        if s: return int(s)
        s = self.db_row['interpreter_id']
        #s = self.get_property(('interpreter', 'id'))
        if s: return int(s)
        return None

    def get_track_number(self):
        data = self.db_row['track_number']
        print "TRACK NUMBER: " + str(data)
        return data
        #return self.get_property(('track_number'))

    def get_media_number(self):
        return self.db_row['media_number']
        #return self.get_property(('media_number'))

    def get_duration(self):
        #duration = self.get_property(('duration'))
        duration = self.db_row['duration']
        if duration:
            (sh, sm, ss) = duration.strip().split(':')
            return (int(sh) * 3600 + int(sm) * 60 + int(ss))
        return -1

    def get_year(self):
        date = self.db_row['release_date']
#        date = self.get_property(('album', 'release_date'))
        if not date and self.parent and self.parent.get_type() & NodeFlag.TYPE_PRODUCT:
            return self.parent.get_year()
        year = 0
        try: year = int(date.split('-')[0])
        except: pass
        return year

    def  get_description(self):
        if self.parent: return self.parent.get_description()
        return ''

    def _set_cache_streaming_url(self):
        if not self.cache_url:
            self.cache_url = Cache_track_stream_url(self.get_id())
        self.cache_url.fetch_data()

    def get_mimetype(self):
        self._set_cache_streaming_url()
        data = self.cache_url.get_data()
        if not data:
            warn(self, "Cannot get mime/type for track (network problem?)")
            return ''
        format = int(data['format_id'])
        mime = ''
        if format == 6:
            mime = 'audio/flac'
        else:
            mime = 'audio/mpeg'
        return mime

    def make_XbmcListItem(self):
        row = qobuz.db.get_track(self.id)
        if not row:
            warn(self, "Cannot make item without data")
            return None
        print "GOOOOOOOOOOOOOOOOT: " + pprint.pformat(row.keys())
        self.db_row = row
        media_number = self.get_media_number()
        if not media_number: media_number = 1
        else: media_number = int(media_number)
        duration = self.get_duration()
        label = self.get_label()
        isplayable = 'true'
        if self.get_streaming_type() == 'sample' or qobuz.gui.is_free_account():
            duration = 60
            label = '[COLOR=FF555555]' + label + '[/COLOR] [[COLOR=55FF0000]Sample[/COLOR]]'
        mode = Mode.PLAY
        url = self.make_url(mode)
        item = xbmcgui.ListItem(label,
                                label,
                                self.get_image(),
                                self.get_image(),
                                url)
        del self.db_row
        return item
        if not item:
            warn(self, "Cannot create xbmc list item")
            return None
        item.setPath(url)
        track_number = self.get_track_number()
        if not track_number: track_number = 0
        else: track_number = int(track_number)
        mlabel = self.get_property(('label', 'name'))
        description = self.get_description()
        comment = ''
        if mlabel: comment = mlabel
        if description: comment += ' - ' + description
        item.setInfo(type = 'music', infoLabels = {
                                   'track_id': self.get_id(),
                                   'title': self.get_title(),
                                   'album': self.get_album(),
                                   'genre': self.get_genre(),
                                   'artist': self.get_artist(),
                                   'tracknumber': track_number,
                                   'duration': duration,
                                   'year': self.get_year(),
                                   'comment': comment
                                   })
        item.setProperty('discnumber', str(media_number))
        item.setProperty('IsPlayable', isplayable)
        item.setProperty('IsInternetStream', isplayable)
        item.setProperty('Music', isplayable)
        self.attach_context_menu(item)
        return item

    def hook_attach_context_menu(self, item, menuItems):
        color = qobuz.addon.getSetting('color_item')
        if self.parent and self.parent.type & NodeFlag.TYPE_PLAYLIST:
            url = self.parent.make_url(Mode.PLAYLIST_REMOVE_TRACK) + '&track-id=' + str(self.get_property('playlist_track_id'))
            menuItems.append((qobuz.utils.color(color, "(i8n) Remove track: ") + self.get_label(), 'XBMC.RunPlugin("%s")' % (url)))

