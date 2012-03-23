import pprint
import qobuz
from itable import Itable

class Product(Itable):

    def __init__(self, id = None):
        super(Product, self).__init__(id)
        self.table_name = 'product'
        self.pk = 'id'
        self.fields_name = {
                            'id'               : {'jsonmap': 'id', 'sqltype': 'INTEGER PRIMARY KEY'},
                            'artist_id': {'jsonmap': ('artist', 'id'), 'sqltype': 'INTEGER'},
                            'description': {'jsonmap': 'descrption', 'sqltype': 'VARCHAR'},
                            'genre_id' : {'jsonmap': ('genre', 'id'), 'sqltype': 'INTEGER'},
                            'image'               : {'jsonmap': ('image', 'large'), 'sqltype': 'VARCHAR'},
                            'label_id'               : {'jsonmap': ('label', 'id'), 'sqltype': 'INTEGER'},
                            'price'               : {'jsonmap': 'price', 'sqltype': 'INTEGER'},
                            'release_date'               : {'jsonmap': 'release_date', 'sqltype': 'VARCHAR'},
                            'subtitle'               : {'jsonmap': 'subtitle', 'sqltype': 'VARCHAR'},
                            'title'               : {'jsonmap': 'title', 'sqltype': 'VARCHAR'},
                            'url'               : {'jsonmap': 'url', 'sqltype': 'VARCHAR'},
                             }

    def fetch(self, handle, id):
        from track import Track
        from artist import Artist
        from genre import Genre
        from label import Label
        jproduct = qobuz.api.get_product(id)['product']
        if not jproduct:
            print "Cannot fetch data"
            return False
        print "JPRODUCT: " + pprint.pformat(jproduct)
        where = {}
        if 'artist' in jproduct:
            A = Artist()
            if not A.get(handle, jproduct['artist']['id']):
                A.insert(handle, jproduct['artist'])
        if 'genre' in jproduct:
            G = Genre()
            if not G.get(handle, jproduct['genre']['id']):
                G.insert(handle, jproduct['genre'])
        if 'label' in jproduct:
            L = Label()
            if not L.get(handle, jproduct['label']['id']):
                L.insert(handle, jproduct['label'])
        # AUTO MAP JSON
        for field in self.fields_name.keys():
            f = self.fields_name[field]
            if not f['jsonmap']: continue
            value = self.get_property(jproduct, f['jsonmap'])
            if not value: continue
            where[field] = value
        for jtrack in jproduct['tracks']:
            print "TRACK: " + pprint.pformat(jtrack)
            T = Track()
            if T.get(handle, jtrack['id']): continue
            T.insert(handle, jtrack)
        self.insert(handle, where)


    def insert_json(self, handle, json):
        where = {}
        for field in self.fields_name.keys():
            f = self.fields_name[field]
            if not f['jsonmap']: continue
            value = self.get_property(json, f['jsonmap'])
            if not value: continue
            where[field] = value
        return self.insert(handle, where)
