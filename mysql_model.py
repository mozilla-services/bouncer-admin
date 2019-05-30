from flask import Flask, render_template, request
from flask_mysqldb import MySQL
import mysql.connector

class MySQLModel:
    def __init__(self, flask_app):
        self._app = flask_app
    
    def index(self):
        db = mysql.connector.connect(user='root', host='127.0.0.1', database='bouncer')
        cur = db.cursor()
        cur.execute('''SELECT * FROM mirror_mirrors''')

        res = cur.fetchall()

        cur.close()
        db.close()
        return str(res)
    
    def location_show(self, product, fuzzy):
        if fuzzy:
            sql = sql = '''SELECT path, mo.name, mp.name FROM mirror_locations ml JOIN mirror_products mp ON ml.product_id=mp.id JOIN mirror_os mo ON mo.id=ml.os_id WHERE mp.name LIKE %s;'''
            product = '%' + product + '%'
        else:
            sql = '''SELECT path, mo.name, mp.name FROM mirror_locations ml JOIN mirror_products mp ON ml.product_id=mp.id JOIN mirror_os mo ON mo.id=ml.os_id WHERE mp.name = %s;'''

        db = mysql.connector.connect(user='root', host='127.0.0.1', database='bouncer')
        cur = db.cursor()
        cur.execute(sql, (product,))

        res = cur.fetchall()

        cur.close()
        db.close()
        return str(res)
    
    def location_add(self, product, os, path):

        os_exists, os_id = self.os_exists(os)
        product_exists, product_id = self.product_exists(product)
        location_exists, location = self.location_exists(os, product)

        if(not os_exists):
            return 'FAILED: \'' + os + '\' does not exist'
        if(not product_exists):
            return 'FAILED: \'' + product + '\' does not exist'
        if(location_exists):
            return 'FAILED: already a path for location \'' + product + '\' on OS \'' + os + '\''
        
        sql = '''INSERT INTO mirror_locations (product_id, os_id, path) VALUES (%s,%s,%s)'''

        db = mysql.connector.connect(user='root', host='127.0.0.1', database='bouncer')
        cur = db.cursor()
        cur.execute(sql, (product_id, os_id, path))

        db.commit()

        cur.close()
        db.close()

        return 'SUCCESS: new location added'
    
    def location_modify(self, product, os, path):

        os_exists, os_id = self.os_exists(os)
        product_exists, product_id = self.product_exists(product)
        location_exists, location = self.location_exists(os, product)

        if(not os_exists):
            return 'FAILED: \'' + os + '\' does not exist'
        if(not product_exists):
            return 'FAILED: \'' + product + '\' does not exist'
        if(not location_exists):
            return 'FAILED: location \'' + product + '\' on OS \'' + os + '\' does not exist'
        
        sql = '''UPDATE mirror_locations SET path=%s WHERE os_id=%s AND product_id=%s'''

        db = mysql.connector.connect(user='root', host='127.0.0.1', database='bouncer')
        cur = db.cursor()
        cur.execute(sql, (path, os_id, product_id))

        db.commit()

        cur.close()
        db.close()

        return 'SUCCESS: location has been updated'
        
    def location_delete(self, product, os):
        os_exists, os_id = self.os_exists(os)
        product_exists, product_id = self.product_exists(product)
        location_exists, location = self.location_exists(os, product)

        if(not os_exists):
            return 'FAILED: \'' + os + '\' does not exist'
        if(not product_exists):
            return 'FAILED: \'' + product + '\' does not exist'
        if(not location_exists):
            return 'FAILED: location \'' + product + '\' on OS \'' + os + '\' does not exist'
        
        sql = '''DELETE FROM mirror_locations WHERE os_id=%s AND product_id=%s'''

        db = mysql.connector.connect(user='root', host='127.0.0.1', database='bouncer')
        cur = db.cursor()
        cur.execute(sql, (os_id, product_id))

        db.commit()

        cur.close()
        db.close()

        return 'SUCCESS: location has been deleted'

    def os_exists(self, os):
        sql = '''SELECT id FROM mirror_os WHERE name=%s;'''

        db = mysql.connector.connect(user='root', host='127.0.0.1', database='bouncer')
        cur = db.cursor()
        cur.execute(sql, (os,))

        res = cur.fetchall()

        cur.close()
        db.close()

        return len(res) > 0, res[0][0]
    
    def product_exists(self, product):
        sql = '''SELECT id FROM mirror_products WHERE name=%s;'''

        db = mysql.connector.connect(user='root', host='127.0.0.1', database='bouncer')
        cur = db.cursor()
        cur.execute(sql, (product,))

        res = cur.fetchall()

        cur.close()
        db.close()
        return len(res) > 0, res[0][0]
    
    def location_exists(self, os, product):
        sql = '''SELECT * FROM mirror_locations ml JOIN mirror_os mo ON ml.os_id=mo.id JOIN mirror_products mp ON ml.product_id=mp.id WHERE mo.name=%s AND mp.name=%s;'''

        db = mysql.connector.connect(user='root', host='127.0.0.1', database='bouncer')
        cur = db.cursor()
        cur.execute(sql, (os, product))

        res = cur.fetchall()

        cur.close()
        db.close()
        return len(res) > 0, res[0][0]
    