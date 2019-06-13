import pytest
import requests
from nazgul import create_app, mysql_model
import os

test_db = os.environ.get('DATABASE_URL', '127.0.0.1')
msm = mysql_model.MySQLModel(host=test_db)
msm._reset_db()

def test_location_show_exact_match(client):
    rv = client.get('/api/location_show?product=Firefox')
    expected = b'<?xml version="1.0" encoding="utf-8"?><locations><product id="1" name="Firefox"><location id="1" os="win64">/firefox/releases/39.0/win64/:lang/Firefox%20Setup%2039.0.exe</location><location id="2" os="osx">/firefox/releases/39.0/mac/:lang/Firefox%2039.0.dmg</location><location id="3" os="win">/firefox/releases/39.0/win32/:lang/Firefox%20Setup%2039.0.exe</location></product></locations>'
    assert expected == rv.data

def test_location_show_exact_no_match(client):
    rv = client.get('/api/location_show?product=NoMatch')
    expected = b'<?xml version="1.0" encoding="utf-8"?>'
    assert expected == rv.data

def test_location_show_fuzzy_match(client):
    rv = client.get('/api/location_show?product=Firefox&fuzzy=True')
    expected = b'<?xml version="1.0" encoding="utf-8"?><locations><product id="1" name="Firefox"><location id="1" os="win64">/firefox/releases/39.0/win64/:lang/Firefox%20Setup%2039.0.exe</location><location id="2" os="osx">/firefox/releases/39.0/mac/:lang/Firefox%2039.0.dmg</location><location id="3" os="win">/firefox/releases/39.0/win32/:lang/Firefox%20Setup%2039.0.exe</location></product><product id="3" name="Firefox-43.0.1-SSL"><location id="7" os="win64">/firefox/releases/43.0.1/win64/:lang/Firefox%20Setup%2043.0.1.exe</location><location id="8" os="osx">/firefox/releases/43.0.1/mac/:lang/Firefox%2043.0.1.dmg</location><location id="9" os="win">/firefox/releases/43.0.1/win32/:lang/Firefox%20Setup%2043.0.1.exe</location></product><product id="2" name="Firefox-SSL"><location id="4" os="win64">/firefox/releases/39.0/win64/:lang/Firefox%20Setup%2039.0.exe</location><location id="5" os="osx">/firefox/releases/39.0/mac/:lang/Firefox%2039.0.dmg</location><location id="6" os="win">/firefox/releases/39.0/win32/:lang/Firefox%20Setup%2039.0.exe</location></product></locations>'
    assert expected == rv.data

def test_location_show_fuzzy_no_match(client):
    rv = client.get('/api/location_show?product=NoMatch&fuzzy=True')
    expected = b'<?xml version="1.0" encoding="utf-8"?>'
    assert expected == rv.data

def test_uptake(client):
    rv = client.get('api/uptake?product=Firefox&os=osx&fuzzy=True')
    expected = b'<?xml version="1.0" encoding="utf-8"?><mirror_uptake><item><product>Firefox</product><os>osx</os><available>2000000</available><total>2000000</total></item><item><product>Firefox-43.0.1-SSL</product><os>osx</os><available>2000000</available><total>2000000</total></item><item><product>Firefox-SSL</product><os>osx</os><available>2000000</available><total>2000000</total></item></mirror_uptake>'
    assert expected == rv.data

def test_mirror_list(client):
    rv = client.get('api/mirror_list')
    expected = b'<?xml version="1.0" encoding="utf-8"?><mirrors><mirror baseurl="http://download-installer.cdn.mozilla.net/pub"/><mirror baseurl="https://download-installer.cdn.mozilla.net/pub"/></mirrors>'
    assert expected == rv.data

def test_location_add_product_not_found(client):
    rv = client.post('api/location_add', data=dict(product='FakeProduct',path='/test_path', os='osx'))
    expected = b'<?xml version="1.0" encoding="utf-8"?><error number="105">FAILED: \'FakeProduct\' does not exist</error>'
    assert expected == rv.data

def test_location_add_os_not_found(client):
    rv = client.post('api/location_add', data=dict(product='Firefox',path='/test_path', os='fake'))
    expected = b'<?xml version="1.0" encoding="utf-8"?><error number="106">FAILED: \'fake\' does not exist</error>'
    assert expected == rv.data

