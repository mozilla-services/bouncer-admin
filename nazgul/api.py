from flask import Flask, render_template, request, Response, Blueprint

from nazgul.mysql_model import MySQLModel, ModelError
import nazgul.xmlrenderer as xmlrenderer
import urllib.parse
import os

bp = Blueprint("api", __name__, url_prefix="/api")

test_db = os.environ.get("DATABASE_URL", "127.0.0.1")
msm = MySQLModel(host=test_db)


@bp.route("/", methods=["GET", "POST"])
def index():
    return "Nazgul API"


@bp.route("/location_show/", methods=["GET"])
def location_show():
    xml = xmlrenderer.XMLRenderer()

    product = request.args.get("product")
    fuzzy = request.args.get("fuzzy") == "True"
    if product is None:
        data = xml.error("The GET parameter product is required", errno=103)
        return Response(data, mimetype="text/xml"), 400

    try:
        res = msm.location_show(product, fuzzy)
        for loc in res:
            xml.prepare_locations(loc)
        data = xml.render()
        status = 200
    except Exception:
        data = xml.error("Unknown error")
        status = 400

    return Response(data, mimetype="text/xml"), status


@bp.route("/location_add/", methods=["POST"])
def location_add():
    xml = xmlrenderer.XMLRenderer()

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
            xml.prepare_locations(p)
        data = xml.render()
        status = 200
    except ModelError as e:
        data = xml.error(e.message, errno=e.errno)
        status = 400
    except Exception:
        data = xml.error("Unknown error")
        status = 400

    return Response(data, mimetype="text/xml"), status


@bp.route("/location_modify/", methods=["POST"])
def location_modify():
    xml = xmlrenderer.XMLRenderer()

    product = request.form.get("product", None)
    os = request.form.get("os", None)
    path = request.form.get("path", None)
    try:
        res = msm.location_modify(product, os, path)
        for p in res:
            xml.prepare_locations(p)
        data = xml.render()
        status = 200
    except ModelError as e:
        data = xml.error(e.message, errno=e.errno)
        status = 400
    except Exception:
        data = xml.error("Unknown error")
        status = 400

    return Response(data, mimetype="text/xml"), status


@bp.route("/location_delete/", methods=["POST"])
def location_delete():
    xml = xmlrenderer.XMLRenderer()

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
        status = 400
    return Response(data, mimetype="text/xml"), status


@bp.route("/product_show/", methods=["GET"])
def product_show():
    xml = xmlrenderer.XMLRenderer()

    product = request.args.get("product")
    fuzzy = request.args.get("fuzzy") == "True"
    try:
        res = msm.product_show(product, fuzzy)
        xml.prepare_products(res)
        data = xml.render()
        status = 200
    except Exception:
        data = xml.error("Unknown error")
        status = 400

    return Response(data, mimetype="text/xml"), status


@bp.route("/product_add/", methods=["POST"])
def product_add():
    xml = xmlrenderer.XMLRenderer()

    product = request.form.get("product", None)
    languages = request.form.getlist("languages", None)
    ssl_only = request.form.get("ssl_only") == "True"
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
        status = 400

    return Response(data, mimetype="text/xml"), status


@bp.route("/product_delete/", methods=["POST"])
def product_delete():
    xml = xmlrenderer.XMLRenderer()

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
        status = 400

    return Response(data, mimetype="text/xml"), status


@bp.route("/product_language_add/", methods=["POST"])
def product_language_add():
    xml = xmlrenderer.XMLRenderer()

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
        status = 400
    return Response(data, mimetype="text/xml"), status


@bp.route("/product_language_delete/", methods=["POST"])
def product_language_delete():
    xml = xmlrenderer.XMLRenderer()

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
        status = 400
    return Response(data, mimetype="text/xml"), status


@bp.route("/mirror_list/", methods=["GET"])
def mirror_list():
    xml = xmlrenderer.XMLRenderer()

    res = msm.mirror_list()
    xml.prepare_mirrors(res)
    data = xml.render()
    return Response(data, mimetype="text/xml"), 400


@bp.route("/uptake/", methods=["GET"])
def uptake():
    xml = xmlrenderer.XMLRenderer()

    product = request.args.get("product")
    os = request.args.get("os")
    fuzzy = request.args.get("fuzzy") == "True"
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
        status = 400
    return Response(data, mimetype="text/xml"), status


@bp.route("/create_update_alias/", methods=["POST"])
def create_update_alias():
    xml = xmlrenderer.XMLRenderer()

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
        status = 400
    return Response(data, mimetype="text/xml"), status
