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
#import sys
#import pprint

import xbmcgui

import qobuz

#from constants import Mode
from flag import NodeFlag
from node import Node
from product import Node_product
#from debug import info, warn, error, debug
from debug import warn
'''
    NODE ARTIST
'''

class Node_artist(Node):

    def __init__(self, parent = None, parameters = None):
        super(Node_artist, self).__init__(parent, parameters)
        self.type = NodeFlag.TYPE_NODE | NodeFlag.TYPE_ARTIST
        self.set_content_type('albums')

    '''
        Getter 
    '''
    def get_label(self):
        return self.get_artist()
    
    def get_artist(self):
        return self.get_property('name')
    
    def get_label2(self):
        return self.get_slug()
    
    def get_slug(self):
        return self.get_property('slug')
    
    def get_artist_id(self): return self.get_id()
        
    '''
        Build Down
    '''
    def _build_down(self, xbmc_directory, lvl, flag = None, progress = None):
        data = qobuz.api.get_albums_from_artist(self.get_id(), qobuz.addon.getSetting('artistsearchlimit'))
        if not data:
            warn(self, "Cannot fetch albums for artist: " + self.get_label())
            return False
        total = len(data['artist']['albums'])
        count = 0
        for jproduct in data['artist']['albums']:
            keys = ['artist', 'interpreter', 'composer']
            for k in keys:
                if k in data['artist']: jproduct[k] = data['artist'][k]
            node = Node_product()
            node.set_data(jproduct)
            xbmc_directory.update(count, total, "Add album:" + node.get_label(), '')
            self.add_child(node)
            count += 1
        return True
    
    '''
        Make XbmcListItem
    '''
    def make_XbmcListItem(self):
        item = xbmcgui.ListItem(self.get_label(),
                                self.get_label(),
                                self.get_image(),
                                self.get_image(),
                                self.make_url(),
                                )
        #item.setProperty('node_id', self.get_id())
        self.attach_context_menu(item)
        return item

