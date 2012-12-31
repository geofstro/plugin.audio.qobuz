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
from flag import NodeFlag
from node import Node
from product import Node_product
from debug import warn
from gui.util import color, lang, getImage

RECOS_TYPES = {
                      'new-releases': lang(30084),
                      'press-awards': lang(30083),
                      'best-sellers': lang(30085),
                      'editor-picks': lang(30086),
                      'most-featured': lang(30102),
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
#from cache.recommendation import Cache_recommendation

class Node_recommendation(Node):

    def __init__(self, parent = None, parameters = None):
        super(Node_recommendation, self).__init__(parent, parameters)
        self.type = NodeFlag.TYPE_NODE | NodeFlag.TYPE_RECOMMENDATION
        self.genre_id = self.get_parameter('genre-id')
        self.genre_type = self.get_parameter('genre-type')
        self.set_label(lang(30082))
        self.image = getImage('album')

    def make_url(self, **ka):
        url = super(Node_recommendation, self).make_url(**ka)
        if self.genre_type:
            url += '&genre-type=' + self.genre_type
        if self.genre_id:
            url += '&genre-id=' + str(self.genre_id)
        if 'action' in self.parameters and self.parameters['action'] == 'scan':
            url += "&action=scan"
        return url

    @property
    def id(self):
        return self.value
    
    @id.getter
    def id(self):
        if not self.genre_id or not self.genre_type: return None
        return self.genre_type + '-' + str(self.genre_id)
    
    @id.setter
    def id(self, value):
        self._id = value
    
    def set_genre_type(self, type):
        self.genre_type = type

    def set_genre_id(self, id):
        self.genre_id = id

    def get_genre_type(self):
        return self.genre_type

    def get_genre_id(self):
        return self.genre_id

# TYPE
    def _build_recos_type(self, xbmc_directory, lvl, flag):
        colorItem = qobuz.addon.getSetting('color_item')
        for gtype in RECOS_TYPES:
            node = Node_recommendation()
            node.set_genre_type(gtype)
            node.set_label(self.label + ' / ' + color(colorItem, RECOS_TYPES[gtype]))
            self.add_child(node)
        return True

# GENRE
    def _build_recos_genre(self, xbmc_directory, lvl, flag):
        colorItem = qobuz.addon.getSetting('color_item')
        for genreid in RECOS_GENRES:
            node = Node_recommendation()
            node.set_genre_type(self.get_genre_type())
            node.set_genre_id(genreid)
            node.set_label(self.label + ' / ' + color(colorItem, RECOS_TYPES[self.genre_type]) + ' / ' + RECOS_GENRES[genreid])
            self.add_child(node)
        return True


# TYPE GENRE
    def _build_down_type_genre(self, xbmc_directory, lvl, flag):
        offset = self.get_parameter('offset') or 0
        limit = qobuz.addon.getSetting('pagination_limit')
        data = qobuz.registry.get(name='recommendation', id=self.id, type=self.genre_type, genre_id=self.genre_id, limit=limit, offset=offset)
        if not data:
            warn(self, "Cannot fetch data for recommendation")
            return False
        for product in data['data']['albums']['items']:
            node = Node_product()
            node.data = product
            self.add_child(node)
        self.add_pagination(data['data'])
        return True

# DISPATCH
    def _build_down(self, xbmc_directory, lvl, flag = None, progress = None):
        if not self.genre_type:
            return self._build_recos_type(xbmc_directory, lvl, flag)
        elif not self.genre_id:
            return self._build_recos_genre(xbmc_directory, lvl, flag)
        self.content_type = 'albums'
        return self._build_down_type_genre(xbmc_directory, lvl, flag)
