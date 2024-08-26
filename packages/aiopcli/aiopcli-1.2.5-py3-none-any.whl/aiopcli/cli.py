from pathlib import Path
import logging
import os
import sys

import click

from aiopcli import client
from aiopcli import settings
from aiopcli import utils
from aiopcli.commands import image
from aiopcli.commands import servable
from aiopcli.commands import env


def _set_log_level():
    import re

    idx = 1
    level = 0
    while idx < len(sys.argv):
        if re.fullmatch('-v+', sys.argv[idx]):
            level += len(sys.argv[idx]) - 1
            del sys.argv[idx]
        elif sys.argv[idx] == "--verbose":
            level += 1
            del sys.argv[idx]
        else:
            idx += 1
    switch_level = {0: "WARN", 1: "INFO"}.get(level, "DEBUG")
    logging.basicConfig(level=os.getenv("LOG_LEVEL", switch_level), stream=sys.stderr)
    return level

verbosity = _set_log_level()


@click.group('aiopcli')
@click.option('-p', '--profile')
@click.option('-H', '--host')
@click.option('-k', '--apikey')
@click.option('-t', '--timeout', type=int, default=300, help='Timeout for client in context.')
@click.pass_context
def cli(ctx, profile, host, apikey, timeout):
    log_level = {0: None, 1: 'INFO'}.get(verbosity, 'DEBUG')
    config, config_path, config_file = settings.load_config(
        profile, host, apikey, log_level=log_level)
    if not config.apikey:
        logging.error("API key must be set")
        exit(1)
    ctx.obj = client.Context(
        client=client.make_client(
            host=config.host, apikey=config.apikey, timeout=timeout),
        config=config, config_path=config_path, config_file=config_file,
    )


@cli.result_callback()
def process_result(status_code, **_):
    sys.exit(status_code)


# New-style commands are loaded as plugins from the `commands` directory
def _register_commands():
    import importlib

    for path in (Path(__file__).parent / "commands").glob("*.py"):
        logging.debug("Importing command %s", path.stem)
        module = importlib.import_module(f".{path.stem}", "aiopcli.commands")
        cli.add_command(module.cli, name=path.stem)

_register_commands()


#
# Old-style commands
#

# aiopcli add server
@cli.group
def add():
    pass

add.add_command(servable.create, name="server")

# aiopcli create | update | delete | status
cli.add_command(env.list)
cli.add_command(env.create)
cli.add_command(env.update)
cli.add_command(env.delete)
cli.add_command(env.get, name="status")

# aiopcli push
cli.add_command(image.push)


@cli.command
@click.argument('env')
@click.option('-e', '--endpoint')
@click.option('-F', '--form', 'fields', multiple=True)
@click.option('-d', '--data')
@click.pass_obj
def predict(ctx, env, endpoint, fields, data):
    env_ = ctx.get_env(env)
    if not env_:
        raise ValueError(f"No such env: '{env}'")
    path = f'/api/v1/env/{env_.id}/predict'
    if endpoint:
        path = client.url_join(path, endpoint)
    with utils.prepare_fields(fields, data) as (files, data):
        logging.debug(f"POST {path} {files=} {data=}")
        response = ctx.client.post(path, files=files, data=data)
    utils.handle_response(response)


@cli.command('tag')
@click.argument('env_id')
@click.argument('tag')
@click.pass_obj
def tag_env(ctx, *, env_id, tag):
    env_ = ctx.get_env(tag)
    if env_:
        if env_id == env_.id:
            logging.info("Nothing changed.")
            return 0
        else:
            logging.warning("Tag already exists, removing.")
            env_.tag = None
    env_ = ctx.get_env(env_id)
    if env_:
        env_.tag = tag
        logging.info(f"Tagged known env {env_id} as '{tag}'")
    else:
        response = ctx.client.get(f'/api/v1/env/{env_id}/status')
        if response.status_code == 403:
            raise ValueError("No such env exists")
        ctx.add_env(env_id=env_id, tag=tag)
        logging.info(f"Tagged new env {env_id} as '{tag}'")
    return ctx.write_config()


@cli.command
@click.pass_obj
def tags(ctx):
    envs = ctx.get_envs()
    if envs:
        for env_ in envs:
            if env_.tag:
                print(f"{env_.id:5d} <- {env_.tag}", file=sys.stderr)
            else:
                print(f"{env_.id}", file=sys.stderr)


if __name__ == "__main__":
    cli()
