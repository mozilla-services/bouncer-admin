#!/usr/bin/env python3
import os, click, requests
import xml.dom.minidom


@click.group()
@click.option(
    "--host", envvar="NAZGUL_PATH", default="http://localhost:8000", show_default=True
)
@click.option("--username", envvar="NAZGUL_USER", default="admin", show_default=True)
@click.option("--password", envvar="NAZGUL_PASS", default="admin", show_default=True)
@click.pass_context
def main(ctx, **kwargs):
    ctx.obj = dict(**kwargs)
    pass


def cli_out(data):
    try:
        dom = xml.dom.minidom.parseString(data)
        pretty_xml = dom.toprettyxml()
        print(pretty_xml)
    except:
        print(data)


@main.command()
@click.pass_obj
def mirror_list(ctx):
    r = requests.get(ctx["host"] + "/api/mirror_list/")
    cli_out(r.text)


@main.command()
@click.pass_obj
@click.argument("product")
@click.option(
    "--fuzzy/--no-fuzzy",
    "fuzzy",
    show_default=True,
    help="True = find similar product names, False = exact match of product name",
)
def location_show(ctx, **kwargs):
    r = requests.get(ctx["host"] + "/api/location_show/", params=dict(**kwargs))
    cli_out(r.text)


@main.command()
@click.pass_obj
@click.argument("product")
@click.argument("os")
@click.argument("path")
def location_add(ctx, **kwargs):
    r = requests.post(
        ctx["host"] + "/api/location_add/",
        data=dict(**kwargs),
        auth=requests.auth.HTTPBasicAuth(ctx["username"], ctx["password"]),
    )
    cli_out(r.text)


@main.command()
@click.pass_obj
@click.argument("product")
@click.argument("os")
@click.argument("path")
def location_modify(ctx, **kwargs):
    r = requests.post(
        ctx["host"] + "/api/location_modify/",
        data=dict(**kwargs),
        auth=requests.auth.HTTPBasicAuth(ctx["username"], ctx["password"]),
    )
    cli_out(r.text)


@main.command()
@click.pass_obj
@click.argument("location_id")
def location_delete(ctx, **kwargs):
    r = requests.post(
        ctx["host"] + "/api/location_delete/",
        data=dict(**kwargs),
        auth=requests.auth.HTTPBasicAuth(ctx["username"], ctx["password"]),
    )
    cli_out(r.text)


@main.command()
@click.pass_obj
@click.argument("product")
@click.option(
    "--fuzzy/--no-fuzzy",
    "fuzzy",
    show_default=True,
    help="True = find similar product names, False = exact match of product name",
)
def product_show(ctx, **kwargs):
    r = requests.get(ctx["host"] + "/api/product_show/", params=dict(**kwargs))
    cli_out(r.text)


@main.command()
@click.pass_obj
@click.argument("product")
@click.argument("languages")
@click.argument("ssl_only")
def product_add(ctx, **kwargs):
    kwargs["languages"] = kwargs["languages"].split(",")
    r = requests.post(
        ctx["host"] + "/api/product_add/",
        data=dict(**kwargs),
        auth=requests.auth.HTTPBasicAuth(ctx["username"], ctx["password"]),
    )
    cli_out(r.text)


@main.command()
@click.pass_obj
@click.option(
    "-pid", "--product_id", default=None, help="id of product to add/delete/update/show"
)
@click.option(
    "-p", "--product", default=None, help="name of product to add/delete/update/show"
)
def product_delete(ctx, **kwargs):
    r = requests.post(
        ctx["host"] + "/api/product_delete/",
        data=dict(**kwargs),
        auth=requests.auth.HTTPBasicAuth(ctx["username"], ctx["password"]),
    )
    cli_out(r.text)


@main.command()
@click.pass_obj
@click.argument("product")
@click.argument("languages")
def product_language_add(ctx, **kwargs):
    kwargs["languages"] = kwargs["languages"].split(",")
    r = requests.post(
        ctx["host"] + "/api/product_language_add/",
        data=dict(**kwargs),
        auth=requests.auth.HTTPBasicAuth(ctx["username"], ctx["password"]),
    )
    cli_out(r.text)


@main.command()
@click.pass_obj
@click.argument("product")
@click.argument("languages")
def product_language_delete(ctx, **kwargs):
    if kwargs["languages"] != "*":
        kwargs["languages"] = kwargs["languages"].split(",")
    r = requests.post(
        ctx["host"] + "/api/product_language_delete/",
        data=dict(**kwargs),
        auth=requests.auth.HTTPBasicAuth(ctx["username"], ctx["password"]),
    )
    cli_out(r.text)


@main.command()
@click.pass_obj
@click.argument("product")
@click.argument("os")
@click.option(
    "--fuzzy/--no-fuzzy",
    "fuzzy",
    show_default=True,
    help="True = find similar product names, False = exact match of product name",
)
def uptake(ctx, **kwargs):
    r = requests.get(ctx["host"] + "/api/uptake/", params=dict(**kwargs))
    cli_out(r.text)


@main.command()
@click.pass_obj
@click.argument("alias")
@click.argument("related_product")
def create_update_alias(ctx, **kwargs):
    r = requests.post(
        ctx["host"] + "/api/create_update_alias/",
        data=dict(**kwargs),
        auth=requests.auth.HTTPBasicAuth(ctx["username"], ctx["password"]),
    )
    cli_out(r.text)


if __name__ == "__main__":
    main()
