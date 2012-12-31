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
import pprint

import xbmcgui, xbmc

import qobuz
from constants import Mode
from flag import NodeFlag
from node import Node
from debug import info, warn, error
from gui.util import color, getImage

'''
    NODE LABEL
'''


class Node_label(Node):

    def __init__(self, parent = None, parameters = None, progress = None):
        super(Node_label, self).__init__(parent, parameters)
        self.type = NodeFlag.TYPE_NODE | NodeFlag.TYPE_LABEL
        self.set_label('Label (i8n)')
        self.url = None
        self.set_is_folder(True)
        self.image = getImage('album')
    
    
    def hook_post_data(self):
        self.label = self.get_property('name')
        self.id = self.get_property('id')
        
    def _build_down(self, xbmc_directory, lvl, flag = None):
        offset = self.get_parameter('offset') or 0
        #@bug: Qobuz service seam do don't return total so pagination is broken
        #limit = qobuz.addon.getSetting('pagination_limit')
        limit = 5000
        data = qobuz.registry.get(name='label-list', id=self.id, limit=limit, offset=offset)
        if not data:
            warn(self, "No label data")
            return False
        print pprint.pformat(data)
        for item in data['data']['labels']['items']:
            node = Node_label()
            node.data = item
            self.add_child(node)
        self.add_pagination(data)
        return True
