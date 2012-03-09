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
import re

class dog():

    def __init__(self):
        self.allowed_keys = {
                             'mode'      : '^\d{1,10}$',
                             'nid'       : '^\d{1,14}$',
                             'nt'        : '^\d{1,10}$',
                             'genre-type': '^(editor-picks|best-sellers|press-awards|new-releases)$',
                             'genre-id'  : '^\d+$',
                             'url'       : '^.*$',
                             'search-type': "^(artists|songs|albums)$",
                             'view-filter': "^\d+$",
                             'depth': "^(-)?\d+$"
                             }

    ''' Match value against regexp '''
    def kv_is_ok(self, key, value):
        print key + ' - ' + value
        if key not in self.allowed_keys:
            return False
        match = None
        try: match = re.match(self.allowed_keys[key], value)
        except: pass
        if match == None:
            return False
        return True
