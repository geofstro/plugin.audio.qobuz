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
from renderer.xbmc import QobuzXbmcRenderer as renderer
from node.flag import NodeFlag as Flag

def getRenderer(nType, params = None):
    return renderer(nType, params)

def getNode(qnt, params = {}):
        nodeName = Flag.to_s(qnt)
        modulePath = 'node.' + nodeName
        moduleName = 'Node_' + nodeName
        """ from node.foo import Node_foo """
#        try:
        modPackage = __import__(modulePath, globals(), 
                                locals(), [moduleName], -1)
#        except Exception as e:
#            error = {
#                     'modulePath': modulePath,
#                     'moduleName': moduleName,
#                     'nodeName': nodeName,
#                     'nodeType': nt,
#                     'error': e
#            }
#            raise QobuzXbmcError(who=self, 
#                                 what="module_loading_error", 
#                                 additional=pprint.pformat(error))
        """ Getting Module from Package """
        nodeModule = getattr(modPackage, moduleName)
        """ 
            Initializing our new node 
            - no parent 
            - parameters 
            """
        node = nodeModule(None, params)
        return node