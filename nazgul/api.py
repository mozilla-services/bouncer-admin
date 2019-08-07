from flask import Flask, render_template, request, Response, Blueprint
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

from nazgul.mysql_model import MySQLModel, ModelError
import nazgul.xmlrenderer as xmlrenderer
import urllib.parse
import os, time, logging, json

bp = Blueprint("api", __name__, url_prefix="/api")
hb = Blueprint("heartbeat", __name__)

POST_SIZE_LIMIT = 500 * 1024

auth = HTTPBasicAuth()

usr_imp = json.loads(os.environ.get("AUTH_USERS", '{"admin":"admin"}'))
users = dict()
for usr in usr_imp:
    users[usr] = generate_password_hash(usr_imp[usr])

test_db = os.environ.get("DATABASE_URL", "127.0.0.1")
username = os.environ.get("DB_USER", "root")
password = os.environ.get("DB_PASS", "")
msm = MySQLModel(host=test_db, user=username, password=password)

# Setup logging
logger = logging.getLogger("nazgul")
logger.setLevel(logging.DEBUG)

fh = logging.FileHandler("nazgul.log")
fh.setLevel(logging.DEBUG)

logger.addHandler(fh)

def verify_content_length(max_length):
    return request.content_length and request.content_length <= max_length


@auth.verify_password
def verify_password(username, password):
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


@hb.route("/", methods=["GET", "POST"])
@auth.login_required
def home():
    return Response("Nazgul", mimetype="text/plain")


@hb.route("/__heartbeat__", methods=["GET"])
def heartbeat():
    return Response("OK", mimetype="text/plain")


@hb.route("/__lbheartbeat__", methods=["GET"])
def lbheartbeat():
    return Response("OK", mimetype="text/plain")


@bp.route("/", methods=["GET", "POST"])
@auth.login_required
def index():
    return Response("Nazgul API", mimetype="text/plain")


@bp.route("/location_show/", methods=["GET"])
@auth.login_required
def location_show():
    xml = xmlrenderer.XMLRenderer()

    product = request.args.get("product")
    fuzzy = request.args.get("fuzzy", "").lower() == "true"
    if product is None:
        data = xml.error("The GET parameter product is required", errno=103)
        return Response(data, mimetype="text/xml"), 400

    try:
        # product, locations = msm.location_show(product, fuzzy)
        products = msm.product_show(product, fuzzy)
        for product in products:
            locations = msm.get_locations(product["id"])
            xml.prepare_locations(product, locations)
        data = xml.render()
        status = 200
    except Exception:
        data = xml.error("Unknown error")
        status = 500

    return Response(data, mimetype="text/xml"), status


@bp.route("/location_add/", methods=["POST"])
@auth.login_required
def location_add():
    xml = xmlrenderer.XMLRenderer()
    
    if not verify_content_length(POST_SIZE_LIMIT):
        data = xml.error("POST request length exceeded 500KB", errno=101)
        return Response(data, mimetype="text/xml"), 400

    product = request.form.get("product", None)
    os = request.form.get("os", None)
    path = request.form.get("path", None)
    if not (product and os and path):
        data = xml.error(
            "product, os, and path are required POST parameters.", errno=101
        )
        return Response(data, mimetype="text/xml"), 400

    try:
        res = msm.location_add(product, os, path)
        for p in res:
            prod = {"id": p["id"], "name": p["name"]}
            xml.prepare_locations(prod, p["locations"])
        data = xml.render()
        status = 200
    except ModelError as e:
        data = xml.error(e.message, errno=e.errno)
        status = 400
    except Exception:
        data = xml.error("Unknown error")
        status = 500

    return Response(data, mimetype="text/xml"), status


@bp.route("/location_modify/", methods=["POST"])
@auth.login_required
def location_modify():
    xml = xmlrenderer.XMLRenderer()

    if not verify_content_length(POST_SIZE_LIMIT):
        data = xml.error("POST request length exceeded 500KB", errno=101)
        return Response(data, mimetype="text/xml"), 400

    product = request.form.get("product", None)
    os = request.form.get("os", None)
    path = request.form.get("path", None)
    try:
        res = msm.location_modify(product, os, path)
        for p in res:
            prod = {"id": p["id"], "name": p["name"]}
            xml.prepare_locations(prod, p["locations"])
        data = xml.render()
        status = 200
    except ModelError as e:
        data = xml.error(e.message, errno=e.errno)
        status = 400
    except Exception:
        data = xml.error("Unknown error")
        status = 500

    return Response(data, mimetype="text/xml"), status


@bp.route("/location_delete/", methods=["POST"])
@auth.login_required
def location_delete():
    xml = xmlrenderer.XMLRenderer()

    if not verify_content_length(POST_SIZE_LIMIT):
        data = xml.error("POST request length exceeded 500KB", errno=101)
        return Response(data, mimetype="text/xml"), 400

    location_id = request.form.get("location_id", None)
    if not location_id:
        data = xml.error("location_id is required.", errno=101)
        return Response(data, mimetype="text/xml"), 400

    try:
        res = msm.location_delete(location_id)
        data = xml.success(res)
        status = 200
    except ModelError as e:
        data = xml.error(e.message, errno=e.errno)
        status = 400
    except Exception:
        data = xml.error("Unknown error")
        status = 500
    return Response(data, mimetype="text/xml"), status


