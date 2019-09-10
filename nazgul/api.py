import os
import time
import logging
import json

from flask import request, Response, Blueprint, g, current_app
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash

from .db import get_db
from .mysql_model import MySQLModel, ModelError
from . import xmlrenderer

bp = Blueprint("api", __name__, url_prefix="/api")
hb = Blueprint("heartbeat", __name__)

auth = HTTPBasicAuth()

# Setup logging
logger = logging.getLogger("nazgul")
logger.setLevel(logging.DEBUG)

fh = logging.FileHandler("nazgul.log")
fh.setLevel(logging.DEBUG)

logger.addHandler(fh)


def get_users():
    if "users" not in g:
        users = {}
        for user, password in json.loads(current_app.config["AUTH_USERS"]).items():
            users[user] = generate_password_hash(password)

        g.users = users

    return g.users


class XMLApiError(Exception):
    def __init__(self, message, status_code, errno=0):
        Exception.__init__(self)
        self.status_code = status_code
        self.message = message
        self.errno = errno


@bp.errorhandler(XMLApiError)
def handle_xml_api_error(error):
    xml = xmlrenderer.XMLRenderer()
    data = xml.error(error.message, errno=error.errno)
    return Response(data, mimetype="text/xml"), error.status_code


@bp.errorhandler(413)
def request_entity_too_large(error):
    xml = xmlrenderer.XMLRenderer()
    data = xml.error("POST request length exceeded 500KB", errno=101)
    return Response(data, mimetype="text/xml"), 413


@auth.verify_password
def verify_password(username, password):
    users = get_users()
    if username in users:
        logger.info(
            "{0} - {1} - {2} - {3}".format(
                time.strftime("%m/%d/%Y %H:%M:%S"),
                request.remote_addr,
                username,
                request.full_path,
            )
        )
        return check_password_hash(users.get(username), password)
    return False


@hb.route("/", methods=["GET"])
def home():
    return Response("Nazgul", mimetype="text/plain")


@hb.route("/__heartbeat__", methods=["GET"])
def heartbeat():
    return Response("OK", mimetype="text/plain")


@hb.route("/__lbheartbeat__", methods=["GET"])
def lbheartbeat():
    return Response("OK", mimetype="text/plain")


@bp.route("/", methods=["GET"])
def index():
    return Response("Nazgul API", mimetype="text/plain")


@bp.route("/location_show/", methods=["GET"])
@bp.route("/location_show", methods=["GET"])
def location_show():
    xml = xmlrenderer.XMLRenderer()

    product = request.args.get("product")
    fuzzy = request.args.get("fuzzy", "").lower() == "true"
    if product is None:
        raise XMLApiError("The GET parameter product is required", 400, 103)

    products = get_db().product_show(product, fuzzy)

    for product in products:
        locations = get_db().get_locations(product["id"])
        xml.prepare_locations(product, locations)
    data = xml.render()
    return Response(data, mimetype="text/xml"), 200


@bp.route("/location_add/", methods=["POST"])
@bp.route("/location_add", methods=["POST"])
@auth.login_required
def location_add():
    xml = xmlrenderer.XMLRenderer()

    product = request.form.get("product", None)
    os = request.form.get("os", None)
    path = request.form.get("path", None)
    if not (product and os and path):
        raise XMLApiError(
            "product, os, and path are required POST parameters.", 400, 101
        )

    try:
        res = get_db().location_add(product, os, path)
    except ModelError as e:
        raise XMLApiError(e.message, 400, e.errno)

    for p in res:
        prod = {"id": p["id"], "name": p["name"]}
        xml.prepare_locations(prod, p["locations"])
    data = xml.render()

    return Response(data, mimetype="text/xml"), 200


@bp.route("/location_modify/", methods=["POST"])
@bp.route("/location_modify", methods=["POST"])
@auth.login_required
def location_modify():
    xml = xmlrenderer.XMLRenderer()

    product = request.form.get("product", None)
    os = request.form.get("os", None)
    path = request.form.get("path", None)
    try:
        res = get_db().location_modify(product, os, path)
    except ModelError as e:
        raise XMLApiError(e.message, 400, e.errno)

    for p in res:
        prod = {"id": p["id"], "name": p["name"]}
        xml.prepare_locations(prod, p["locations"])
    data = xml.render()

    return Response(data, mimetype="text/xml"), 200


@bp.route("/location_delete/", methods=["POST"])
@bp.route("/location_delete", methods=["POST"])
@auth.login_required
def location_delete():
    xml = xmlrenderer.XMLRenderer()

    location_id = request.form.get("location_id", None)
    if not location_id:
        raise XMLApiError("location_id is required.", 400, 101)

    try:
        get_db().location_delete(location_id)
    except ModelError as e:
        raise XMLApiError(e.message, 400, e.errno)

    data = xml.success("SUCCESS: location has been deleted")
    return Response(data, mimetype="text/xml"), 200


