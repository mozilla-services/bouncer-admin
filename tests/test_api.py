import pytest
import requests
from nazgul import create_app, mysql_model
import cli
import os, subprocess

test_db = os.environ.get("DATABASE_URL", "127.0.0.1")
msm = mysql_model.MySQLModel(host=test_db)
msm._reset_db()

test_user = "admin"
test_pass = "test"
os.environ["AUTH_USERS"] = '{"' + test_user + '":"' + test_pass + '"}'


def test_location_show_exact_match(client):
    rv = client.get(
        "/api/location_show/?product=Firefox",
        headers={"Authorization": requests.auth._basic_auth_str(test_user, test_pass)},
    )
    expected = b'<?xml version="1.0" encoding="utf-8"?><locations><product id="1" name="Firefox"><location id="1" os="win64">/firefox/releases/39.0/win64/:lang/Firefox%20Setup%2039.0.exe</location><location id="2" os="osx">/firefox/releases/39.0/mac/:lang/Firefox%2039.0.dmg</location><location id="3" os="win">/firefox/releases/39.0/win32/:lang/Firefox%20Setup%2039.0.exe</location></product></locations>'
    assert expected == rv.data


def test_location_show_exact_no_match(client):
    rv = client.get(
        "/api/location_show/?product=NoMatch",
        headers={"Authorization": requests.auth._basic_auth_str(test_user, test_pass)},
    )
    expected = b'<?xml version="1.0" encoding="utf-8"?>'
    assert expected == rv.data


def test_location_show_fuzzy_match(client):
    rv = client.get(
        "/api/location_show/?product=Firefox&fuzzy=True",
        headers={"Authorization": requests.auth._basic_auth_str(test_user, test_pass)},
    )
    expected = b'<?xml version="1.0" encoding="utf-8"?><locations><product id="1" name="Firefox"><location id="1" os="win64">/firefox/releases/39.0/win64/:lang/Firefox%20Setup%2039.0.exe</location><location id="2" os="osx">/firefox/releases/39.0/mac/:lang/Firefox%2039.0.dmg</location><location id="3" os="win">/firefox/releases/39.0/win32/:lang/Firefox%20Setup%2039.0.exe</location></product><product id="3" name="Firefox-43.0.1-SSL"><location id="7" os="win64">/firefox/releases/43.0.1/win64/:lang/Firefox%20Setup%2043.0.1.exe</location><location id="8" os="osx">/firefox/releases/43.0.1/mac/:lang/Firefox%2043.0.1.dmg</location><location id="9" os="win">/firefox/releases/43.0.1/win32/:lang/Firefox%20Setup%2043.0.1.exe</location></product><product id="2" name="Firefox-SSL"><location id="4" os="win64">/firefox/releases/39.0/win64/:lang/Firefox%20Setup%2039.0.exe</location><location id="5" os="osx">/firefox/releases/39.0/mac/:lang/Firefox%2039.0.dmg</location><location id="6" os="win">/firefox/releases/39.0/win32/:lang/Firefox%20Setup%2039.0.exe</location></product></locations>'
    assert expected == rv.data


def test_location_show_fuzzy_no_match(client):
    rv = client.get(
        "/api/location_show/?product=NoMatch&fuzzy=True",
        headers={"Authorization": requests.auth._basic_auth_str(test_user, test_pass)},
    )
    expected = b'<?xml version="1.0" encoding="utf-8"?>'
    assert expected == rv.data


def test_uptake(client):
    rv = client.get(
        "api/uptake/?product=Firefox&os=osx&fuzzy=True",
        headers={"Authorization": requests.auth._basic_auth_str(test_user, test_pass)},
    )
    expected = b'<?xml version="1.0" encoding="utf-8"?><mirror_uptake><item><product>Firefox</product><os>osx</os><available>2000000</available><total>2000000</total></item><item><product>Firefox-43.0.1-SSL</product><os>osx</os><available>2000000</available><total>2000000</total></item><item><product>Firefox-SSL</product><os>osx</os><available>2000000</available><total>2000000</total></item></mirror_uptake>'
    assert expected == rv.data


