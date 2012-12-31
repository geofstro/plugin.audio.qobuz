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
from exception import QobuzXbmcError
from api import QobuzApi
from time import time
from util.file import FileUtil
import cPickle as pickle
import os
from debug import *
import hashlib
import re

class QobuzLocalStorage(object):

    def __init__(self,**ka):
        # Checking mandatory parameters
        mandatory = ['username','password','streamFormat']
        for key in mandatory:
            if not key in ka: raise QobuzXbmcError(who=self,
                                                   what='missing_parameter',
                                                   additional=key)
        # Regexp to filter out keys that we don't hashed
        self.hashing_exclude_keys = None
        self.hash_key_algorithm = 'md5'

        # Setting our options and their default
        self.options = ka
        if not 'autoSave' in self.options:
            self.options['autoSave'] = True
        if not 'autoLoad' in self.options:
            self.options['autoLoad'] = True
        if not 'refresh' in self.options:
            self.options['refresh'] = 3600
        if not 'overwrite' in self.options:
            self.options['overwrite'] = True
        if not 'hashKey' in self.options:
            self.options['hashKey'] = False
        
        if self.options['hashKey']:
            self.hashing_exclude_keys = '^user.*$'

        # Our dictionary storage
        self.data = {}

        # Qobuz API
        self.api = QobuzApi()
        if not self.login(**ka):
            user = None
            if 'user' in ka: user = ka['user']
            raise QobuzXbmcError(who=self,what='login_failure',additional=repr(user))

    ''' We are compiling exluded key regex and raise error if it's fail '''
    @property
    def hashing_exclude_keys(self):
        return self._hashing_exclude_keys
    @hashing_exclude_keys.getter
    def hashing_exclude_keys(self):
        return self._hashing_exclude_keys
    @hashing_exclude_keys.setter
    def hashing_exclude_keys(self,pattern):
        self._hashing_exclude_keys = None
        if not pattern: return
        try:
            self._hashing_exclude_keys = re.compile(pattern)
        except: raise QobuzXbmcError(who=self,what='invalid_exclude_pattern',additional=pattern)

    def login(self,**ka):
        # Login into Qobuz our raise exception   
        #key = self.make_key(name='user', id=0)
        data = self.get(name='user',id=0,username=ka['username'],password=ka['password'])
        if not data: return False
        # We feed our api wit user data (auth_token, rights ...)
        self.api.set_logged(**data)
        return True

    def lastError(self):
        return self.api.last_error

    def set(self,**ka):
        mandatory = ['name','id']
        for key in mandatory:
            if not key in ka:
                raise QobuzXbmcError(who=self,what='missing_parameter',additional=key)
        key = self.make_key(**ka)
        if not self.options['overwrite'] and key in self.data:
            raise QobuzXbmcError(who=self,what='key_exist',additional=key)
        self.data[key] = {
                          'name': ka['name'],
                          'id': ka['id'],
                          'saved': False,
                          'data': ka['value'],
                          'updatedOn': time(),
                          'refresh': self.options['refresh']
                          }
        if self.options['autoSave']:
            self.save(key)
        return self

    def save(self,key):
        QobuzXbmcError(who=self,what='not_implemented_in_child_class',additional='save')

    def delete_by_name(self,name):
        QobuzXbmcError(who=self,what='not_implemented_in_child_class',additional='delete_by_name')

    def make_key(self,**ka):
        key = self._make_key(**ka)
        if self.options['hashKey']:
            return self.hash_key(key)
        return key

    def _make_key(self,**ka):
        QobuzXbmcError(who=self,what='not_implemented_in_child_class',additional='make_key')

    def hash_key(self,key):
        if self.hashing_exclude_keys:
            if self.hashing_exclude_keys.match(key):
                return key
        h = hashlib.new(self.hash_key_algorithm)
        h.update(key)
        return h.hexdigest()

    def get(self,*args,**ka):
        key = self.make_key(**ka)
        if not key in self.data:
                self.load(**ka)
        if key in self.data:
            return self.data[key]
        return None

    def load(self,**ka):
        self.hook_pre_load(**ka)
        # noRemote prevent data loading from Qobuz (local key only)
        if 'noRemote' in ka and ka['noRemote'] == True:
            return False
        key = self.make_key(**ka)
        if key in self.data and self.fresh(key):
            return self.data[key]
        log(self,"[REMOTE/QOBUZ] Loading: " + key)
        response = None
        # We are deleting name and id because we don't want to send them
        # to Qobuz
        name = ka['name']
        del ka['name']
        id = ka['id']
        del ka['id']
        # Switching on name
        if name == 'user':
            response = self.api.user_login(**ka)
        elif name == 'product':
            response = self.api.album_get(album_id=id)
        elif name == 'user-playlists':
            response = self.api.playlist_getUserPlaylists(**ka)
        elif name == 'user-playlist':
            response = self.api.playlist_get(playlist_id=id,extra='tracks',limit=ka['limit'],offset=ka['offset'])
        elif name == 'user-favorites':
            response = self.api.favorite_getUserFavorites(**ka)
        elif name == 'track':
            response = self.api.track_get(track_id=id)
        elif name == 'user-stream-url':
            response = self.api.track_getFileUrl(track_id=id,format_id=self.options['streamFormat'])
        elif name == 'user-purchases':
            response = self.api.purchase_getUserPurchases(limit=ka['limit'])
        elif name == 'recommendation':
            response = self.api.album_getFeatured(**ka)
        elif name == 'artist':
            response = self.api.artist_get(artist_id=id,limit=ka['limit'])
        elif name == 'genre-list':
            response = self.api.genre_list(parent_id=id,limit=ka['limit'])
        elif name == 'label-list':
            response = self.api.label_list(**ka)
        else:
            QobuzXbmcError(
                        who=self,
                        what='qobuz_api_invalid_query',
                        additional=pprint.pformat(ka))
        if not response:
                warn(self,"Loading from Qobuz fail")
                return False
        ka['value'] = response
        ka['name'] = name
        ka['id'] = id
        self.set(**ka)
        return True


    def fresh(self,key):
        if not key in self.data:
            return False
        if (time() - self.data[key]['updatedOn']) > self.options['refresh']:
            return False
        return True

    def saved(self,key,value=None):
        if not key:
            QobuzXbmcError(who=self,what='missing_parameter',additional='key')
        if not key in self.data:
            QobuzXbmcError(who=self,what='undefined_key',additional=key)
        if value == None:
            return self.data[key]['saved']
        self.data[key]['saved'] = True if value else False
        return self

    def delete(self,**ka):
        key = self.make_key(**ka)
        self.data[key] = None
        del self.data[key]

