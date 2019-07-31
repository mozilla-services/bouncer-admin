from flask import Flask, render_template, request
import mysql.connector


class MySQLModel:
    def __init__(
        self, user="root", host="127.0.0.1", password="", db="bouncer"
    ):
        self.db_config = {
            "database": db,
            "user": user,
            "password": password,
            "host": host,
            "autocommit": True
        }
        # TODO: Should I have autocommit always True?
        self._db = mysql.connector.connect(**self.db_config)

    def index(self):
        return "Welcome to Nazgul"

    def get_locations(self, product):
        sql = """SELECT ml.id, ml.path, mo.name FROM mirror_locations ml JOIN mirror_os mo ON ml.os_id=mo.id WHERE product_id=%s;"""

        cur = self._get_cursor()
        cur.execute(sql, (product,))

        res = cur.fetchall()

        cur.close()

        locations = []
        for line in res:
            locations.append({"id": line[0], "path": line[1], "os_name": line[2]})

        return locations

    def location_add(self, product, os, path):
        os_exists, os_id = self.os_exists(os)
        product_exists, product_id = self.product_exists(product)
        location_exists, location_id = self.location_exists(os, product)

        if not os_exists:
            raise ModelError("FAILED: '" + os + "' does not exist", 106)
        if not product_exists:
            raise ModelError("FAILED: '" + product + "' does not exist", 105)
        if location_exists:
            raise ModelError("The specified location already exists.", 104)

        sql = """INSERT INTO mirror_locations (product_id, os_id, path) VALUES (%s,%s,%s)"""

        cur = self._get_cursor()
        cur.execute(sql, (product_id, os_id, path))

        self._db.commit()

        cur.close()

        products = self.get_locations_info([product_id])
        return products

    def location_modify(self, product, os, path):
        os_exists, os_id = self.os_exists(os)
        product_exists, product_id = self.product_exists(product)
        location_exists, location_id = self.location_exists(os, product)

        if not os_exists:
            raise ModelError("FAILED: '" + os + "' does not exist", 106)
        if not product_exists:
            raise ModelError("FAILED: '" + product + "' does not exist", 105)
        if not location_exists:
            raise ModelError(
                "FAILED: location '" + product + "' on OS '" + os + "' does not exist",
                104,
            )

        sql = """UPDATE mirror_locations SET path=%s WHERE os_id=%s AND product_id=%s"""

        cur = self._get_cursor()
        cur.execute(sql, (path, os_id, product_id))

        self._db.commit()

        cur.close()

        products = self.get_locations_info([product_id])
        return products

    def location_delete(self, location_id):
        if not self.location_id_valid(location_id):
            raise ModelError("No location found.", 102)

        sql = """DELETE FROM mirror_locations WHERE id=%s"""

        cur = self._get_cursor()
        cur.execute(sql, (location_id,))

        self._db.commit()

        cur.close()

        return "SUCCESS: location has been deleted"

    def product_show(self, product, fuzzy):
        if fuzzy:
            sql = """SELECT id FROM mirror_products WHERE name LIKE %s;"""
            product = "%" + product + "%"
        else:
            sql = """SELECT id FROM mirror_products WHERE name = %s;"""

        cur = self._get_cursor()
        cur.execute(sql, (product,))

        res = cur.fetchall()

        cur.close()

        ids = []
        for line in res:
            ids.append(line[0])

        products = self.get_products_info(ids)
        return products

    def product_add(self, product, languages, ssl_only):
        product_exists, product_id = self.product_exists(product)
        if product_exists:
            raise ModelError("product already exists.", 104)

        sql = """INSERT INTO mirror_products (name, ssl_only) VALUES (%s, %s)"""

        cur = self._get_cursor()
        cur.execute(sql, (product, int(ssl_only)))
        self._db.commit()

        product_exists, product_id = self.product_exists(product)
        for lang in languages:
            sql = """INSERT INTO mirror_product_langs (product_id, language) VALUES (%s, %s)"""
            cur.execute(sql, (product_id, lang))

        self._db.commit()

        cur.close()

        products = self.get_products_info([product_id])
        return products

    def product_delete_name(self, name):
        product_exists, product_id = self.product_exists(name)
        if not product_exists:
            raise ModelError("No product found.", 102)

        cur = self._get_cursor()

        sql = """DELETE FROM mirror_products WHERE id=%s"""
        cur.execute(sql, (product_id,))

        sql = """DELETE FROM mirror_product_langs WHERE product_id=%s"""
        cur.execute(sql, (product_id,))

        sql = """DELETE FROM mirror_locations WHERE product_id=%s"""
        cur.execute(sql, (product_id,))

        self._db.commit()

        cur.close()

        return "SUCCESS: product has been deleted"

    def product_delete_id(self, id):
        cur = self._get_cursor()

        sql = """DELETE FROM mirror_products WHERE id=%s"""
        cur.execute(sql, (id,))

        sql = """DELETE FROM mirror_product_langs WHERE product_id=%s"""
        cur.execute(sql, (id,))

        sql = """DELETE FROM mirror_locations WHERE product_id=%s"""
        cur.execute(sql, (id,))

        self._db.commit()

        cur.close()

        return "SUCCESS: product has been deleted"

    def product_language_add(self, product, languages):
        product_exists, product_id = self.product_exists(product)
        if not product_exists:
            raise ModelError("Product not found.", 102)

        cur = self._get_cursor()

        for lang in languages:
            sql = """INSERT INTO mirror_product_langs (product_id, language) VALUES (%s, %s)"""
            cur.execute(sql, (product_id, lang))

        self._db.commit()

        cur.close()

        products = self.get_products_info([product_id])
        return products

    def product_language_delete(self, product, languages):
        product_exists, product_id = self.product_exists(product)
        if not product_exists:
            raise ModelError("Product not found.", 102)

        cur = self._get_cursor()

        if languages[0] == "*":
            sql = """DELETE FROM mirror_product_langs WHERE product_id=%s"""
            cur.execute(sql, (product_id,))
        else:
            for lang in languages:
                sql = """DELETE FROM mirror_product_langs WHERE product_id=%s AND language=%s"""
                cur.execute(sql, (product_id, lang))

        self._db.commit()

        cur.close()

        return "SUCCESS: language has been deleted"

    def mirror_list(self):
        cur = self._get_cursor()

        sql = """SELECT baseurl FROM mirror_mirrors WHERE active=1"""
        cur.execute(sql)

        res = cur.fetchall()

        mirrors = []
        for line in res:
            mirrors.append({"baseurl": line[0]})

        cur.close()

        return mirrors

    def uptake(self, product, os, fuzzy):
        cur = self._get_cursor()

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
                raise ModelError("No products found", 102)

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
                raise ModelError("No OSes found", 103)

        cur.close()

        return {"product_names": product_names, "os_names": os_names}

    def create_update_alias(self, alias, related_product):
        product_exists, product_id = self.product_exists(related_product)
        if not product_exists:
            raise ModelError(
                "You must specify a valid product to match with an alias", 103
            )
        alias_name_match, product_id = self.product_exists(alias)
        if alias_name_match:
            raise ModelError(
                "You cannot create an alias with the same name as a product", 104
            )

        alias_exists, alias_id = self.alias_exists(alias)

        cur = self._get_cursor()
        if alias_exists:
            sql = """UPDATE mirror_aliases SET related_product=%s WHERE alias=%s"""
            cur.execute(sql, (related_product, alias))
        else:
            sql = """INSERT INTO mirror_aliases (alias, related_product) VALUES (%s, %s)"""
            cur.execute(sql, (alias, related_product))

        self._db.commit()

        cur.close()

        return "Created/updated alias " + alias

    def os_exists(self, os):
        sql = """SELECT id FROM mirror_os WHERE name=%s;"""

        cur = self._get_cursor()
        cur.execute(sql, (os,))

        res = cur.fetchall()

        cur.close()

        if len(res) > 0:
            return True, res[0][0]
        else:
            return False, []

    def product_exists(self, product):
        sql = """SELECT id FROM mirror_products WHERE name=%s;"""

        cur = self._get_cursor()
        cur.execute(sql, (product,))

        res = cur.fetchall()

        cur.close()

        if len(res) > 0:
            return True, res[0][0]
        else:
            return False, []

    def location_exists(self, os, product):
        sql = """SELECT ml.id FROM mirror_locations ml JOIN mirror_os mo ON ml.os_id=mo.id JOIN mirror_products mp ON ml.product_id=mp.id WHERE mo.name=%s AND mp.name=%s;"""

        cur = self._get_cursor()
        cur.execute(sql, (os, product))

        res = cur.fetchall()

        cur.close()

        if len(res) > 0:
            return True, res[0][0]
        else:
            return False, []

    def alias_exists(self, alias):
        sql = """SELECT id FROM mirror_aliases WHERE alias=%s;"""

        cur = self._get_cursor()
        cur.execute(sql, (alias,))

        res = cur.fetchall()

        cur.close()

        if len(res) > 0:
            return True, res[0][0]
        else:
            return False, []

    def location_id_valid(self, location_id):
        sql = """SELECT id FROM mirror_locations WHERE id=%s;"""

        cur = self._get_cursor()
        cur.execute(sql, (location_id,))

        res = cur.fetchall()

        cur.close()

        return len(res) > 0

    def get_products_info(self, ids):
        sql = """SELECT mp.id, mp.name, mpl.language FROM mirror_products mp JOIN mirror_product_langs mpl ON mp.id=mpl.product_id WHERE mp.id=%s"""

        cur = self._get_cursor()
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

        cur = self._get_cursor()
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

    def _get_cursor(self):
        try:
            cur = self._db.cursor()
        except mysql.connector.errors.OperationalError:
            self._db = mysql.connector.connect(**self.db_config)
            cur = self._db.cursor()
        return cur


class ModelError(Exception):
    def __init__(self, message, errno):
        self.message = message
        self.errno = errno