@bp.route("/product_show/", methods=["GET"])
@bp.route("/product_show", methods=["GET"])
def product_show():
    xml = xmlrenderer.XMLRenderer()

    product = request.args.get("product")
    fuzzy = request.args.get("fuzzy", "").lower() == "true"

    res = get_db().product_show(product, fuzzy)
    xml.prepare_products(res)
    data = xml.render()

    return Response(data, mimetype="text/xml"), 200


@bp.route("/product_add/", methods=["POST"])
@bp.route("/product_add", methods=["POST"])
@auth.login_required
def product_add():
    xml = xmlrenderer.XMLRenderer()

    product = request.form.get("product", None)
    languages = request.form.getlist("languages", None)
    ssl_only = request.form.get("ssl_only", "").lower() == "true"
    try:
        res = get_db().product_add(product, languages, ssl_only)
    except ModelError as e:
        raise XMLApiError(e.message, 400, e.errno)

    xml.prepare_products(res)
    data = xml.render()

    return Response(data, mimetype="text/xml"), 200


@bp.route("/product_delete/", methods=["POST"])
@bp.route("/product_delete", methods=["POST"])
@auth.login_required
def product_delete():
    xml = xmlrenderer.XMLRenderer()

    product = request.form.get("product", None)
    product_id = request.form.get("product_id", None)

    try:
        if product is None:
            get_db().product_delete_id(product_id)
        else:
            get_db().product_delete_name(product)
    except ModelError as e:
        raise XMLApiError(e.message, 400, e.errno)

    data = xml.success("SUCCESS: product has been deleted")

    return Response(data, mimetype="text/xml"), 200


@bp.route("/product_language_add/", methods=["POST"])
@bp.route("/product_language_add", methods=["POST"])
@auth.login_required
def product_language_add():
    xml = xmlrenderer.XMLRenderer()

    product = request.form.get("product", None)
    languages = request.form.getlist("languages", None)
    try:
        res = get_db().product_language_add(product, languages)
    except ModelError as e:
        raise XMLApiError(e.message, 400, e.errno)

    xml.prepare_products(res)
    data = xml.render()

    return Response(data, mimetype="text/xml"), 200


@bp.route("/product_language_delete/", methods=["POST"])
@bp.route("/product_language_delete", methods=["POST"])
@auth.login_required
def product_language_delete():
    xml = xmlrenderer.XMLRenderer()

    product = request.form.get("product", None)
    languages = request.form.getlist("languages", None)
    try:
        get_db().product_language_delete(product, languages)
    except ModelError as e:
        raise XMLApiError(e.message, 400, e.errno)

    data = xml.success("SUCCESS: language has been deleted")

    return Response(data, mimetype="text/xml"), 200


@bp.route("/mirror_list/", methods=["GET"])
@bp.route("/mirror_list", methods=["GET"])
def mirror_list():
    xml = xmlrenderer.XMLRenderer()

    res = get_db().mirror_list()
    xml.prepare_mirrors(res)
    data = xml.render()

    return Response(data, mimetype="text/xml"), 200


@bp.route("/uptake/", methods=["GET"])
@bp.route("/uptake", methods=["GET"])
def uptake():
    xml = xmlrenderer.XMLRenderer()

    product = request.args.get("product")
    os = request.args.get("os")
    fuzzy = request.args.get("fuzzy", "").lower() == "true"
    if product is None and os is None:
        raise XMLApiError("product and/or os are required GET parameters.", 400, 101)

    try:
        res = get_db().uptake(product, os, fuzzy)
    except ModelError as e:
        # Error no. for /uptake is always 102 in Tuxedo (Should this be changed in Nazgul?)
        raise XMLApiError(e.message, 400, 102)

    xml.prepare_uptake_fake(products=res["product_names"], oses=res["os_names"])
    data = xml.render()

    return Response(data, mimetype="text/xml"), 200


@bp.route("/create_update_alias/", methods=["POST"])
@bp.route("/create_update_alias", methods=["POST"])
@auth.login_required
def create_update_alias():
    xml = xmlrenderer.XMLRenderer()

    alias = request.form.get("alias", None)
    related_product = request.form.get("related_product", None)

    if not alias:
        raise XMLApiError("Alias name not provided", 400, 102)
    if not related_product:
        raise XMLApiError("Related product name not provided", 400, 103)

    try:
        get_db().create_update_alias(alias, related_product)
    except ModelError as e:
        raise XMLApiError(e.message, 400, e.errno)

    data = xml.success(f"Created/updated alias {alias}")

    return Response(data, mimetype="text/xml"), 200
