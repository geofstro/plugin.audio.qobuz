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
import os
import sys
import xbmcplugin
import xbmcgui

from utils.icacheable import ICacheable
from debug import log, info, warn
from constants import *
from utils.tag import IQobuzTag, QobuzTagUserPlaylist
import qobuz
'''
    Class QobuzUserPLaylists
'''
class QobuzUserPlaylists(ICacheable):

    def __init__(self, Api, cache_path, cache_refresh):
        self.Api = Api
        super(QobuzUserPlaylists, self).__init__(
                                               cache_path,
                                               'userplaylists',
                                               0)
        self.set_cache_refresh(cache_refresh)
        self.fetch_data()

    def _fetch_data(self):
        raw_data = self.Api.get_user_playlists()
        data = []
        for p in raw_data:
            data.append(p['playlist'])
        return data

    def length(self):
        if not self._raw_data:
           return 0
        return len(self._raw_data)


class QobuzUserPlaylistsXbmc(QobuzUserPlaylists):
    def __init__(self):
        super(QobuzUserPlaylistsXbmc, self).__init__(
                qobuz.api,
                qobuz.path.cache,
                qobuz.addon.getSetting('cache_duration_userplaylist'))
    
    def get_image(self, name):
        return self.cacheImage.get('userplaylists', name.strip())
    
    def set_image_genre(self, name, image):
        return self.cacheImage.set('userplaylists', name , image)
    
    def get_items(self):
        i = 1
        list = []
        account_owner = qobuz.addon.getSetting('username')
        fanArt = qobuz.image.access.get('fanArt')
        for json_track in self.get_data():
            tag = QobuzTagUserPlaylist(json_track)
            u = qobuz.boot.build_url(MODE_PLAYLIST, tag.id)
            item = xbmcgui.ListItem(tag.name)
            owner = tag.owner_name
            if owner == account_owner: 
                owner = ''
            else: 
                owner += ' - '
            image = qobuz.image.cache.get('userplaylists', tag.name)
            if not image:
                image = qobuz.image.access.get('qobuzIcon')
            item.setThumbnailImage(image)
            item.setIconImage(image)
            item.setLabel(owner + tag.name)
            item.setInfo(type="Music",infoLabels={ "title": tag.name, "count": i })
            item.setProperty('Music','false')
            item.setProperty('IsPlayable','false');
            item.setProperty('fanart_image', fanArt)
            qobuz.gui.setContextMenu(item)
            list.append((u, item, True))
            i = i + 1
        return list
            