@bp.route("/product_show/", methods=["GET"])
@auth.login_required
def product_show():
    xml = xmlrenderer.XMLRenderer()

    product = request.args.get("product")
    fuzzy = request.args.get("fuzzy", "").lower() == "true"
    try:
        res = msm.product_show(product, fuzzy)
        xml.prepare_products(res)
        data = xml.render()
        status = 200
    except Exception:
        data = xml.error("Unknown error")
        status = 500

    return Response(data, mimetype="text/xml"), status


@bp.route("/product_add/", methods=["POST"])
@auth.login_required
def product_add():
    xml = xmlrenderer.XMLRenderer()

    if not verify_content_length(POST_SIZE_LIMIT):
        data = xml.error("POST request length exceeded 500KB", errno=101)
        return Response(data, mimetype="text/xml"), 400

    product = request.form.get("product", None)
    languages = request.form.getlist("languages", None)
    ssl_only = request.form.get("ssl_only", "").lower() == "true"
    try:
        res = msm.product_add(product, languages, ssl_only)
        xml.prepare_products(res)
        data = xml.render()
        status = 200
    except ModelError as e:
        data = xml.error(e.message, errno=e.errno)
        status = 400
    except Exception:
        data = xml.error("Unknown error")
        status = 500

    return Response(data, mimetype="text/xml"), status


@bp.route("/product_delete/", methods=["POST"])
@auth.login_required
def product_delete():
    xml = xmlrenderer.XMLRenderer()

    if not verify_content_length(POST_SIZE_LIMIT):
        data = xml.error("POST request length exceeded 500KB", errno=101)
        return Response(data, mimetype="text/xml"), 400

    product = request.form.get("product", None)
    product_id = request.form.get("product_id", None)

    try:
        if product is None:
            res = msm.product_delete_id(product_id)
        else:
            res = msm.product_delete_name(product)
        data = xml.success(res)
        status = 200
    except ModelError as e:
        data = xml.error(e.message, errno=e.errno)
        status = 400
    except Exception:
        data = xml.error("Unknown error")
        status = 500

    return Response(data, mimetype="text/xml"), status


@bp.route("/product_language_add/", methods=["POST"])
@auth.login_required
def product_language_add():
    xml = xmlrenderer.XMLRenderer()

    if not verify_content_length(POST_SIZE_LIMIT):
        data = xml.error("POST request length exceeded 500KB", errno=101)
        return Response(data, mimetype="text/xml"), 400

    product = request.form.get("product", None)
    languages = request.form.getlist("languages", None)
    try:
        res = msm.product_language_add(product, languages)
        xml.prepare_products(res)
        data = xml.render()
        status = 200
    except ModelError as e:
        data = xml.error(e.message, errno=e.errno)
        status = 400
    except Exception:
        data = xml.error("Unknown error")
        status = 500
    return Response(data, mimetype="text/xml"), status


@bp.route("/product_language_delete/", methods=["POST"])
@auth.login_required
def product_language_delete():
    xml = xmlrenderer.XMLRenderer()

    if not verify_content_length(POST_SIZE_LIMIT):
        data = xml.error("POST request length exceeded 500KB", errno=101)
        return Response(data, mimetype="text/xml"), 400

    product = request.form.get("product", None)
    languages = request.form.getlist("languages", None)
    try:
        res = msm.product_language_delete(product, languages)
        data = xml.success(res)
        status = 200
    except ModelError as e:
        data = xml.error(e.message, errno=e.errno)
        status = 400
    except Exception:
        data = xml.error("Unknown error")
        status = 500
    return Response(data, mimetype="text/xml"), status


@bp.route("/mirror_list/", methods=["GET"])
@auth.login_required
def mirror_list():
    xml = xmlrenderer.XMLRenderer()

    res = msm.mirror_list()
    xml.prepare_mirrors(res)
    data = xml.render()
    return Response(data, mimetype="text/xml"), 200


@bp.route("/uptake/", methods=["GET"])
@auth.login_required
def uptake():
    xml = xmlrenderer.XMLRenderer()

    product = request.args.get("product")
    os = request.args.get("os")
    fuzzy = request.args.get("fuzzy", "").lower() == "true"
    if product is None and os is None:
        data = xml.error("product and/or os are required GET parameters.", errno=101)
        return Response(data, mimetype="text/xml"), 400

    try:
        res = msm.uptake(product, os, fuzzy)
        xml.prepare_uptake_fake(products=res["product_names"], oses=res["os_names"])
        data = xml.render()
        status = 200
    except ModelError as e:
        # Error no. for /uptake is always 102 in Tuxedo (Should this be changed in Nazgul?)
        data = xml.error(e.message, errno=102)
        status = 400
    except Exception:
        data = xml.error("Unknown error")
        status = 500
    return Response(data, mimetype="text/xml"), status


@bp.route("/create_update_alias/", methods=["POST"])
@auth.login_required
def create_update_alias():
    xml = xmlrenderer.XMLRenderer()

    if not verify_content_length(POST_SIZE_LIMIT):
        data = xml.error("POST request length exceeded 500KB", errno=101)
        return Response(data, mimetype="text/xml"), 400

    alias = request.form.get("alias", None)
    related_product = request.form.get("related_product", None)

    if not alias:
        data = xml.error("Alias name not provided", errno=102)
        return Response(data, mimetype="text/xml"), 400
    if not related_product:
        data = xml.error("Related product name not provided", errno=103)
        return Response(data, mimetype="text/xml"), 400

    try:
        res = msm.create_update_alias(alias, related_product)
        data = xml.success(res)
        status = 200
    except ModelError as e:
        data = xml.error(e.message, errno=e.errno)
        status = 400
    except Exception:
        data = xml.error("Unknown error")
        status = 500
    return Response(data, mimetype="text/xml"), status
