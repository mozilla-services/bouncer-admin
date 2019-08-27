#!/usr/bin/env python3
import os, click, base64, requests, urllib3
import xml.dom.minidom

base_url = os.environ.get("NAZGUL_PATH", "http://localhost:5000")
username = os.environ.get("NAZGUL_USER", "admin")
password = os.environ.get("NAZGUL_PASS", "admin")


@click.group()
@click.option('--host', default=base_url, show_default=True)
@click.option('--username', default=username, show_default=True)
@click.option('--password', default=password, show_default=True)
@click.pass_context
def main(ctx, **kwargs):
    ctx.obj = dict(**kwargs)
    pass

def cli_out(data):
    dom = xml.dom.minidom.parseString(data)
    pretty_xml = dom.toprettyxml()
    print(pretty_xml)

@main.command()
@click.pass_obj
def mirror_list(ctx):
    r = requests.get(ctx['host'] + "/api/mirror_list/")
    cli_out(r.text)
    return r.text

@main.command()
@click.pass_obj
@click.argument("product")
@click.option("-f", "--fuzzy", default=False, is_flag=True, help="True = find similar product names, False = exact match of product name")
def location_show(ctx, **kwargs):
    r = requests.get(ctx['host'] + "/api/location_show/", params=dict(**kwargs))
    cli_out(r.text)
    return r.text

@main.command()
@click.pass_obj
@click.argument("product")
@click.argument("os")
@click.argument("path")
def location_add(ctx, **kwargs):
    r = requests.post(ctx['host'] + '/api/location_add/', data=dict(**kwargs), auth=requests.auth.HTTPBasicAuth(ctx['username'], ctx['password']))
    cli_out(r.text)
    return r.text

@main.command()
@click.pass_obj
@click.argument("product")
@click.argument("os")
@click.argument("path")
def location_modify(ctx, **kwargs):
    r = requests.post(ctx['host'] + '/api/location_modify/', data=dict(**kwargs), auth=requests.auth.HTTPBasicAuth(ctx['username'], ctx['password']))
    cli_out(r.text)
    return r.text

@main.command()
@click.pass_obj
@click.argument("location_id")
def location_delete(ctx, **kwargs):
    r = requests.post(ctx['host'] + '/api/location_delete/', data=dict(**kwargs), auth=requests.auth.HTTPBasicAuth(ctx['username'], ctx['password']))
    cli_out(r.text)
    return r.text

@main.command()
@click.pass_obj
@click.argument("product")
@click.option("-f", "--fuzzy", default=False, is_flag=True, help="True = find similar product names, False = exact match of product name")
def product_show(ctx, **kwargs):
    r = requests.get(ctx['host'] + "/api/product_show/", params=dict(**kwargs))
    cli_out(r.text)
    return r.text

@main.command()
@click.pass_obj
@click.argument("product")
@click.argument("languages")
@click.argument("ssl_only")
def product_add(ctx, **kwargs):
    kwargs['languages'] = kwargs['languages'].split(",")
    r = requests.post(ctx['host'] + '/api/product_add/', data=dict(**kwargs), auth=requests.auth.HTTPBasicAuth(ctx['username'], ctx['password']))
    cli_out(r.text)
    return r.text


@main.command()
@click.pass_obj
@click.option("-pid", "--product_id", default=None, help="id of product to add/delete/update/show")
@click.option("-p", "--product", default=None, help="name of product to add/delete/update/show")
def product_delete(ctx, **kwargs):
    r = requests.post(ctx['host'] + '/api/product_delete/', data=dict(**kwargs), auth=requests.auth.HTTPBasicAuth(ctx['username'], ctx['password']))
    cli_out(r.text)
    return r.text

@main.command()
@click.pass_obj
@click.argument("product")
@click.argument("languages")
def product_language_add(ctx, **kwargs):
    kwargs['languages'] = kwargs['languages'].split(",")
    r = requests.post(ctx['host'] + '/api/product_language_add/', data=dict(**kwargs), auth=requests.auth.HTTPBasicAuth(ctx['username'], ctx['password']))
    cli_out(r.text)
    return r.text

@main.command()
@click.pass_obj
@click.argument("product")
@click.argument("languages",)
def product_language_delete(ctx, **kwargs):
    if kwargs['languages'] != "*":
        kwargs['languages'] = kwargs['languages'].split(",")
    r = requests.post(ctx['host'] + '/api/product_language_delete/', data=dict(**kwargs), auth=requests.auth.HTTPBasicAuth(ctx['username'], ctx['password']))
    cli_out(r.text)
    return r.data

@main.command()
@click.pass_obj
@click.argument("product")
@click.argument("os")
@click.option("-f", "--fuzzy", default=False, is_flag=True, help="True = find similar product names, False = exact match of product name")
def uptake(ctx, **kwargs):
    r = requests.get(ctx['host'] + "/api/uptake/", params=dict(**kwargs))
    cli_out(r.text)
    return r.text

@main.command()
@click.pass_obj
@click.argument("alias")
@click.argument("related_product")
def create_update_alias(ctx, **kwargs):
    r = requests.get(ctx['host'] + "/api/uptake/", params=dict(**kwargs))
    cli_out(r.text)
    return r.text

if __name__ == "__main__":
    main()