class QobuzCacheDefault(QobuzLocalStorage):

    def __init__(self,**ka):
        # @bug: Must have been herited from parent class ?
        #self._hashing_exclude_keys = None
        super(QobuzCacheDefault,self).__init__(**ka)
        if not 'basePath' in ka:
            QobuzXbmcError(who=self,what='missing_parameter',additional='basePath')


    def _make_key(self,*args,**ka):
        if not 'id' in ka: ka['id'] = 0
        key = ka['name'] + '-' + str(ka['id']);
        if 'offset' in ka: key += '-' + str(ka['offset'])
        return key

    def _make_sub_path(self,xpath,key,size,count):
        if count == 0 or len(key) < size + 1:
            return key + '.dat'
        subp = key[:size]
        root = os.path.join(os.path.join(*xpath),subp)
        if not os.path.exists(root):
            os.mkdir(root)
        xpath.append(subp)
        count -= 1
        return self._make_sub_path(xpath,key[size:],size,count)

    def _make_path(self, key):
        xpath = []
        xpath.append(self.options['basePath'])
        fileName = None
        if self.options['hashKey'] and not self.hashing_exclude_keys.match(key):
            fileName = self._make_sub_path(xpath,key,2,1)
        else:
            fileName = key + '.dat'
        return os.path.join(os.path.join(*xpath),fileName)

    def hook_pre_load(self,**ka):
        key = self.make_key(**ka)
        log(self,"[DISK] Loading: " + key)
        cache = self._make_path(key)
        #cache = os.path.join(self.options['basePath'], key+'.dat');
        if not os.path.exists(cache):
            warn(self,"[DISK] Path doesn't exists: " + cache)
            return False
        with open(cache,'rb') as f:
            f = open(cache,'rb')
            try:
                self.data[key] = pickle.load(f)
            except:
                warn(self,"[DISK] Failed to load data with Pickle: " + cache)
                return False
        return True

    def save(self,key=None):
        if key == None:
            count = 0
            for key in self.data:
                if not self.saved(key):
                    count += 1
                    self.save(key)
            return count
        if not key in self.data:
            raise QobuzXbmcError(who=self,what='undefined_key',additional=key)
        log(self, "[DISK] Saving: " + key)
        cache = self._make_path(key)
        with open(cache,'wb') as f:
            s = pickle.dump(self.data[key],f,protocol=pickle.HIGHEST_PROTOCOL)
            f.flush()
            os.fsync(f)
        return s
        warn(self,'[DISK] Saving failed: ' + key)
        return 0

    def delete(self,**ka):
        key = self.make_key(**ka)
        info(self,'[DISK] Deleting: ' + key)
        cache = os.path.join(self.options['basePath'],key + '.dat')
        if not os.path.exists(cache):
            return False
        fu = FileUtil();
        if fu.unlink(cache):
            super(QobuzCacheDefault,self).delete(**ka)

    def delete_by_name(self, pattern):
        fu = FileUtil()
        files = fu.find(self.options['basePath'], pattern)
        ret = True
        for fileName in files:
            log(self, "[DISK] Removing " + fileName)
            if not fu.unlink(fileName): 
                warn(self, "[DISK] Failed to remove: " + fileName)
                ret = False
        return ret

