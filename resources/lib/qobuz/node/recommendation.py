# -*- coding: UTF-8 -*-
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
import xbmcgui

import qobuz
from flag import NodeFlag as Flag
from node import Node
from product import Node_product
from debug import warn
from gui.util import color, lang, getImage

RECOS_TYPE_IDS = {
    1: 'new-releases',
    2: 'press-awards',
    3: 'best-sellers',
    4: 'editor-picks',
    5: 'most-featured'
}

RECOS_TYPES = {
    1: lang(30084),
    2: lang(30083),
    3: lang(30085),
    4: lang(30086),
    5: lang(30102),
}

RECOS_GENRES = {
    2: lang(30093),
    10: lang(30095),
    6: lang(30090),
    59: lang(30098),
    73: lang(30201),
    80: lang(30089),
    64: lang(30202),
    91: lang(30094),
    94: lang(30092),
    112: lang(30087),
    127: lang(30200),
    123: lang(30203),
    'null': 'All',
}
'''
    NODE RECOS
'''


class Node_recommendation(Node):

    def __init__(self, parent=None, parameters=None):
        super(Node_recommendation, self).__init__(parent, parameters)
        self.type = Flag.NODE | Flag.RECOMMENDATION
        self.genre_id = self.get_parameter('genre-id')
        self.genre_type = self.get_parameter('genre-type')
        self.set_label(lang(30082))
        self.image = getImage('album')
        self.offset = self.get_parameter('offset') or 0

    def make_url(self, **ka):
        url = super(Node_recommendation, self).make_url(**ka)
        if self.genre_type:
            url += '&genre-type=' + str(self.genre_type)
        if self.genre_id:
            url += '&genre-id=' + str(self.genre_id)
        return url

    def myid(self):
        if not self.genre_id or not self.genre_type:
            return None
        return str(self.genre_type) + '-' + str(self.genre_id)

    def pre_build_down(self, xbmc_directory, lvl=1, whiteFlag=Flag.NODE):
        if not (self.genre_type and self.genre_id):
            return True
        offset = self.offset or 0
        limit = qobuz.addon.getSetting('pagination_limit')
        data = qobuz.registry.get(name='recommendation',
                                  id=self.myid(),
                                  type=RECOS_TYPE_IDS[int(self.genre_type)],
                                  genre_id=self.genre_id,
                                  limit=limit,
                                  offset=offset)
        if not data:
            warn(self, "Cannot fetch data for recommendation")
            return False
        self.add_pagination(data['data'])
        self.data = data['data']
        return True
    
# TYPE
    def _build_recos_type(self, xbmc_directory, lvl, flag):
        colorItem = qobuz.addon.getSetting('color_item')
        for gid in RECOS_TYPE_IDS:
            node = Node_recommendation()
            node.genre_type = gid
            node.set_label(
                self.label + ' / ' + color(colorItem, RECOS_TYPES[gid]))
            self.add_child(node)
        return True

# GENRE
    def _build_recos_genre(self, xbmc_directory, lvl, flag):
        colorItem = qobuz.addon.getSetting('color_item')
        for genre_id in RECOS_GENRES:
            node = Node_recommendation()
            node.genre_type = self.genre_type
            node.genre_id = genre_id
            node.set_label(self.label + ' / '
                           + color(colorItem,
                                   RECOS_TYPES[int(self.genre_type)])
                           + ' / ' + RECOS_GENRES[genre_id])
            self.add_child(node)
        return True

# TYPE GENRE
    def _build_down_type_genre(self, xbmc_directory, lvl, flag):
        if not self.data:
            return False
        for product in self.data['albums']['items']:
            node = Node_product()
            node.data = product
            self.add_child(node)
        return True

# DISPATCH
    def _build_down(self, xbmc_directory, lvl, flag=None, progress=None):
        if not self.genre_type:
            return self._build_recos_type(xbmc_directory, lvl, flag)
        elif not self.genre_id:
            return self._build_recos_genre(xbmc_directory, lvl, flag)
        self.content_type = 'albums'
        return self._build_down_type_genre(xbmc_directory, lvl, flag)
