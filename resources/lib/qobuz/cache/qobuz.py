'''
    qobuz.storage.qobuz
    ~~~~~~~~~~~~~~~~~~

    We are setting ttl here based on key type
    
    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from file import CacheFile
from gui.util import getSetting

class CacheQobuz(CacheFile):

    def __init__(self, *a, **ka):
        self._store = {}

    def get_ttl(self, key, *a, **ka):
        if len(a) > 0:
            if a[0] == '/track/getFileUrl':
                return 60*15
        if 'user_id' in ka:
            return getSetting('cache_duration_middle', isInt=True) * 60
        return getSetting('cache_duration_long', isInt=True) * 60
