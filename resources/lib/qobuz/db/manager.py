import os, sys
try:
    from sqlite3 import dbapi2 as sqlite
    #logFile.info("Loading sqlite3 as DB engine")
except:
    from pysqlite2 import dbapi2 as sqlite
    #logFile.info("Loading pysqlite2 as DB engine")
from track import Track
from product import Product
from artist import Artist
from genre import Genre
from label import Label

class Manager():

    def __init__(self, path):
        self.path = path
        self.handle = None
        self.tables = {
                       'track':  Track(),
                       'product':  Product(),
                       'artist': Artist(),
                       'genre': Genre(),
                       'label': Label()
                       }
        self.auto_create = True

    def create_new_database(self):
        #os.unlink(self.path)
        handle = sqlite.connect(self.path)
        handle.row_factory = sqlite.Row
        if not handle:
            print "Error: Cannot create database, " + self.path
            return False
        for table_name in self.tables:
            self.tables[table_name].create(handle)
        handle.close()
        return True

    def connect(self, path = None):
        if path: self.path = path
        else: path = self.path
        if not self.exists():
            if not self.auto_create:
                print "Database doesn't exist and auto create is false."
                return False
            if not self.create_new_database():
                print "Cannot create new database"
                return False
        #os.unlink(path)
        conn = sqlite.connect(path)
        if not conn:
            print "Cannot open database: %s" % (path)
            return None
        self.handle = conn
        self.handle.row_factory = sqlite.Row
        return conn

    def get(self, table, where = {}, auto_fetch = True):
        if not table in self.tables:
            print "Invalid table: " + table
            return False
        T = self.tables[table]
        row = T.get(self.handle, where[T.pk])
        if not row:
            print "No data in database"
            if T.auto_fetch and auto_fetch:
                print "AutoFethc ENABLE"
                row = T.fetch(self.handle, where[T.pk])
            if not row:
                print "We definitly don't have this data"
                return None
        return row

    def get_track(self, id):
        cursor = self.handle.cursor()
        query = "SELECT t.id as id, t.copyright AS copyright, " \
        "t.duration AS duration, t.media_number AS media_number," \
        "t.streaming_type AS streaming_type, t.title as title, " \
        "t.track_number AS track_number, t.version AS version, " \
        "t.work AS work, " \
        "p.image AS image, " \
        "ai.name AS interpreter_name " \
        "FROM track AS t, " \
        "product AS p, " \
        "artist AS ai, artist AS ac " \
        "WHERE t.product_id = p.id AND (t.interpreter_id IS NULL OR t.interpreter_id = ai.id) AND (t.composer_id IS NULL OR t.composer_id = ac.id) " \
        "AND t.id = ? "
        print "Query: " + query
        cursor.execute(query, (id,))
        row = cursor.fetchone()
        if not row:
            print "No result"
            return None
        return row

    def insert(self, table, where):
        if not table in self.tables:
            print "Invalid table " + table
            return False
        T = self.tables[table]
        if not T.pk in where.keys():
            print "Cannot insert data without primary key"
            return False
        if T.get(self.handle, where[T.pk]):
            print "Cannot insert data, primary key already present"
            return False
        return T.insert(self.handle, where)

    def insert_json(self, table, json):
        if not table in self.tables:
            print "Invalid table " + table
            return False
        T = self.tables[table]
        if not T.pk in json:
            print "JSON Data doesn't contain 'id'"
            return False
        row = T.get(self.handle, json['id'])
        if row:
            print "Cannot insert data, primary key already present"
            return row
        if not T.insert_json(self.handle, json):
            return None
        return T.get(self.handle, json['id'])

    def exists(self):
        return os.path.exists(self.path)