def test_mirror_list(client):
    rv = client.get(
        "api/mirror_list/",
        headers={"Authorization": requests.auth._basic_auth_str(test_user, test_pass)},
    )
    expected = b'<?xml version="1.0" encoding="utf-8"?><mirrors><mirror baseurl="http://download-installer.cdn.mozilla.net/pub"/><mirror baseurl="https://download-installer.cdn.mozilla.net/pub"/></mirrors>'
    assert expected == rv.data


def test_location_add_product_not_found(client):
    rv = client.post(
        "api/location_add/",
        data=dict(product="FakeProduct", path="/test_path", os="osx"),
        headers={"Authorization": requests.auth._basic_auth_str(test_user, test_pass)},
    )
    expected = b'<?xml version="1.0" encoding="utf-8"?><error number="105">FAILED: \'FakeProduct\' does not exist</error>'
    assert expected == rv.data


def test_location_add_os_not_found(client):
    rv = client.post(
        "api/location_add/",
        data=dict(product="Firefox", path="/test_path", os="fake"),
        headers={"Authorization": requests.auth._basic_auth_str(test_user, test_pass)},
    )
    expected = b'<?xml version="1.0" encoding="utf-8"?><error number="106">FAILED: \'fake\' does not exist</error>'
    assert expected == rv.data


def test_location_add_location_exists(client):
    rv = client.post(
        "api/location_add/",
        data=dict(product="Firefox", path="/test_path", os="osx"),
        headers={"Authorization": requests.auth._basic_auth_str(test_user, test_pass)},
    )
    expected = b'<?xml version="1.0" encoding="utf-8"?><error number="104">The specified location already exists.</error>'
    assert expected == rv.data


def test_location_add(client):
    rv = client.post(
        "api/location_add/",
        data=dict(product="AaronProduct", path="/test_path", os="win64"),
        headers={"Authorization": requests.auth._basic_auth_str(test_user, test_pass)},
    )
    location_exits, location_id = msm.location_exists("win64", "AaronProduct")
    msm._reset_db()
    if location_exits:
        expected1 = b'<?xml version="1.0" encoding="utf-8"?><locations><product id="4556" name="AaronProduct"><location id="'
        expected2 = b'" os="win64">/test_path</location><location id="23194" os="osx">/test</location></product></locations>'
        assert expected1 in rv.data and expected2 in rv.data
    else:
        print("FAILED: test_location_add - Location not inserted into DB")
        assert False


def test_location_delete_location_not_found(client):
    rv = client.post(
        "api/location_delete/",
        data=dict(location_id=0),
        headers={"Authorization": requests.auth._basic_auth_str(test_user, test_pass)},
    )
    expected = b'<?xml version="1.0" encoding="utf-8"?><error number="102">No location found.</error>'
    assert expected == rv.data


def test_location_delete_location_input_missing(client):
    rv = client.post(
        "api/location_delete/",
        data=dict(not_loc_id="fakeloc"),
        headers={"Authorization": requests.auth._basic_auth_str(test_user, test_pass)},
    )
    expected = b'<?xml version="1.0" encoding="utf-8"?><error number="101">location_id is required.</error>'
    assert expected == rv.data


def test_location_delete(client):
    rv = client.post(
        "api/location_delete/",
        data=dict(location_id=23194),
        headers={"Authorization": requests.auth._basic_auth_str(test_user, test_pass)},
    )
    location_exists, location_id = msm.location_exists("osx", "AaronProduct")
    msm._reset_db()
    if not location_exists:
        expected = b'<?xml version="1.0" encoding="utf-8"?><success>SUCCESS: location has been deleted</success>'
        assert expected == rv.data
    else:
        print("FAILED: test_location_delete - Location not deleted from DB")
        assert False


