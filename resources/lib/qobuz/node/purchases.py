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
from flag import NodeFlag
from inode import INode
from debug import warn
from api import easyapi
from product import Node_product
from track import Node_track
from gui.util import lang, getImage, getSetting

class Node_purchases(INode):
    '''Displaying product purchased by user (track and album)
    '''
    def __init__(self, parent=None, params=None):
        super(Node_purchases, self).__init__(parent, params)
        self.label = lang(30100)
        self.type = NodeFlag.PURCHASES
        self.content_type = 'albums'
        self.image = getImage('album')
        self.offset = self.get_parameter('offset') or 0
        
    def fetch(self, Dir, lvl, whiteFlag, blackFlag):
        limit = getSetting('pagination_limit')
        data = easyapi.get('/purchase/getUserPurchases', limit=limit, 
                           offset=self.offset, user_id=easyapi.user_id)
        if not data:
            warn(self, "Cannot fetch purchases data")
            return False
        self.data = data
        return True
        
    def populate(self, Dir, lvl, whiteFlag, blackFlag):
        if 'albums' in self.data:
            self.__populate_albums(Dir, lvl, whiteFlag, blackFlag)
        elif 'tracks' in self.data:
            self.__populate_tracks(Dir, lvl, whiteFlag, blackFlag)

    def __populate_albums(self, Dir, lvl, whiteFlag, blackFlag):
        for album in self.data['albums']['items']:
            node = Node_product()
            node.data = album
            self.add_child(node)
        return list
    
    def __populate_tracks(self, Dir, lvl, whiteFlag, blackFlag):
        for track in self.data['tracks']['items']:
            node = Node_track()
            node.data = track
            self.add_child(node)
        return list
    
