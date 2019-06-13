from flask import Flask, render_template, request, Response, Blueprint
try:
    from nazgul.mysql_model import MySQLModel
    import nazgul.xmlrenderer as xmlrenderer
except:
    from mysql_model import MySQLModel
    import xmlrenderer
import urllib.parse
import ast
import os

bp = Blueprint('api', __name__, url_prefix='/api')

test_db = os.environ.get('DATABASE_URL', '127.0.0.1')
msm = MySQLModel(host=test_db)

@bp.route('/', methods=['GET', 'POST'])
def index():
    return 'Nazgul API'

@bp.route('/location_show', methods=['GET'])
def location_show():
    xml = xmlrenderer.XMLRenderer()

    product = request.args.get('product')
    fuzzy = request.args.get('fuzzy') == 'True'
    if product is None:
        data = xml.error('The GET parameter product is required', errno=103)
        return Response(data, mimetype='text/xml'), 400 

    res, success = msm.location_show(product, fuzzy)
    if success:
        for loc in res:
            xml.prepare_locations(loc)
        data = xml.render()
    else:
        data = xml.error('Unknown error')
    return Response(data, mimetype='text/xml'), 200 if success else 400 

@bp.route('/location_add', methods=['POST'])
def location_add():
    xml = xmlrenderer.XMLRenderer()

    product = request.form.get('product', None)
    os = request.form.get('os', None)
    path = request.form.get('path', None)
    if not (product and os and path):
        data = xml.error('product, os, and path are required POST parameters.', errno=101)
        return Response(data, mimetype='text/xml'), 400

    res, success = msm.location_add(product, os, path)
    if success:
        for p in res:
            xml.prepare_locations(p)
        data = xml.render()
    else:
        if res == 104:
            data = xml.error('The specified location already exists.', errno=104)
        elif res == 105:
            data = xml.error('FAILED: \'' + product + '\' does not exist', errno=105)
        elif res == 106:
            data = xml.error('FAILED: \'' + os + '\' does not exist', errno=106)
        else:
            data = xml.error('Unknown error')
    return Response(data, mimetype='text/xml'), 200 if success else 400 

@bp.route('/location_modify', methods=['POST'])
def location_modify():
    xml = xmlrenderer.XMLRenderer()

    product = request.form.get('product', None)
    os = request.form.get('os', None)
    path = request.form.get('path', None)
    res, success = msm.location_modify(product, os, path)
    if success:
        for p in res:
            xml.prepare_locations(p)
        data = xml.render()
    else:
        if res == 104:
            data = xml.error('FAILED: location \'' + product + '\' on OS \'' + os + '\' does not exist', errno=104)
        elif res == 105:
            data = xml.error('FAILED: \'' + product + '\' does not exist', errno=105)
        elif res == 106:
            data = xml.error('FAILED: \'' + os + '\' does not exist', errno=106)
        else:
            data = xml.error('Unknown error')
    return Response(data, mimetype='text/xml'), 200 if success else 400 

@bp.route('/location_delete', methods=['POST'])
def location_delete():
    xml = xmlrenderer.XMLRenderer()

    location_id = request.form.get('location_id', None)
    if not location_id:
        data = xml.error('location_id is required.', errno=101)
        return Response(data, mimetype='text/xml'), 400 

    res, success = msm.location_delete(location_id)
    if success:
        data = xml.success(res)
    else:
        if res == 102:
            data = xml.error('No location found.', errno=102)
        else:
            data = xml.error('Unknown error')
    return Response(data, mimetype='text/xml'), 200 if success else 400 

@bp.route('/product_show', methods=['GET'])
def product_show():
    xml = xmlrenderer.XMLRenderer()

    product = request.args.get('product')
    fuzzy = request.args.get('fuzzy') == 'True'
    res, success = msm.product_show(product, fuzzy)

    if success:
        xml.prepare_products(res)
        data = xml.render()
    else:
        data = xml.error('Unknown error')
    return Response(data, mimetype='text/xml'), 200 if success else 400 