def test_location_modify_invalid_product(client):
    rv = client.post(
        "api/location_modify/",
        data=dict(product="FakeProduct", os="osx", path="/newpath"),
        headers={"Authorization": requests.auth._basic_auth_str(test_user, test_pass)},
    )
    expected = b'<?xml version="1.0" encoding="utf-8"?><error number="105">FAILED: \'FakeProduct\' does not exist</error>'
    assert expected == rv.data


def test_location_modify_invalid_os(client):
    rv = client.post(
        "api/location_modify/",
        data=dict(product="Firefox", os="fakeos", path="/newpath"),
        headers={"Authorization": requests.auth._basic_auth_str(test_user, test_pass)},
    )
    expected = b'<?xml version="1.0" encoding="utf-8"?><error number="106">FAILED: \'fakeos\' does not exist</error>'
    assert expected == rv.data


def test_location_modify_invalid_location(client):
    rv = client.post(
        "api/location_modify/",
        data=dict(product="AaronProduct", os="win", path="/newpath"),
        headers={"Authorization": requests.auth._basic_auth_str(test_user, test_pass)},
    )
    expected = b'<?xml version="1.0" encoding="utf-8"?><error number="104">FAILED: location \'AaronProduct\' on OS \'win\' does not exist</error>'
    assert expected == rv.data


def test_location_modify(client):
    rv = client.post(
        "api/location_modify/",
        data=dict(product="AaronProduct", os="osx", path="/newpath"),
        headers={"Authorization": requests.auth._basic_auth_str(test_user, test_pass)},
    )
    expected = b'<?xml version="1.0" encoding="utf-8"?><locations><product id="4556" name="AaronProduct"><location id="23194" os="osx">/newpath</location></product></locations>'
    msm._reset_db()
    assert expected == rv.data


def test_product_show_exact_match(client):
    rv = client.get(
        "/api/product_show/?product=Firefox",
        headers={"Authorization": requests.auth._basic_auth_str(test_user, test_pass)},
    )
    expected = b'<?xml version="1.0" encoding="utf-8"?><products><product id="1" name="Firefox"><language locale="en-GB"/><language locale="en-US"/></product></products>'
    assert expected == rv.data


def test_product_show_exact_no_match(client):
    rv = client.get(
        "/api/product_show/?product=NoMatch",
        headers={"Authorization": requests.auth._basic_auth_str(test_user, test_pass)},
    )
    expected = b'<?xml version="1.0" encoding="utf-8"?><products/>'
    assert expected == rv.data


def test_product_show_fuzzy_match(client):
    rv = client.get(
        "/api/product_show/?product=Firefox&fuzzy=True",
        headers={"Authorization": requests.auth._basic_auth_str(test_user, test_pass)},
    )
    expected = b'<?xml version="1.0" encoding="utf-8"?><products><product id="1" name="Firefox"><language locale="en-GB"/><language locale="en-US"/></product><product id="3" name="Firefox-43.0.1-SSL"><language locale="en-GB"/><language locale="en-US"/></product><product id="2" name="Firefox-SSL"><language locale="en-GB"/><language locale="en-US"/></product></products>'
    assert expected == rv.data


def test_product_show_fuzzy_no_match(client):
    rv = client.get(
        "/api/product_show/?product=NoMatch&fuzzy=True",
        headers={"Authorization": requests.auth._basic_auth_str(test_user, test_pass)},
    )
    expected = b'<?xml version="1.0" encoding="utf-8"?><products/>'
    assert expected == rv.data


def test_product_add_no_match(client):
    rv = client.post(
        "api/product_add/",
        data=dict(product="AaronProduct", ssl_only="osx", languages={"en-GB"}),
        headers={"Authorization": requests.auth._basic_auth_str(test_user, test_pass)},
    )
    expected = b'<?xml version="1.0" encoding="utf-8"?><error number="104">product already exists.</error>'
    assert expected == rv.data