def test_location_add_location_exists(client):
    rv = client.post('api/location_add', data=dict(product='Firefox',path='/test_path', os='osx'))
    expected = b'<?xml version="1.0" encoding="utf-8"?><error number="104">The specified location already exists.</error>'
    assert expected == rv.data

def test_location_add(client):
    rv = client.post('api/location_add', data=dict(product='AaronProduct',path='/test_path', os='win64'))
    location_exits, location_id = msm.location_exists('win64', 'AaronProduct')
    msm._reset_db()
    if location_exits:
        expected1 = b'<?xml version="1.0" encoding="utf-8"?><locations><product id="4556" name="AaronProduct"><location id="'
        expected2 = b'" os="win64">/test_path</location><location id="23194" os="osx">/test</location></product></locations>'
        assert expected1 in rv.data and expected2 in rv.data
    else:
        print('FAILED: test_location_add - Location not inserted into DB')
        assert False

def test_location_delete_location_not_found(client):
    rv = client.post('api/location_delete', data=dict(location_id=0))
    expected = b'<?xml version="1.0" encoding="utf-8"?><error number="102">No location found.</error>'
    assert expected == rv.data

def test_location_delete_location_input_missing(client):
    rv = client.post('api/location_delete', data=dict(not_loc_id='fakeloc'))
    expected = b'<?xml version="1.0" encoding="utf-8"?><error number="101">location_id is required.</error>'
    assert expected == rv.data

def test_location_delete(client):
    rv = client.post('api/location_delete', data=dict(location_id=23194))
    location_exists, location_id = msm.location_exists('osx', 'AaronProduct')
    msm._reset_db()
    if not location_exists:
        expected = b'<?xml version="1.0" encoding="utf-8"?><success>SUCCESS: location has been deleted</success>'
        assert expected == rv.data
    else:
        print('FAILED: test_location_delete - Location not deleted from DB')
        assert False

def test_location_modify_invalid_product(client):
    rv = client.post('api/location_modify', data=dict(product='FakeProduct', os='osx', path='/newpath'))
    expected = b'<?xml version="1.0" encoding="utf-8"?><error number="105">FAILED: \'FakeProduct\' does not exist</error>'
    assert expected == rv.data

def test_location_modify_invalid_os(client):
    rv = client.post('api/location_modify', data=dict(product='Firefox', os='fakeos', path='/newpath'))
    expected = b'<?xml version="1.0" encoding="utf-8"?><error number="106">FAILED: \'fakeos\' does not exist</error>'
    assert expected == rv.data

def test_location_modify_invalid_location(client):
    rv = client.post('api/location_modify', data=dict(product='AaronProduct', os='win', path='/newpath'))
    expected = b'<?xml version="1.0" encoding="utf-8"?><error number="104">FAILED: location \'AaronProduct\' on OS \'win\' does not exist</error>'
    assert expected == rv.data

def test_location_modify(client):
    rv = client.post('api/location_modify', data=dict(product='AaronProduct', os='osx', path='/newpath'))
    expected = b'<?xml version="1.0" encoding="utf-8"?><locations><product id="4556" name="AaronProduct"><location id="23194" os="osx">/newpath</location></product></locations>'
    msm._reset_db()
    assert expected == rv.data

def test_product_show_exact_match(client):
    rv = client.get('/api/product_show?product=Firefox')
    expected = b'<?xml version="1.0" encoding="utf-8"?><products><product id="1" name="Firefox"><language locale="en-GB"/><language locale="en-US"/></product></products>'
    assert expected == rv.data

def test_product_show_exact_no_match(client):
    rv = client.get('/api/product_show?product=NoMatch')
    expected = b'<?xml version="1.0" encoding="utf-8"?><products/>'
    assert expected == rv.data

def test_product_show_fuzzy_match(client):
    rv = client.get('/api/product_show?product=Firefox&fuzzy=True')
    expected = b'<?xml version="1.0" encoding="utf-8"?><products><product id="1" name="Firefox"><language locale="en-GB"/><language locale="en-US"/></product><product id="3" name="Firefox-43.0.1-SSL"><language locale="en-GB"/><language locale="en-US"/></product><product id="2" name="Firefox-SSL"><language locale="en-GB"/><language locale="en-US"/></product></products>'
    assert expected == rv.data

def test_product_show_fuzzy_no_match(client):
    rv = client.get('/api/product_show?product=NoMatch&fuzzy=True')
    expected = b'<?xml version="1.0" encoding="utf-8"?><products/>'
    assert expected == rv.data