@bp.route('/product_add', methods=['POST'])
def product_add():
    xml = xmlrenderer.XMLRenderer()

    product = request.form.get('product', None)
    lang_in = request.form.get('languages', None)
    languages = ast.literal_eval(urllib.parse.unquote(lang_in))
    ssl_only = request.form.get('ssl_only') == 'True'
    res, success = msm.product_add(product, languages, ssl_only)

    if success:
        xml.prepare_products(res)
        data = xml.render()
    else:
        if res == 104:
            data = xml.error('product already exists.', errno=104)
        else:
            data = xml.error('Unknown error')
    return Response(data, mimetype='text/xml'), 200 if success else 400 


@bp.route('/product_delete', methods=['POST'])
def product_delete():
    xml = xmlrenderer.XMLRenderer()

    product = request.form.get('product', None)
    product_id = request.form.get('product_id', None)

    if product is None:
        res, success = msm.product_delete_id(product_id)
    else:
        res, success = msm.product_delete_name(product)
    
    if success:
        data = xml.success(res)
    else:
        if res == 102:
            data = xml.error('No product found.', errno=102)
        else:
            data = xml.error('Unknown error')
    return Response(data, mimetype='text/xml'), 200 if success else 400 


@bp.route('/product_language_add', methods=['POST'])
def product_language_add():
    xml = xmlrenderer.XMLRenderer()

    product = request.form.get('product', None)
    lang_in = request.form.get('languages', None)
    languages = ast.literal_eval(urllib.parse.unquote(lang_in))
    res, success = msm.product_language_add(product, languages)

    if success:
        xml.prepare_products(res)
        data = xml.render()
    else:
        if res == 102:
            data = xml.error('Product not found.', errno=102)
        else:
            data = xml.error('Unknown error')
    return Response(data, mimetype='text/xml'), 200 if success else 400 


@bp.route('/product_language_delete', methods=['POST'])
def product_language_delete():
    xml = xmlrenderer.XMLRenderer()

    product = request.form.get('product', None)
    lang_in = request.form.get('languages', None)
    languages = ast.literal_eval(urllib.parse.unquote(lang_in))
    res, success = msm.product_language_delete(product, languages)
    if success:
        data = xml.success(res)
    else:
        if res == 102:
            data = xml.error('Product not found.', errno=102)
        else:
            data = xml.error('Unknown error')
    return Response(data, mimetype='text/xml'), 200 if success else 400

@bp.route('/mirror_list', methods=['GET'])
def mirror_list():
    xml = xmlrenderer.XMLRenderer()

    res, success = msm.mirror_list()
    xml.prepare_mirrors(res)
    data = xml.render()
    return Response(data, mimetype='text/xml'), 200 if success else 400
    

@bp.route('/uptake', methods=['GET'])
def uptake():
    xml = xmlrenderer.XMLRenderer()

    product = request.args.get('product')
    os = request.args.get('os')
    fuzzy = request.args.get('fuzzy') == 'True'
    if product is None and os is None:
        data = xml.error('product and/or os are required GET parameters.', errno=101)
        return Response(data, mimetype='text/xml'), 400

    res, success = msm.uptake(product, os, fuzzy)
    if success:
        xml.prepare_uptake_fake(products=res['product_names'], oses=res['os_names'])
        data = xml.render()
    else:
        if res == 102:
            data = xml.error('No products found', errno=102)
        elif res == 103:
            data = xml.error('No OSes found', errno=102)
        else:
            data = xml.error('Unknown error')
    return Response(data, mimetype='text/xml'), 200 if success else 400

@bp.route('/create_update_alias', methods=['POST'])
def create_update_alias():
    xml = xmlrenderer.XMLRenderer()

    alias = request.form.get('alias', None)
    related_product = request.form.get('related_product', None)

    if not alias:
        data = xml.error('Alias name not provided', errno=102)
        return Response(data, mimetype='text/xml'), 400
    if not related_product:
        data = xml.error('Related product name not provided', errno=103)
        return Response(data, mimetype='text/xml'), 400

    res, success = msm.create_update_alias(alias, related_product)
    if success:
        data = xml.success(res)
    else:
        if res == 103:
            data = xml.error('You must specify a valid product to match with an alias', errno=103)
        elif res == 104:
            data = xml.error('You cannot create an alias with the same name as a product', errno=104)
        else:
            data = xml.error('Unknown error')
    return Response(data, mimetype='text/xml'), 200 if success else 400

if __name__ == '__main__':
    app = Flask(__name__, instance_relative_config=True)
    app.register_blueprint(bp)
    app.run(host='0.0.0.0', port=5000)
    