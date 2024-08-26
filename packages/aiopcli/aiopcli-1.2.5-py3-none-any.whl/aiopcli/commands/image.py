import logging
import subprocess
import sys
import urllib.parse

import click

from aiopcli import utils


@click.group("image")
def cli():
    pass


@cli.command
@click.argument('image')
@click.pass_obj
def push(ctx, image):
    response = ctx.client.post('/isapi/api/v1/images')
    if response.status_code != 200:
        return utils.handle_response(response)
    image_id = response.json()['imageId']
    logging.info(f'image_id: {image_id}')

    host_url = urllib.parse.urlparse(ctx.host)
    server_name = host_url.netloc.split(':')[0]  # remove port if present
    registry_host = f'registry.{server_name}'
    logging.info(registry_host)

    # docker login
    password = ctx.apikey
    subprocess.run(
        ['docker', 'login', '--username', 'aiop', '--password-stdin', registry_host],
        input=password, check=True, text=True, stdout=sys.stderr
    )

    # tag image
    target_tag = f'{registry_host}/{image_id}:latest'
    subprocess.run(
        ['docker', 'tag', image, target_tag], check=True, stdout=sys.stderr)

    # image push
    subprocess.run(['docker', 'push', target_tag], check=True, stdout=sys.stderr)

    # image delete
    subprocess.run(['docker', 'rmi', target_tag], check=True, stdout=sys.stderr)

    # docker logout
    # subprocess.run(['docker', 'logout', registry_host], check=True)

    return utils.handle_response(response)
