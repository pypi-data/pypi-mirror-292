import logging
import re

import click

from aiopcli.utils import handle_response

# FIXME: currently disabled
PLAN_TYPES = [
    'basic',
    'standard',
    'gpu_basic',
    'gpu_standard',
    'dedicated_fragments',
    'gpu_pro',
    'gpu_pro2',
]


@click.command
@click.option('-t', '--terminated', is_flag=True)
@click.pass_obj
def list(ctx, terminated):
    response = ctx.client.get(
        '/api/v1/list_inference_env',
        params={} if terminated else {'status': 'active'},
    )
    handle_response(response)


@click.command
@click.argument('env', required=False)
@click.pass_obj
def get(ctx, env):
    status_code = 0
    if env:
        envs = [ctx.get_env(env)]
        if not envs[0]:
            raise ValueError(f"No such env: '{env}'")
    else:
        envs = ctx.get_envs()
    if envs:
        for env_ in envs:
            response = ctx.client.get(f'/api/v1/env/{env_.id}/status')
            # if env_.tag and response.status_code == 200:
            #     print(f"{env_.tag}: ", end='')
            status_code |= handle_response(response)
    else:
        logging.error("No known envs.")
    return status_code


@click.command
@click.option('-s', '--servable', required=True)
#@click.option('-p', '--server-plan', required=True, type=click.Choice(PLAN_TYPES))
@click.option('-p', '--server-plan', required=True, type=str)
@click.option('-c', '--capacity', type=int, default=1)
@click.option('-l', '--auto-scaling-limit', type=int)
@click.option('-t', '--tag')
@click.pass_obj
def create(ctx, servable, server_plan, capacity, auto_scaling_limit, tag):
    response = create_env(ctx, servable, server_plan, capacity, auto_scaling_limit, tag)
    return handle_response(response)


def create_env(ctx, servable, server_plan, capacity, auto_scaling_limit, tag):
    # this function is also called by `aiopcli deploy`
    if ctx.get_env(tag):
        raise ValueError(f"Name '{tag}' is already in use")
    request = {
        'servable_id': servable,
        'server_plan': server_plan,
        'desired_capacity': capacity,
        'auto_scaling_enabled': auto_scaling_limit is not None,
    }
    if auto_scaling_limit:
        request['auto_scaling_max_replicas'] = auto_scaling_limit
    response = ctx.client.post('/api/v1/create_inference_env', json=request)
    if 200 <= response.status_code < 300:
        # FIXME: move error check code once the status code changes
        result = response.json()
        if result['result'] != 0:
            raise ValueError(f"Failed to create env: {result['msg']}")
        ctx.add_env(env_id=result['env_id'], tag=tag)
    return response


@click.command
@click.argument('env')
@click.option('-s', '--servable')
@click.option('-p', '--server-plan')
#@click.option('-p', '--server-plan', type=click.Choice(PLAN_TYPES))
@click.option('-c', '--capacity', type=int)
@click.option('--auto-scale', type=click.Choice(['true', 'false']))
@click.option('-l', '--auto-scaling-limit', type=int)
@click.pass_obj
def update(ctx, env, servable, server_plan, capacity, auto_scale, auto_scaling_limit):
    response = update_env(
        ctx, env, servable, server_plan, capacity, auto_scale, auto_scaling_limit)
    return response


def update_env(ctx, env, servable, server_plan, capacity, auto_scale, auto_scaling_limit):
    env_ = ctx.get_env(env)
    if env_ is None:
        raise ValueError(f"Unknown env {env}")

    # get current settings for this env
    response = ctx.client.get(f'/api/v1/env/{env_.id}/status')
    if response.status_code != 200:
        return handle_response(response)
    request = {
        k: v for k, v in response.json().items() if k in (
            'env_id', 'servable_id', 'server_plan', 'desired_capacity', 
            'auto_scaling_enabled', 'auto_scaling_max_replicas',
        )
    }

    # update with inputs
    auto_scale = {'true': True, 'false': False, None: None}[auto_scale]
    if servable is not None:
        request['servable_id'] = servable
    if server_plan is not None:
        request['server_plan'] = server_plan
    if capacity is not None:
        request['desired_capacity'] = capacity
    if auto_scale is not None:
        request['auto_scaling_enabled'] = auto_scale
    if auto_scaling_limit is not None:
        request['auto_scaling_max_replicas'] = auto_scaling_limit
    
    if request['auto_scaling_enabled'] is False:
        if auto_scaling_limit is not None:
            raise ValueError("Cannot disable auto scaling while setting limit")
        # auto_scaling_max_replicas not allow if auto_scaling_enabled is false
        request.pop('auto_scaling_max_replicas', None)

    response = ctx.client.post('/api/v1/update_inference_env', json=request)
    return handle_response(response)


@click.command
@click.argument('env')
@click.pass_obj
def delete(ctx, env):
    env_ = ctx.get_env(env)
    if not env_:
        raise ValueError(f"No such tag: '{env}'")
    response = ctx.client.post('/api/v1/delete_inference_env', json={'env_id': env_.id})

    # FIXME: once an error code is returned properly, rewrite this
    exit_code = 1
    if 200 <= response.status_code < 300:
        result = response.json()
        exit_code = result['result']
    if exit_code == 0:
        ctx.delete_env(env_.id)

    # return _handle_response(response)
    handle_response(response)
    return exit_code


@click.group("env")
def cli():
    pass

@cli.command
@click.argument('env')
@click.option('-r', '--replica')
@click.option('-c', '--container', default='api-server')
@click.option('-f', '--follow', is_flag=True)
@click.option('-s', '--since')
@click.pass_obj
def logs(ctx, env, replica, container, follow, since):
    env_ = ctx.get_env(env)
    if not env_:
        raise ValueError(f"No such tag: '{env}'")

    # if no replica is given, pick the first running replica from the list
    if not replica:
        response = ctx.client.get(f'/api/v1/env/{env_.id}/status')
        if response.status_code != 200:
            raise ValueError("Failed to get status")
        status = response.json()
        running = [r for r in status["replicas"] if r["status"] == "Running"]
        if not running:
            raise ValueError("No running replicas")
        replica = running[0]["replica_id"]
        if len(running) > 1:
            logging.info(
                "%s running replicas found; defaulting to `%s`", len(running), replica)

    params={
        'replica_id': replica,
        'container': container,
        'follow': {True: 'true', False: 'false'}[follow],
    }
    if follow:
        params['follow'] = 'true'
    if since:
        match = re.fullmatch(r'(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?', since)
        if not match:
            raise ValueError("'since' value is invalid")
        seconds = (
            int(match.group(1) or 0) * 3600 + int(match.group(2) or 0) * 60
            + int(match.group(3) or 0))
        if not seconds:
            raise ValueError("'since' must be non-zero")
        params['since_seconds'] = seconds
    
    if follow:
        with ctx.client.stream(
                "GET", f'/api/v1/env/{env_.id}/logs', params=params) as response:
            return handle_response(response, stream=True)
    else:
        response = ctx.client.get(
            f'/api/v1/env/{env_.id}/logs', params=params)
        return handle_response(response)


cli.add_command(list)
cli.add_command(get)
cli.add_command(create)
cli.add_command(update)
cli.add_command(delete)
