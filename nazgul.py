from flask import Flask, render_template, request
from flask_mysqldb import MySQL
from mysql_model import MySQLModel

app = Flask(__name__)

msm = MySQLModel(app)

@app.route('/', methods=['GET', 'POST'])
def index():
    return msm.index()

@app.route('/location_show', methods=['GET'])
def location_show():
    product = request.args.get('product')
    fuzzy = request.args.get('fuzzy') == 'True'
    return msm.location_show(product, fuzzy)

@app.route('/location_add', methods=['POST'])
def location_add():
    data = request.get_json()
    product = data.get('product')
    os = data.get('os')
    path = data.get('path')
    return msm.location_add(product, os, path)

@app.route('/location_modify', methods=['POST'])
def location_modify():
    data = request.get_json()
    product = data.get('product')
    os = data.get('os')
    path = data.get('path')
    return msm.location_modify(product, os, path)

@app.route('/location_delete', methods=['POST'])
def location_delete():
    data = request.get_json()
    product = data.get('product')
    os = data.get('os')
    return msm.location_delete(product, os)

@app.route('/product_show', methods=['GET'])
def product_show():
    return 'product_show'

@app.route('/product_add', methods=['GET'])
def product_add():
    return 'product_add'

@app.route('/product_delete', methods=['GET'])
def product_delete():
    return 'product_delete'

@app.route('/product_language_add', methods=['GET'])
def product_language_add():
    return 'product_language_add'

@app.route('/product_language_delete', methods=['GET'])
def product_language_delete():
    return 'product_language_delete'

@app.route('/mirror_list', methods=['GET'])
def mirror_list():
    return 'mirror_list'


if __name__ == "__main__":
    app.run()