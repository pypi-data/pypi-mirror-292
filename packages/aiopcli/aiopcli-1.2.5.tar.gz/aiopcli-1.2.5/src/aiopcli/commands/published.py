from typing import Optional

import click

from aiopcli import client
from aiopcli import utils


@click.group("published")
def cli():
    pass

@cli.command
@click.argument("name")
@click.option("--version")
@click.pass_obj
def get(ctx: client.Context, name: str, version: Optional[str]):
    response = ctx.client.get(
        f"/isapi/api/v1/published/servables/{name}",
        params={"version": version} if version else None,
    )
    return utils.handle_response(response)
