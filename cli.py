import os, click, base64, urllib3
import xml.dom.minidom

base_url = os.environ.get("NAZGUL_PATH", "http://localhost:5000")
username = os.environ.get("NAZGUL_USER", "admin")
password = os.environ.get("NAZGUL_PASS", "admin")


@click.command()
@click.argument("method")
@click.option(
    "-pid", "--product_id", default=None, help="id of product to add/delete/update/show"
)
@click.option(
    "-p", "--product", default=None, help="name of product to add/delete/update/show"
)
@click.option(
    "-f",
    "--fuzzy",
    default=False,
    is_flag=True,
    help="True = find similar product names, False = exact match of product name",
)
@click.option("-os", "--os", default=None, help="os of related product/location")
@click.option("-path", "--path", default=None, help="path for location")
@click.option(
    "-langs",
    "--languages",
    default=None,
    help="list of languages separated by commas (eg. 'en-US,es-SP,fr-FR' )",
)
@click.option("-ssl", "--ssl_only", default=False, is_flag=True, help="")
@click.option("-l", "--location_id", default=None, help="id of location")
@click.option("-a", "--alias", default=None, help="alias name")
@click.option("-rp", "--related_product", default=None, help="product related to alias")
@click.option(
    "-h", "--help_method", default=False, is_flag=True, help="get usage on given method"
)
def main(
    method,
    product_id,
    product,
    fuzzy,
    os,
    path,
    languages,
    ssl_only,
    location_id,
    alias,
    related_product,
    help_method,
):
    if help_method:
        print(usage(method))
        return
    err = False
    if method == "mirror_list":
        resp = mirror_list()

    elif method == "location_show":
        if not product:
            resp = "ERROR: product name required for location show -- " + usage(method)
            err = True
        else:
            resp = location_show(product, fuzzy)

    elif method == "location_add":
        if not (product and os and path):
            resp = "ERROR: product name required for location add -- " + usage(method)
            err = True
        else:
            resp = location_add(product, os, path)
    elif method == "location_modify":
        if not (product and os and path):
            resp = "ERROR: product name required for location modify -- " + usage(
                method
            )
            err = True
        else:
            resp = location_modify(product, os, path)

    elif method == "location_delete":
        if not location_id:
            resp = "ERROR: location id required for location delete -- " + usage(method)
            err = True
        else:
            resp = location_delete(location_id)

    elif method == "product_show":
        if not product:
            resp = "ERROR: product name required for product show -- " + usage(method)
            err = True
        else:
            resp = product_show(product, fuzzy)

    elif method == "product_add":
        if not (product and languages):
            resp = (
                "ERROR: product name and languages required for product add -- "
                + usage(method)
            )
            err = True
        else:
            resp = product_add(product, languages, ssl_only)

    elif method == "product_delete":
        if not (product or product_id):
            resp = (
                "ERROR: product name or product_id required for product delete -- "
                + usage(method)
            )
            err = True
        else:
            resp = product_delete(product, product_id)

    elif method == "product_language_add":
        if not (product and languages):
            resp = (
                "ERROR: product name and languages required for product language add -- "
                + usage(method)
            )
            err = True
        else:
            resp = product_language_add(product, languages)

    elif method == "product_language_delete":
        if not (product and languages):
            resp = (
                "ERROR: product name and languages required for product language delete -- "
                + usage(method)
            )
            err = True
        else:
            resp = product_language_delete(product, languages)

    elif method == "uptake":
        if not (product and os):
            resp = "ERROR: product name and os required for uptake -- " + usage(method)
            err = True
        else:
            resp = uptake(product, os, fuzzy)

    elif method == "create_update_alias":
        if not (alias and related_product):
            resp = (
                "ERROR: alias and related_product required for create update alias -- "
                + usage(method)
            )
            err = True
        else:
            resp = create_update_alias(alias, related_product)
    if err:
        print(resp)
    else:
        dom = xml.dom.minidom.parseString(resp)
        pretty_xml = dom.toprettyxml()
        print(pretty_xml)


def usage(method):
    if method == "mirror_list":
        return "USAGE: python3 cli.py location_show -p [PRODUCT NAME]"
    elif method == "location_add":
        return "USAGE: python3 cli.py location_add -p [PRODUCT NAME] -os [OS NAME] -path [PATH]"
    elif method == "location_modify":
        return "USAGE: python3 cli.py location_modify -p [PRODUCT NAME] -os [OS NAME] -path [PATH]"
    elif method == "location_delete":
        return "USAGE: python3 cli.py location_delete -l [LOCATION ID]"
    elif method == "product_show":
        return "USAGE: python3 cli.py product_show -p [PRODUCT NAME]"
    elif method == "product_add":
        return "USAGE: python3 cli.py product_add -p [PRODUCT NAME] -langs [COMMA SEPARATED STRING]"
    elif method == "product_delete":
        return "USAGE: python3 cli.py product_delete -p [PRODUCT NAME]"
    elif method == "product_language_add":
        return "USAGE: python3 cli.py product_language_add -p [PRODUCT NAME] -langs [COMMA SEPARATED STRING]"
    elif method == "product_language_delete":
        return "USAGE: python3 cli.py product_language_delete -p [PRODUCT NAME] -langs [COMMA SEPARATED STRING]"
    elif method == "uptake":
        return "USAGE: python3 cli.py uptake -p [PRODUCT NAME] -os [OS NAME]"
    elif method == "create_update_alias":
        return (
            "USAGE: python3 cli.py create_update_alias -a [ALIAS] -rp [RELATED PRODUCT]"
        )


