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
class __NodeFlag():
    def __init__(self):
        self.DONTFETCHTRACK        = 1
        self.TYPE_NODE             = 2
        self.TYPE_TRACK            = 4
        self.TYPE_PLAYLIST         = 8
        self.TYPE_USERPLAYLISTS    = 16
        self.TYPE_RECOMMENDATION   = 32
        self.TYPE_ROOT             = 64
        self.TYPE_PRODUCT          = 128
        self.TYPE_VIRTUAL_PLAYLIST = 256
        self.TYPE_PURCHASES        = 512
        self.TYPE_SEARCH           = 1024
        self.TYPE_ARTIST           = 2048

#        self.DONTFETCHTRACK        = 1
#        self.TYPE_NODE             = 2
#        self.TYPE_TRACK            = 4
#        self.TYPE_PLAYLIST         = 8
#        self.TYPE_USERPLAYLISTS    = 16
#        self.TYPE_RECOMMENDATION   = 32
#        self.TYPE_ROOT             = 64
#        self.TYPE_PRODUCT          = 128
#        self.TYPE_VIRTUAL_PLAYLIST = 256
#        self.TYPE_PURCHASES        = 512
#        self.TYPE_SEARCH           = 1024
#        self.TYPE_ARTIST           = 2048
    def to_string(self, flag):
        if not flag: return "No Flag"
        if flag   == self.TYPE_NODE:           return "node"
        elif flag == self.TYPE_TRACK:          return "track"
        elif flag == self.TYPE_PLAYLIST:       return "playlist"
        elif flag == self.TYPE_USERPLAYLISTS:  return "userplaylists"
        elif flag == self.TYPE_RECOMMENDATION: return "recommendations"
        elif flag == self.TYPE_ROOT:           return "root"
        elif flag == self.TYPE_PRODUCT:        return "product"
        elif flag == self.TYPE_PURCHASES:      return "purchases"
        elif flag == self.TYPE_ARTIST:         return "artist"
        else: return "Unknow flag: " + str(flag)

NodeFlag = __NodeFlag()
