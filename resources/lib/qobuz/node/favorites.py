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
from product import Node_product
from debug import info, warn, error
'''
    NODE PLAYLIST
'''
from track import Node_track

class Node_favorites(Node):

    def __init__(self, parent = None, parameters = None, progress = None):
        super(Node_favorites, self).__init__(parent, parameters)
        self.type = NodeFlag.TYPE_NODE | NodeFlag.TYPE_FAVORITES
        self.set_label(qobuz.lang(30079))
        self.packby = ''#album'      
        self.name = qobuz.lang(30079)
        self.label = qobuz.lang(30079)    
        self.set_content_type('songs')

    def _build_down(self, xbmc_directory, lvl, flag = None):
        data = qobuz.registry.get(name='user-favorites')
        if not data:
            warn(self, "Build-down: Cannot fetch favorites data")
            return False
        self.set_data(data)
        albumseen = {}
        warn (self, pprint.pformat(data))
        for track in data['data']['tracks']['items']:
            node = None
            node = Node_track()
            node.set_data(track)
            self.add_child(node)
    
        for product in self.filter_products(data):
            self.add_child(product)
        return True
        
        
        del self._data['tracks']
        
    def get_name(self):
        name = self.get_property('name')
        return name
    
    def get_owner(self):
        return self.get_property(('owner', 'name'))
            
    def get_description(self):
        return self.get_property('description')
    
    def make_XbmcListItem(self):
        color_item = qobuz.addon.getSetting('color_item')
        color_pl = qobuz.addon.getSetting('color_item_playlist')
        image = self.get_image()
        owner = self.get_owner()
        url = self.make_url()
        item = xbmcgui.ListItem(self.label,
                                owner,
                                image,
                                image,
                                url)
        if not item:
            warn(self, "Error: Cannot make xbmc list item")
            return None
        item.setPath(url)
        self.attach_context_menu(item)
        return item

    def hook_attach_context_menu(self, item, menuItems):
        color = qobuz.addon.getSetting('color_item')
        color_warn = qobuz.addon.getSetting('color_item_caution')
        label = self.get_label()
                     
    def filter_products(self, data):
        list = []
        if not data: return list
        albumseen = {}
        for track in data['data']['albums']['items']:
            #warn(self, 'Track ' + track)
            json = track
            json[u'interpreter'] = track['artist']['name']
            product = Node_product()
            product.set_data(json)
            id = product.id
            if id in albumseen: continue
            albumseen[id] = 1
            list.append(product)
        return list

    def add_to_favorites(self):
            from gui.directory import Directory
            from renderer.xbmc import Xbmc_renderer as renderer
            nt = None
            try: nt = int(self.get_parameter('nt'))
            except:
                warn(self, "No node type...abort")
                return False
            id = None
            try: id = self.get_parameter('nid')        
            except: pass 
            depth = -1
            try: depth = int(self.get_parameter('depth'))
            except: pass
            view_filter = 0
            try: view_filter = int(self.get_parameter('view-filter'))
            except: pass
            render = renderer(nt, id)
            render.set_depth(depth)
            render.set_filter(view_filter)
            render.set_root_node()
            dir = Directory(render.root, qobuz.boot.handle, True)
            flags = NodeFlag.TYPE_TRACK | NodeFlag.DONTFETCHTRACK
            if render.root.type & NodeFlag.TYPE_TRACK:
                flags = NodeFlag.TYPE_TRACK
            ret = render.root.build_down(dir, depth, flags)
            if not ret: 
                dir.end_of_directory()
                return False
            trackids = []
            if len(dir.nodes) < 1:
                warn(self, "No track to add to favorites")
                dir.end_of_directory()
                return False
            for node in dir.nodes:
                trackids.append(str(node.id))
            strtracks = ','.join(trackids)
            ret = qobuz.api.favorites_add_track(strtracks)
            info(self, pprint.pformat(ret))
            qobuz.registry.delete(name='user-favorites')
            dir.end_of_directory()
            return True
