from flask import Flask, render_template, request, Response, Blueprint
from flask_mysqldb import MySQL
from nazgul.mysql_model import MySQLModel

bp = Blueprint('api', __name__, url_prefix='/api')

msm = MySQLModel()

@bp.route('/', methods=['GET', 'POST'])
def index():
    return 'Nazgul API'

@bp.route('/location_show', methods=['GET'])
def location_show():
    product = request.args.get('product')
    fuzzy = request.args.get('fuzzy') == 'True'
    data, success = msm.location_show(product, fuzzy)
    return Response(data, mimetype='text/xml'), 200 if success else 400 

@bp.route('/location_add', methods=['POST'])
def location_add():
    product = request.form.get('product', None)
    os = request.form.get('os', None)
    path = request.form.get('path', None)
    data, success = msm.location_add(product, os, path)
    return Response(data, mimetype='text/xml'), 200 if success else 400 

@bp.route('/location_modify', methods=['POST'])
def location_modify():
    product = request.form.get('product', None)
    os = request.form.get('os', None)
    path = request.form.get('path', None)
    return Response(msm.location_modify(product, os, path), mimetype='text/xml')

@bp.route('/location_delete', methods=['POST'])
def location_delete():
    product = request.form.get('product', None)
    os = request.form.get('os', None)
    data, success = msm.location_delete(product, os)
    return Response(data, mimetype='text/xml'), 200 if success else 400 

@bp.route('/product_show', methods=['GET'])
def product_show():
    product = request.args.get('product')
    fuzzy = request.args.get('fuzzy') == 'True'
    data, success = msm.product_show(product, fuzzy)
    return Response(data, mimetype='text/xml'), 200 if success else 400 


@bp.route('/product_add', methods=['POST'])
def product_add():
    product = request.form.get('product', None)
    languages = request.form.get('languages', None)
    ssl_only = request.form.get('ssl_only') == 'True'
    data, success = msm.product_add(product, languages, ssl_only)
    return Response(data, mimetype='text/xml'), 200 if success else 400 


@bp.route('/product_delete', methods=['POST'])
def product_delete():
    product = request.form.get('product', None)
    product_id = request.form.get('product_id', None)

    if product is None:
        data, success = msm.product_delete_id(product_id)
        return Response(data, mimetype='text/xml'), 200 if success else 400 

    else:
        data, success = msm.product_delete_name(product)
        return Response(data, mimetype='text/xml'), 200 if success else 400 


@bp.route('/product_language_add', methods=['POST'])
def product_language_add():
    product = request.form.get('product', None)
    languages = request.form.get('languages', None)
    data, success = msm.product_language_add(product, languages)
    return Response(data, mimetype='text/xml'), 200 if success else 400 


@bp.route('/product_language_delete', methods=['POST'])
def product_language_delete():
    product = request.form.get('product', None)
    languages = request.form.get('languages', None)
    data, success = msm.product_language_delete(product, languages)
    return Response(data, mimetype='text/xml'), 200 if success else 400

@bp.route('/mirror_list', methods=['GET'])
def mirror_list():
    data, success = msm.mirror_list()
    return Response(data, mimetype='text/xml'), 200 if success else 400
    

@bp.route('/uptake', methods=['GET'])
def uptake():
    product = request.args.get('product')
    os = request.args.get('os')
    fuzzy = request.args.get('fuzzy') == 'True'

    data, success = msm.uptake(product, os, fuzzy)
    return Response(data, mimetype='text/xml'), 200 if success else 400