def test_product_add_no_match(client):
    rv = client.post('api/product_add', data=dict(product='AaronProduct', ssl_only='osx', languages={'en-GB'}))
    expected = b'<?xml version="1.0" encoding="utf-8"?><error number="104">product already exists.</error>'
    assert expected == rv.data

def test_product_add(client):
    rv = client.post('api/product_add', data={'product': 'Fake', 'ssl_only':'True', 'languages': '%5B%27en-CA%27%2C%27en-US%27%5D'})
    expected = b'<?xml version="1.0" encoding="utf-8"?><products><product id="4563" name="Fake"><language locale="en-CA"/><language locale="en-US"/></product></products>'
    msm._reset_db()
    assert expected == rv.data

def test_product_delete_id(client):
    rv = client.post('api/product_delete', data={'product_id': 4556})
    expected = b'<?xml version="1.0" encoding="utf-8"?><success>SUCCESS: product has been deleted</success>'
    msm._reset_db()
    assert expected == rv.data

def test_product_delete_name_no_match(client):
    rv = client.post('api/product_delete', data={'product': 'Fake'})
    expected = b'<?xml version="1.0" encoding="utf-8"?><error number="102">No product found.</error>'
    assert expected == rv.data

def test_product_delete_name(client):
    rv = client.post('api/product_delete', data={'product': 'AaronProduct'})
    expected = b'<?xml version="1.0" encoding="utf-8"?><success>SUCCESS: product has been deleted</success>'
    msm._reset_db()
    assert expected == rv.data

def test_product_language_add(client):
    rv = client.post('api/product_language_add', data={'product': 'AaronProduct', 'languages': '%5B%27fr-FR%27%2C%20%27es-SP%27%5D'})
    expected = b'<?xml version="1.0" encoding="utf-8"?><products><product id="4556" name="AaronProduct"><language locale="en-CA"/><language locale="en-GB"/><language locale="en-US"/><language locale="es-SP"/><language locale="fr-FR"/></product></products>'
    msm._reset_db()
    assert expected == rv.data

def test_product_language_add_no_match(client):
    rv = client.post('api/product_language_add', data={'product': 'Fake', 'languages': '%5B%27fr-FR%27%2C%20%27es-SP%27%5D'})
    expected = b'<?xml version="1.0" encoding="utf-8"?><error number="102">Product not found.</error>'
    assert expected == rv.data

def test_product_language_delete(client):
    rv = client.post('api/product_language_delete', data={'product': 'AaronProduct', 'languages': '%5B%27en-GB%27%2C%20%27en-US%27%5D'})
    expected = b'<?xml version="1.0" encoding="utf-8"?><success>SUCCESS: language has been deleted</success>'
    msm._reset_db()
    assert expected == rv.data

def test_product_language_delete_star(client):
    rv = client.post('api/product_language_delete', data={'product': 'AaronProduct', 'languages': '%5B%27*%27%5D'})
    expected = b'<?xml version="1.0" encoding="utf-8"?><success>SUCCESS: language has been deleted</success>'
    msm._reset_db()
    assert expected == rv.data

def test_product_language_delete_no_match(client):
    rv = client.post('api/product_language_delete', data={'product': 'Fake', 'languages': '%5B%27fr-FR%27%2C%20%27es-SP%27%5D'})
    expected = b'<?xml version="1.0" encoding="utf-8"?><error number="102">Product not found.</error>'
    assert expected == rv.data

def test_create_update_alias_no_product_match(client):
    rv = client.post('api/create_update_alias', data={'alias': 'aaron-product', 'related_product': 'FakeProduct'})
    expected = b'<?xml version="1.0" encoding="utf-8"?><error number="103">You must specify a valid product to match with an alias</error>'
    assert expected == rv.data

def test_create_update_alias_alias_product_name_collision(client):
    rv = client.post('api/create_update_alias', data={'alias': 'Firefox', 'related_product': 'AaronProduct'})
    expected = b'<?xml version="1.0" encoding="utf-8"?><error number="104">You cannot create an alias with the same name as a product</error>'
    assert expected == rv.data

def test_create_update_alias(client):
    rv = client.post('api/create_update_alias', data={'alias': 'aaron-product', 'related_product': 'AaronProduct'})
    expected = b'<?xml version="1.0" encoding="utf-8"?><success>Created/updated alias aaron-product</success>'
    msm._reset_db()
    assert expected == rv.data

