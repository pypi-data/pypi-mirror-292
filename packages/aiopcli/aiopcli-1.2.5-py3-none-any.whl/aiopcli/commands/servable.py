import logging
import shutil
import subprocess as sp
import sys

import click

from aiopcli import artifacts
from aiopcli import client
from aiopcli import custom_image
from aiopcli import utils


def _parse_server(s):
    if utils.is_tar_gzip_file(s) or utils.is_image_id(s):
        pass
    else:
        raise ValueError(f'Custom image {s} must be an image id or a file of type .tgz or .tar.gz')
    return s


@click.group("servable")
def cli():
    pass


@click.command
@click.option('-n', '--name', required=True)
@click.option('-d', '--description')
@click.option('--api-server', 'apiServer', type=_parse_server, required=True,
              help='apiserver image file path or imageId')
@click.option('--inference-server', 'inferenceServer', type=_parse_server, default=None,
              help='inferenceserver image file path or imageId')
@click.option('-p', '--api-port', 'port', type=int, default=8080)
@click.option('-m', '--metrics-port', 'metricsPort', type=int, default=None)
@click.option('-s', '--shared-memory-requirement', 'sharedMemoryRequirement', default='0m')
@click.option('-t', '--inference-type', 'inferenceType',
              type=click.Choice(['gpu', 'cpu', 'auto']), default='auto')
@click.option('-i', '--inference-server-type', 'inferenceServerType',
              type=click.Choice(['tritonserver', 'other']), default='tritonserver')
@click.option('-l', '--liveness-endpoint', 'liveness', default=None)
@click.option('-r', '--readiness-endpoint', 'readiness', default=None)
@click.option(
    '-t', '--timeout', type=int, default=1800, help='Timeout for waiting for artifact status.')
@click.option('-f', '--force', is_flag=True)
@click.pass_obj
def create(ctx: client.Context, timeout, force, **kwargs):
    if utils.is_tar_gzip_file(api_file := kwargs['apiServer']):
        kwargs['apiServer'] = artifacts.register_artifact(
            ctx, api_file, timeout=timeout, force=force)
    else:
        if not utils.is_image_id(kwargs['apiServer']):
            raise ValueError(
                "api-server must be an image id or a .tgz or .tar.gz file")
        kwargs['apiServerImageId'] = kwargs.pop('apiServer')

    if kwargs['inferenceServer']:
        if utils.is_tar_gzip_file(kwargs['inferenceServer']):
            kwargs['inferenceServer'] = artifacts.register_artifact(
                ctx, kwargs['inferenceServer'], timeout=timeout, force=force)
        else:
            if not utils.is_image_id(kwargs['inferenceServer']):
                raise ValueError(
                    "inference-server must be an image id or a .tgz or .tar.gz file")
            kwargs['inferenceServerImageId'] = kwargs.pop('inferenceServer')

    spec = custom_image.parse(**kwargs)

    # TODO: error handling
    response = ctx.client.post('/isapi/api/v1/servables', json=spec.dict(exclude_none=True))
    return utils.handle_response(response)

cli.add_command(create)


@cli.command
@click.argument("name", required=False)
@click.option("--no-pager", is_flag=True)
@click.pass_obj
def list(ctx: client.Context, name, no_pager):
    status = 0
    if no_pager:
        process, fp = None, sys.stdout
    elif shutil.which("less"):
        process = sp.Popen(["less"], stdin=sp.PIPE, text=True)
        fp = process.stdin
    elif shutil.which("more"):
        process = sp.Popen(["more"], stdin=sp.PIPE, text=True, bufsize=1000)
        fp = process.stdin
    try:
        page_index = 1
        while True:
            params = {"pageIndex": page_index}
            if name:
                params["name"] = name
            response = ctx.client.get('/isapi/api/v1/servables', params=params)
            response.raise_for_status()
            result = response.json()
            for servable in result["records"]:
                print("{servableId}  {name}".format_map(servable), file=fp)
            if result.get("hasNext"):
                page_index += 1
            else:
                break
    except BrokenPipeError:
        # user quit less
        pass
    except Exception as e:
        logging.error(e, exc_info=True)
        status = 1
    finally:
        if process:
            process.stdin.close()
            process.wait()
    return status


@cli.command
@click.argument("servable")
@click.pass_obj
def get(ctx: client.Context, servable):
    response = ctx.client.get(f"/isapi/api/v1/servables/{servable}")
    return utils.handle_response(response)


@cli.command
@click.argument("servable")
@click.argument("label")
@click.pass_obj
def publish(ctx: client.Context, servable, label):
    response = ctx.client.post(
        f"/isapi/api/v1/servables/{servable}/publish",
        params={"label": label},
        json={}
    )
    return utils.handle_response(response)
