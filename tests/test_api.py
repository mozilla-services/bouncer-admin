import pytest
import requests
from nazgul import create_app

def test_uptake(client):
    """Dummy test"""

    rv = client.get('/api/uptake')
    assert b':(' in rv.data

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