class QobuzCacheCommon(QobuzLocalStorage):
    def __init__(self,*args,**ka):
        print "Loading Common cache"
        import xbmcaddon
        import xbmc
        import StorageServer
        #StorageServer.dbg = True
        self.storage = StorageServer.StorageServer('plugin_audio_qobuz',24)
        super(QobuzCacheCommon,self).__init__(*args,**ka)
        print "import ok"

    def _make_key(self,*args,**ka):
            if not 'id' in ka: ka['id'] = 0
            return "" + ka['name'] + '-' + str(ka['id']);

    def hook_pre_load(self,**ka):
        key = self.make_key(**ka)
        data = self.storage.get(key)
        log(self,"LOADING " + key + ' / ' + pprint.pformat(data))
        if data:
            self.data[key] = pickle.loads(data)

    def save(self,key=None):
        if key == None:
            count = 0
            for key in self.data:
                if not self.saved(key):
                    count += 1
                    self.save(key)
            return count
        if not key in self.data:
            QobuzXbmcError(who=self,what='undefined_key',additional=key)
        data = pickle.dumps(self.data[key],0)
        log(self, "SAVE key " + key + ' / ' + pprint.pformat(data))
        self.storage.set(key,data)
        self.saved(key,True)
        return 1

class QobuzRegistry():

    def __init__(self,*args,**ka):
        if not 'cacheType' in ka:
            ka['cacheType'] = 'default'
        if ka['cacheType'] == 'default':
            self.cache = QobuzCacheDefault(*args,**ka)
        elif ka['cacheType'] == 'xbmc-common':
            cache = None
            try:
                cache = QobuzCacheCommon(*args,**ka)
            except Exception:
                cache = QobuzCacheDefault(*args,**ka)
            self.cache = cache
        else:
            QobuzXbmcError(who=self,what='unknown_cache_type',additionnal=ka['cacheType'])
        return None

    def get_api(self):
        return self.cache.api

    def lastError(self):
        return self.cache.lastError()

    def get(self,**ka):
        if not 'id' in ka: ka['id'] = 0
        return self.cache.get(**ka);

    def set(self,**ka):
        self.cache.set(**ka)

    def save(self):
        return self.cache.save()

    def delete(self,**ka):
        if not 'id' in ka:
            ka['id'] = 0
        return self.cache.delete(**ka)

    def delete_by_name(self,name):
        return self.cache.delete_by_name(name)

    def make_key(self,**ka):
        return self.cache.make_key(**ka)

    def login(self,**ka):
        return self.cache.login(**ka)

if __name__ == '__main__':
    pass
#    try:
#        QobuzXbmcError({'Who': 'TestException','What': 'test_exception','With': 'TestingException'})
#    except(QobuzXbmcError):
#        pass
#
#    reg = QobuzRegistry(user='SET_USER',password='SET_PASSWORD',cacheType='xbmc-common',
#                   basePath='c:/tmp/qobuz/',
#                   autoSave=True,
#                   autoLoad=True,refresh=3600)
#
#    user_playlists = reg.get(name='user-playlists',id=12342323)
#    if not user_playlists:
#        print "Error:" + repr(reg.lastError())
#    for pl in user_playlists['data']['playlists']['items']:
#        print  '[' + repr(pl['id']) + ']' + "Name: " + pl['name']
#        playlist = reg.get(name='playlist',id=pl['id'])
