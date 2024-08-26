from typing import Optional
import click

from aiopcli import client
from aiopcli import utils
from aiopcli.commands import env as env_commands


@click.command("deploy")
@click.argument("label")
@click.option("--create", is_flag=True)
@click.option("--env")
@click.option("--version", type=int)
#@click.option('-p', '--server-plan', required=True, type=click.Choice(PLAN_TYPES))
@click.option('-p', '--server-plan', type=str)
@click.option('-c', '--capacity', type=int, default=1)
@click.option('--auto-scale', type=click.Choice(['true', 'false']))
@click.option('-l', '--auto-scaling-limit', type=int)
@click.option('-t', '--tag')
@click.pass_obj
def cli(
    ctx: client.Context, label: str, version: Optional[int], 
    env: Optional[str], create: bool, server_plan, capacity, auto_scale, auto_scaling_limit, tag
):
    if not create and not env:
        raise click.UsageError("must specify --create or --env=<env-id>")
    if not env and auto_scale is not None and auto_scaling_limit is None:
        raise click.BadParameter("auto-scaling-limit was not specified", param="auto-scaling-limit")
    if create and not server_plan:
        raise click.BadParameter("--server-plan required on new deployments")

    response = ctx.client.get(
        f"/isapi/api/v1/published/servables/{label}",
        params={"version": version} if version else None,
    )
    if response.status_code >= 300:
        return utils.handle_response(response)
        
    if env:
        response = env_commands.update_env(
            ctx, env=env, servable=response.json(), server_plan=server_plan, capacity=capacity,
            auto_scale=auto_scale, auto_scaling_limit=auto_scaling_limit,
        )
    else:
        response = env_commands.create_env(
            ctx, servable=response.json(), server_plan=server_plan, 
            capacity=capacity, auto_scaling_limit=auto_scaling_limit, tag=tag,
        )

    return utils.handle_response(response)