def test_product_add(client):
    rv = client.post(
        "api/product_add/",
        data={"product": "Fake", "ssl_only": "True", "languages": ["en-CA", "en-US"]},
        headers={"Authorization": requests.auth._basic_auth_str(test_user, test_pass)},
    )
    expected = b'<?xml version="1.0" encoding="utf-8"?><products><product id="4563" name="Fake"><language locale="en-CA"/><language locale="en-US"/></product></products>'
    msm._reset_db()
    assert expected == rv.data


def test_product_delete_id(client):
    rv = client.post(
        "api/product_delete/",
        data={"product_id": 4556},
        headers={"Authorization": requests.auth._basic_auth_str(test_user, test_pass)},
    )
    expected = b'<?xml version="1.0" encoding="utf-8"?><success>SUCCESS: product has been deleted</success>'
    msm._reset_db()
    assert expected == rv.data


def test_product_delete_name_no_match(client):
    rv = client.post(
        "api/product_delete/",
        data={"product": "Fake"},
        headers={"Authorization": requests.auth._basic_auth_str(test_user, test_pass)},
    )
    expected = b'<?xml version="1.0" encoding="utf-8"?><error number="102">No product found.</error>'
    assert expected == rv.data


def test_product_delete_name(client):
    rv = client.post(
        "api/product_delete/",
        data={"product": "AaronProduct"},
        headers={"Authorization": requests.auth._basic_auth_str(test_user, test_pass)},
    )
    expected = b'<?xml version="1.0" encoding="utf-8"?><success>SUCCESS: product has been deleted</success>'
    msm._reset_db()
    assert expected == rv.data


def test_product_language_add(client):
    rv = client.post(
        "api/product_language_add/",
        data={"product": "AaronProduct", "languages": ["fr-FR", "es-SP"]},
        headers={"Authorization": requests.auth._basic_auth_str(test_user, test_pass)},
    )
    expected = b'<?xml version="1.0" encoding="utf-8"?><products><product id="4556" name="AaronProduct"><language locale="en-CA"/><language locale="en-GB"/><language locale="en-US"/><language locale="es-SP"/><language locale="fr-FR"/></product></products>'
    msm._reset_db()
    assert expected == rv.data


def test_product_language_add_no_match(client):
    rv = client.post(
        "api/product_language_add/",
        data={"product": "Fake", "languages": ["fr-FR", "es-SP"]},
        headers={"Authorization": requests.auth._basic_auth_str(test_user, test_pass)},
    )
    expected = b'<?xml version="1.0" encoding="utf-8"?><error number="102">Product not found.</error>'
    assert expected == rv.data


def test_product_language_delete(client):
    rv = client.post(
        "api/product_language_delete/",
        data={"product": "AaronProduct", "languages": ["en-GB", "en-US"]},
        headers={"Authorization": requests.auth._basic_auth_str(test_user, test_pass)},
    )
    expected = b'<?xml version="1.0" encoding="utf-8"?><success>SUCCESS: language has been deleted</success>'
    msm._reset_db()
    assert expected == rv.data


def test_product_language_delete_star(client):
    rv = client.post(
        "api/product_language_delete/",
        data={"product": "AaronProduct", "languages": ["*"]},
        headers={"Authorization": requests.auth._basic_auth_str(test_user, test_pass)},
    )
    expected = b'<?xml version="1.0" encoding="utf-8"?><success>SUCCESS: language has been deleted</success>'
    msm._reset_db()
    assert expected == rv.data


def test_product_language_delete_no_match(client):
    rv = client.post(
        "api/product_language_delete/",
        data={"product": "Fake", "languages": ["fr-FR", "es-SP"]},
        headers={"Authorization": requests.auth._basic_auth_str(test_user, test_pass)},
    )
    expected = b'<?xml version="1.0" encoding="utf-8"?><error number="102">Product not found.</error>'
    assert expected == rv.data


def test_create_update_alias_no_product_match(client):
    rv = client.post(
        "api/create_update_alias/",
        data={"alias": "aaron-product", "related_product": "FakeProduct"},
        headers={"Authorization": requests.auth._basic_auth_str(test_user, test_pass)},
    )
    expected = b'<?xml version="1.0" encoding="utf-8"?><error number="103">You must specify a valid product to match with an alias</error>'
    assert expected == rv.data


