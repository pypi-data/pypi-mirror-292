import contextlib
from pathlib import Path
from typing import BinaryIO, Union
import hashlib
import logging
import time

logger = logging.getLogger()

ENDPOINT = '/isapi/api/v1/artifacts'


def get_artifacts(ctx, digest: str = None):
    response = ctx.client.get(ENDPOINT, params={'digest': digest} if digest else None)
    return _handle_response(response)


def get(ctx, artifact_id: str):
    response = ctx.client.get(f'{ENDPOINT}/{artifact_id}')
    return _handle_response(response)


def post(ctx, files):
    response = ctx.client.post(ENDPOINT, files=files)
    return _handle_response(response)


def _handle_response(response):
    if not (200 <= response.status_code < 300):
        # TODO: raise useful exception
        raise ValueError(f"Failed to acquire resource '{ENDPOINT}': {response.content} \n"
                         f"Request failed with status code: {response.status_code}")
    return response.json()


def add(ctx, path: Union[str, Path, BinaryIO], force: bool = False):
    # FIXME: use separate kwarg for file pointers; "path" is not accurate
    logger.info(f"ARTIFACT '{path}'")
    if isinstance(path, str):
        path = Path(path)

    with contextlib.ExitStack() as stack:
        if isinstance(path, Path):
            if not path.exists():
                raise ValueError(f"{path}: does not exist")
            if not path.is_file():
                raise ValueError(f"{path}: only regular files can be registered as artifacts.")
            file_name = path.name
            fp = stack.enter_context(path.open('rb'))
        else:
            file_name = 'data'
            fp = path

        response = None
        if not force:
            logging.info("  Computing hash...")

            hasher = hashlib.sha256()
            while data := fp.read(8096):
                hasher.update(data)
            fp.seek(0)
            digest = f'sha256:{hasher.hexdigest()}'

            logging.info(f"  Checking if artifact exists: {digest}")
            response = get_artifacts(ctx, digest=digest)

        if response:
            response = response[0]
            logger.info(f"  Already exists on server: {response['artifactId']}")
        else:
            logger.info(f"  Does not exist. Uploading '{path}'...")
            file_data = (file_name, fp, 'application/octet-stream')
            response = post(ctx, files={'data': file_data})
        return response


def wait(ctx, artifact_id, timeout=600, interval=1):
    tick = time.time()
    while True:
        if time.time() > tick + timeout:
            # TODO: error handling
            raise ValueError("Timed out.")
        response = get(ctx, artifact_id)
        if response['status'] == 'failed':
            # TODO: error handling
            raise ValueError(f"Artifact failed: {response}.")
        elif response['status'] == 'ready':
            return response
        time.sleep(interval)


def register_artifacts(ctx, timeout: int, force: bool = False, **kwargs):
    # apiserver
    logger.info('Uploading apiserver...')
    kwargs['apiServerImageArtifactId'] = register_artifact(
        ctx, kwargs.pop('apiServer'), timeout, force)
    logger.info(f"Uploaded apiServer artifactId: {kwargs['apiServer']}")

    # inferenceserver
    if kwargs.get('inferenceServer'):
        logger.info('Uploading inferenceserver...')
        kwargs['inferenceServerImageArtifactId'] = register_artifact(
            ctx, kwargs.pop('inferenceServer'), timeout, force)
        logger.info(f"Uploaded inferenceServer artifactId: {kwargs['inferenceServer']}")
    return kwargs


def register_artifact(ctx, image: str, timeout: int, force: bool):
    image = Path() / image
    artifact_id = add(ctx, path=image, force=force)['artifactId']
    wait(ctx, artifact_id, timeout=timeout)
    return artifact_id