def mirror_list():
    http = urllib3.PoolManager()
    r = http.request("GET", base_url + "/api/mirror_list/")
    return r.data


def location_show(product, fuzzy):
    http = urllib3.PoolManager()
    r = http.request(
        "GET",
        base_url + "/api/location_show/?product=" + product + "&fuzzy=" + str(fuzzy),
    )
    return r.data


def location_add(product, os, path):
    data = str.encode("product=" + product + "&os=" + os + "&path=" + path)
    http = urllib3.PoolManager()
    headers = urllib3.util.make_headers(basic_auth=username + ":" + password)
    headers["Content-Type"] = "application/x-www-form-urlencoded"
    r = http.request(
        "POST", base_url + "/api/location_add/", headers=headers, body=data
    )

    return r.data


def location_modify(product, os, path):
    data = str.encode("product=" + product + "&os=" + os + "&path=" + path)
    http = urllib3.PoolManager()
    headers = urllib3.util.make_headers(basic_auth=username + ":" + password)
    headers["Content-Type"] = "application/x-www-form-urlencoded"
    r = http.request(
        "POST", base_url + "/api/location_modify/", headers=headers, body=data
    )

    return r.data


def location_delete(location_id):
    data = str.encode("location_id=" + location_id)
    http = urllib3.PoolManager()
    headers = urllib3.util.make_headers(basic_auth=username + ":" + password)
    headers["Content-Type"] = "application/x-www-form-urlencoded"
    r = http.request(
        "POST", base_url + "/api/location_delete/", headers=headers, body=data
    )

    return r.data


def product_show(product, fuzzy):
    http = urllib3.PoolManager()
    r = http.request(
        "GET",
        base_url + "/api/product_show/?product=" + product + "&fuzzy=" + str(fuzzy),
    )
    return r.data


def product_add(product, languages, ssl_only):
    langs = languages.split(",")
    data = "product=" + product + "&ssl_only=" + str(ssl_only)
    for lang in langs:
        data += "&languages=" + lang
    data = str.encode(data)
    http = urllib3.PoolManager()
    headers = urllib3.util.make_headers(basic_auth=username + ":" + password)
    headers["Content-Type"] = "application/x-www-form-urlencoded"
    r = http.request("POST", base_url + "/api/product_add/", headers=headers, body=data)

    return r.data


def product_delete(product, product_id):
    if not product:
        data = str.encode("product=" + product)
    else:
        data = str.encode("product_id=" + product_id)
    http = urllib3.PoolManager()
    headers = urllib3.util.make_headers(basic_auth=username + ":" + password)
    headers["Content-Type"] = "application/x-www-form-urlencoded"
    r = http.request(
        "POST", base_url + "/api/product_delete/", headers=headers, body=data
    )

    return r.data


def product_language_add(product, languages):
    langs = languages.split(",")
    data = "product=" + product
    for lang in langs:
        data += "&languages=" + lang
    data = str.encode(data)
    http = urllib3.PoolManager()
    headers = urllib3.util.make_headers(basic_auth=username + ":" + password)
    headers["Content-Type"] = "application/x-www-form-urlencoded"
    r = http.request(
        "POST", base_url + "/api/product_language_add/", headers=headers, body=data
    )

    return r.data


def product_language_delete(product, languages):
    langs = languages.split(",")
    data = "product=" + product
    for lang in langs:
        data += "&languages=" + lang
    data = str.encode(data)
    http = urllib3.PoolManager()
    headers = urllib3.util.make_headers(basic_auth=username + ":" + password)
    headers["Content-Type"] = "application/x-www-form-urlencoded"
    r = http.request(
        "POST", base_url + "/api/product_language_delete/", headers=headers, body=data
    )

    return r.data


def uptake(product, os, fuzzy):
    http = urllib3.PoolManager()
    r = http.request(
        "GET",
        base_url
        + "/api/uptake/?product="
        + product
        + "&os="
        + os
        + "&fuzzy="
        + str(fuzzy),
    )
    return r.data


def create_update_alias(alias, related_product):
    data = str.encode("alias=" + alias + "&related_product=" + related_product)
    http = urllib3.PoolManager()
    headers = urllib3.util.make_headers(basic_auth=username + ":" + password)
    headers["Content-Type"] = "application/x-www-form-urlencoded"
    r = http.request(
        "POST", base_url + "/api/create_update_alias/", headers=headers, body=data
    )

    return r.data


if __name__ == "__main__":
    main()
