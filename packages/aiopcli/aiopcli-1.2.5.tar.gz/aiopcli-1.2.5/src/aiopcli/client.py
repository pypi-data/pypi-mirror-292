from typing import Optional
import logging
import re
import json as json_
from pathlib import Path

import atomicwrites
import toml
import httpx

from aiopcli import settings
from aiopcli.constants import REF_REGEX

try:
    import pydantic.v1 as pydantic  # pydantic v2
except ImportError:
    import pydantic  # pydantic v1


class Client(httpx.Client):
    @classmethod
    def __get_validators__(cls):
        return iter(())
        # yield cls.trivial_validator

    def request(self, method, url, *, json=None, **kwargs):
        logging.info("Request: %s", json_.dumps(json, indent=2, ensure_ascii=False))
        return super().request(method, url, json=json, **kwargs)

    # @classmethod
    # def trivial_validator(cls, v):
    #     assert isinstance(v, Client)
    #     return v


def make_client(host: str, timeout: int = 300, apikey: str = None):
    if not re.match(r'^https?://', host):
        host = 'http://' + host
    logging.info("api key: %s", apikey)
    return Client(
        base_url=host.rstrip('/'),
        timeout=httpx.Timeout(timeout, read=timeout),
        headers={'aiop-apikey': apikey} if apikey else None
    )


class Context(pydantic.BaseModel):
    client: Client
    config: settings.Config = settings.Config()
    config_path: Optional[Path]
    config_file: settings.ConfigFile = settings.ConfigFile()

    @property
    def host(self):
        return self.config.host

    @property
    def apikey(self):
        return self.config.apikey

    def write_config(self):
        if self.config_path and self.config_file:
            with atomicwrites.atomic_write(self.config_path, overwrite=True) as fp:
                toml.dump(self.config_file.dict(exclude_none=True), fp)
            logging.info("Updated config %s", self.config_path)
            return 0
        else:
            logging.warning("Could not access config file.")
            return 1

    def add_env(self, env_id, tag=None):
        if self.config_file:
            self.config_file.envs.append(settings.Env(id=env_id, tag=tag))
            self.write_config()

    def delete_env(self, env_id):
        if self.config_file:
            for k, env in enumerate(self.config_file.envs) or ():
                if env.id == env_id:
                    logging.info(f"Deleting env: {env}")
                    del self.config_file.envs[k]
                    self.write_config()
                    return
            logging.info(f"Env {env_id} was not in known envs.")

    def get_envs(self):
        return self.config_file.envs or []

    def get_env(self, ref, pass_env_id=True):
        # pass_env_id
        if ref is None:
            return None
        if re.match(REF_REGEX, ref):
            for env in self.config_file.envs or ():
                if env.tag == ref:
                    return env
            return None
        if re.match(r'^\d+$', ref):
            env_id = int(ref)
            for env in self.config_file.envs or ():
                if env.id == env_id:
                    return env
            return settings.Env(id=int(ref)) if pass_env_id else None
        raise ValueError(f"Invalid reference: {ref}")


def url_join(url, path):
    if url.endswith('/'):
        url = url[:-1]
    if path.startswith('/'):
        path = path[1:]
    return f'{url}/{path}'
