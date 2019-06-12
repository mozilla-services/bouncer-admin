from flask import Flask, render_template, request
import mysql.connector

try:
    import nazgul.xmlrenderer as xmlrenderer
except:
    import xmlrenderer


class MySQLModel:
    def __init__(self, user="root", host="127.0.0.1", password="", db="bouncer"):
        self._pass = password
        self._user = user
        self._host = host
        self._db_name = db
        # TODO: Should I have autocommit always True?
        self._db = mysql.connector.connect(
            user=user, host=host, database=db, autocommit=True
        )

    def index(self):
        return "Welcome to Nazgul"

    def location_show(self, product, fuzzy):
        xml = xmlrenderer.XMLRenderer()

        if product is None:
            return xml.error("The GET parameter product is required", errno=103), False
        if fuzzy:
            sql = """SELECT distinct id FROM mirror_products mp WHERE name LIKE %s;"""
            product = "%" + product + "%"
        else:
            sql = """SELECT distinct id FROM mirror_products WHERE name = %s;"""

        cur = self._db.cursor()
        cur.execute(sql, (product,))

        res = cur.fetchall()

        cur.close()

        ids = []
        for line in res:
            ids.append(line[0])

        locs = self.get_locations_info(ids)

        for loc in locs:
            xml.prepare_locations(loc)
        return xml.render(), True

    def location_add(self, product, os, path):
        xml = xmlrenderer.XMLRenderer()

        if not (product and os and path):
            return (
                xml.error(
                    "product, os, and path are required POST parameters.", errno=101
                ),
                False,
            )

        os_exists, os_id = self.os_exists(os)
        product_exists, product_id = self.product_exists(product)
        location_exists, location_id = self.location_exists(os, product)

        if not os_exists:
            return xml.error("FAILED: '" + os + "' does not exist", errno=104), False
        if not product_exists:
            return (
                xml.error("FAILED: '" + product + "' does not exist", errno=104),
                False,
            )
        if location_exists:
            return xml.error("The specified location already exists.", errno=104), False

        sql = """INSERT INTO mirror_locations (product_id, os_id, path) VALUES (%s,%s,%s)"""

        cur = self._db.cursor()
        cur.execute(sql, (product_id, os_id, path))

        self._db.commit()

        cur.close()

        products = self.get_locations_info([product_id])
        for p in products:
            xml.prepare_locations(p)
        return xml.render(), True

    def location_modify(self, product, os, path):
        xml = xmlrenderer.XMLRenderer()

        os_exists, os_id = self.os_exists(os)
        product_exists, product_id = self.product_exists(product)
        location_exists, location_id = self.location_exists(os, product)

        if not os_exists:
            return xml.error("FAILED: '" + os + "' does not exist", errno=104), False
        if not product_exists:
            return (
                xml.error("FAILED: '" + product + "' does not exist", errno=104),
                False,
            )
        if not location_exists:
            return (
                xml.error(
                    "FAILED: location '"
                    + product
                    + "' on OS '"
                    + os
                    + "' does not exist",
                    errno=104,
                ),
                False,
            )

        sql = """UPDATE mirror_locations SET path=%s WHERE os_id=%s AND product_id=%s"""

        cur = self._db.cursor()
        cur.execute(sql, (path, os_id, product_id))

        self._db.commit()

        cur.close()

        products = self.get_locations_info([product_id])
        for p in products:
            xml.prepare_locations(p)
        return xml.render(), True

    def location_delete(self, location_id):
        xml = xmlrenderer.XMLRenderer()

        if not location_id:
            return xml.error("location_id is required.", errno=101), False
        if not self.location_id_valid(location_id):
            return xml.error("No location found.", errno=102), False

        sql = """DELETE FROM mirror_locations WHERE id=%s"""

        cur = self._db.cursor()
        cur.execute(sql, (location_id,))

        self._db.commit()

        cur.close()

        return xml.success("SUCCESS: location has been deleted"), True

    def product_show(self, product, fuzzy):
        xml = xmlrenderer.XMLRenderer()

        if fuzzy:
            sql = """SELECT id FROM mirror_products WHERE name LIKE %s;"""
            product = "%" + product + "%"
        else:
            sql = """SELECT id FROM mirror_products WHERE name = %s;"""

        cur = self._db.cursor()
        cur.execute(sql, (product,))

        res = cur.fetchall()

        cur.close()

        ids = []
        for line in res:
            ids.append(line[0])

        xml.prepare_products(self.get_products_info(ids))
        return xml.render(), True

    def product_add(self, product, languages, ssl_only):
        xml = xmlrenderer.XMLRenderer()

        product_exists, product_id = self.product_exists(product)
        if product_exists:
            return xml.error("product already exists.", errno=104), False

        sql = """INSERT INTO mirror_products (name, ssl_only) VALUES (%s, %s)"""

        cur = self._db.cursor()
        cur.execute(sql, (product, int(ssl_only)))
        self._db.commit()

        product_exists, product_id = self.product_exists(product)
        for lang in languages:
            sql = """INSERT INTO mirror_product_langs (product_id, language) VALUES (%s, %s)"""
            cur.execute(sql, (product_id, lang))

        self._db.commit()

        cur.close()

        xml.prepare_products(self.get_products_info([product_id]))
        return xml.render(), True

    def product_delete_name(self, name):
        xml = xmlrenderer.XMLRenderer()

        product_exists, product_id = self.product_exists(name)
        if not product_exists:
            return xml.error("No product found.", errno=102), False

        cur = self._db.cursor()

        sql = """DELETE FROM mirror_products WHERE id=%s"""
        cur.execute(sql, (product_id,))

        sql = """DELETE FROM mirror_product_langs WHERE product_id=%s"""
        cur.execute(sql, (product_id,))

        sql = """DELETE FROM mirror_locations WHERE product_id=%s"""
        cur.execute(sql, (product_id,))

        self._db.commit()

        cur.close()

        return xml.success("SUCCESS: product has been deleted"), True

    def product_delete_id(self, id):
        xml = xmlrenderer.XMLRenderer()

        cur = self._db.cursor()

        sql = """DELETE FROM mirror_products WHERE id=%s"""
        cur.execute(sql, (id,))

        sql = """DELETE FROM mirror_product_langs WHERE product_id=%s"""
        cur.execute(sql, (id,))

        sql = """DELETE FROM mirror_locations WHERE product_id=%s"""
        cur.execute(sql, (id,))

        self._db.commit()

        cur.close()

        return xml.success("SUCCESS: product has been deleted"), True

    def product_language_add(self, product, languages):
        xml = xmlrenderer.XMLRenderer()

        product_exists, product_id = self.product_exists(product)
        if not product_exists:
            return xml.error("Product not found.", errno=102), False

        cur = self._db.cursor()

        for lang in languages:
            sql = """INSERT INTO mirror_product_langs (product_id, language) VALUES (%s, %s)"""
            cur.execute(sql, (product_id, lang))

        self._db.commit()

        cur.close()

        xml.prepare_products(self.get_products_info([product_id]))
        return xml.render(), True

    def product_language_delete(self, product, languages):
        xml = xmlrenderer.XMLRenderer()

        product_exists, product_id = self.product_exists(product)
        if not product_exists:
            return xml.error("Product not found.", errno=102), False

        cur = self._db.cursor()

        if languages[0] == "*":
            sql = """DELETE FROM mirror_product_langs WHERE product_id=%s"""
            cur.execute(sql, (product_id,))
        else:
            for lang in languages:
                sql = """DELETE FROM mirror_product_langs WHERE product_id=%s AND language=%s"""
                cur.execute(sql, (product_id, lang))

        self._db.commit()

        cur.close()

        return xml.success("SUCCESS: language has been deleted"), True

    def mirror_list(self):
        xml = xmlrenderer.XMLRenderer()

        cur = self._db.cursor()

        sql = """SELECT baseurl FROM mirror_mirrors WHERE active=1"""
        cur.execute(sql)

        res = cur.fetchall()

        mirrors = []
        for line in res:
            mirrors.append({"baseurl": line[0]})

        cur.close()

        xml.prepare_mirrors(mirrors)
        return xml.render(), True

    def uptake(self, product, os, fuzzy):
        xml = xmlrenderer.XMLRenderer()

        if product is None and os is None:
            return (
                xml.error("product and/or os are required GET parameters.", errno=101),
                False,
            )

        cur = self._db.cursor()

        product_names = None
        if product:
            if fuzzy:
                sql = """SELECT name FROM mirror_products WHERE name LIKE %s;"""
                product = "%" + product + "%"
            else:
                sql = """SELECT name FROM mirror_products WHERE name = %s;"""

            cur.execute(sql, (product,))

            res = cur.fetchall()
            product_names = [line[0] for line in res]
            if not product_names:
                return xml.error("No products found", errno=102), False

        os_names = None
        if os:
            if fuzzy:
                sql = """SELECT name FROM mirror_os WHERE name LIKE %s;"""
                os = "%" + os + "%"
            else:
                sql = """SELECT name FROM mirror_os WHERE name = %s;"""

            cur.execute(sql, (os,))

            res = cur.fetchall()
            os_names = [line[0] for line in res]
            if not os_names:
                return xml.error("No OSes found", errno=102), False

        cur.close()

        xml.prepare_uptake_fake(products=product_names, oses=os_names)
        return xml.render(), True

    def create_update_alias(self, alias, related_product):
        xml = xmlrenderer.XMLRenderer()

        if not alias:
            return xml.error("Alias name not provided", errno=102), False
        if not related_product:
            return xml.error("Related product name not provided", errno=103), False
        product_exists, product_id = self.product_exists(related_product)
        if not product_exists:
            return (
                xml.error(
                    "You must specify a valid product to match with an alias", errno=103
                ),
                False,
            )
        alias_name_match, product_id = self.product_exists(alias)
        if alias_name_match:
            return (
                xml.error(
                    "You cannot create an alias with the same name as a product",
                    errno=104,
                ),
                False,
            )

        alias_exists, alias_id = self.alias_exists(alias)

        cur = self._db.cursor()
        if alias_exists:
            sql = """UPDATE mirror_aliases SET related_product=%s WHERE alias=%s"""
            cur.execute(sql, (related_product, alias))
        else:
            sql = """INSERT INTO mirror_aliases (alias, related_product) VALUES (%s, %s)"""
            cur.execute(sql, (alias, related_product))

        self._db.commit()

        cur.close()

        return xml.success("Created/updated alias " + alias), True

    def os_exists(self, os):
        sql = """SELECT id FROM mirror_os WHERE name=%s;"""

        cur = self._db.cursor()
        cur.execute(sql, (os,))

        res = cur.fetchall()

        cur.close()

        if len(res) > 0:
            return True, res[0][0]
        else:
            return False, []

    def product_exists(self, product):
        sql = """SELECT id FROM mirror_products WHERE name=%s;"""

        cur = self._db.cursor()
        cur.execute(sql, (product,))

        res = cur.fetchall()

        cur.close()

        if len(res) > 0:
            return True, res[0][0]
        else:
            return False, []

    def location_exists(self, os, product):
        sql = """SELECT ml.id FROM mirror_locations ml JOIN mirror_os mo ON ml.os_id=mo.id JOIN mirror_products mp ON ml.product_id=mp.id WHERE mo.name=%s AND mp.name=%s;"""

        cur = self._db.cursor()
        cur.execute(sql, (os, product))

        res = cur.fetchall()

        cur.close()

        if len(res) > 0:
            return True, res[0][0]
        else:
            return False, []

    def alias_exists(self, alias):
        sql = """SELECT id FROM mirror_aliases WHERE alias=%s;"""

        cur = self._db.cursor()
        cur.execute(sql, (alias,))

        res = cur.fetchall()

        cur.close()

        if len(res) > 0:
            return True, res[0][0]
        else:
            return False, []

    def location_id_valid(self, location_id):
        sql = """SELECT id FROM mirror_locations WHERE id=%s;"""

        cur = self._db.cursor()
        cur.execute(sql, (location_id,))

        res = cur.fetchall()

        cur.close()

        return len(res) > 0

    def get_products_info(self, ids):
        sql = """SELECT mp.id, mp.name, mpl.language FROM mirror_products mp JOIN mirror_product_langs mpl ON mp.id=mpl.product_id WHERE mp.id=%s"""

        cur = self._db.cursor()
        products = []
        for id in ids:
            cur.execute(sql, (id,))
            res = cur.fetchall()
            if res == []:
                continue
            prod = {"id": res[0][0], "name": res[0][1]}
            languages = []
            for line in res:
                languages.append(line[2])

            prod["languages"] = languages

            products.append(prod)

        return products

    def get_locations_info(self, ids):
        sql = """SELECT ml.id, ml.product_id, mp.name, path, mo.name FROM mirror_locations ml JOIN mirror_products mp ON ml.product_id=mp.id JOIN mirror_os mo ON mo.id=ml.os_id WHERE mp.id=%s"""

        cur = self._db.cursor()
        products = []
        for id in ids:
            cur.execute(sql, (id,))
            res = cur.fetchall()
            if res == []:
                continue
            prod = {"id": res[0][1], "name": res[0][2]}
            locations = []
            for line in res:
                locations.append({"id": line[0], "path": line[3], "os_name": line[4]})

            prod["locations"] = locations

            products.append(prod)

        return products

    """ TEST HELPER FUNCTIONS """

    def _reset_db(self):
        cur = self._db.cursor()

        for line in open("data.sql"):
            cur.execute(line)

        cur.close()
        self._db.commit()