def test_create_update_alias_alias_product_name_collision(client):
    rv = client.post(
        "api/create_update_alias/",
        data={"alias": "Firefox", "related_product": "AaronProduct"},
        headers={"Authorization": requests.auth._basic_auth_str(test_user, test_pass)},
    )
    expected = b'<?xml version="1.0" encoding="utf-8"?><error number="104">You cannot create an alias with the same name as a product</error>'
    assert expected == rv.data


def test_create_update_alias(client):
    rv = client.post(
        "api/create_update_alias/",
        data={"alias": "aaron-product", "related_product": "AaronProduct"},
        headers={"Authorization": requests.auth._basic_auth_str(test_user, test_pass)},
    )
    expected = b'<?xml version="1.0" encoding="utf-8"?><success>Created/updated alias aaron-product</success>'
    msm._reset_db()
    assert expected == rv.data


def test_content_length_limit(client):
    f = open("tests/dummytestdata.txt", "r")
    dummydata = f.read()
    rv = client.post(
        "api/location_add/",
        data=dict(
            product="FakeProduct", path="/test_path", os="osx", testfile=dummydata
        ),
        headers={"Authorization": requests.auth._basic_auth_str(test_user, test_pass)},
    )
    expected = b'<?xml version="1.0" encoding="utf-8"?><error number="101">POST request length exceeded 500KB</error>'
    assert expected == rv.data

def test_cli_location_show(client):
    subprocess.run(["./cli.py", "location-show", "Firefox"])
    assert True

def test_cli_location_add(client):
    subprocess.run(["./cli.py", "location-add", "AaronProduct", "osx", "/test_path"])
    assert True

def test_cli_location_modify(client):
    subprocess.run(["./cli.py", "location-modify", "AaronProduct", "osx", "/test_path"])
    assert True

def test_cli_location_delete(client):
    subprocess.run(["./cli.py", "location-delete", "23194"])
    assert True

def test_cli_product_show(client):
    subprocess.run(["./cli.py", "product-show", "Firefox"])
    assert True

def test_cli_product_add(client):
    subprocess.run(["./cli.py", "product-add", "Test123", "en-GB,en-US", "True"])
    assert True

def test_cli_product_delete(client):
    subprocess.run(["./cli.py", "product-delete", "AaronProduct"])
    assert True

def test_cli_product_language_add(client):
    subprocess.run(["./cli.py", "product-languag-add", "Test123", "en-GB,en-US"])
    assert True

def test_cli_product_language_delete(client):
    subprocess.run(["./cli.py", "product-language-delete", "AaronProduct", "*"])
    assert True

def test_cli_uptake(client):
    subprocess.run(["./cli.py", "uptake", "AaronProduct", "osx"])
    assert True

def test_cli_create_update_alias(client):
    subprocess.run(["./cli.py", "create-update-alias", "aaronproduct", "AaronProduct"])
    assert True

def test_cli_mirror_list(client):
    subprocess.run(["./cli.py", "mirror-list"])
    assert True


def test_cli_help(client):
    subprocess.run(["./cli.py", "location-add", "--help"])
    subprocess.run(["./cli.py", "location-modify", "-help"])
    subprocess.run(["./cli.py", "location-delete", "-help"])
    subprocess.run(["./cli.py", "location-show", "-help"])
    subprocess.run(["./cli.py", "product-show", "-help"])
    subprocess.run(["./cli.py", "product-add", "-help"])
    subprocess.run(["./cli.py", "product-delete", "-help"])
    subprocess.run(["./cli.py", "product-language_add", "-help"])
    subprocess.run(["./cli.py", "product-language_delete", "-help"])
    subprocess.run(["./cli.py", "uptake", "-help"])
    subprocess.run(["./cli.py", "create-update-alias", "-help"])
    subprocess.run(["./cli.py", "mirror-list", "-help"])

    assert True
