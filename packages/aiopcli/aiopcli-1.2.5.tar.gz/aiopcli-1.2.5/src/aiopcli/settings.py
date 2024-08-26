from pathlib import Path
from typing import Optional, Dict, List
import logging

import toml
try:
    import pydantic.v1 as pydantic  # pydantic>=2
    from pydantic.v1 import BaseSettings
except ImportError:
    import pydantic  # pydantic<2
    from pydantic import BaseSettings

from aiopcli import constants

logger = logging.getLogger()


class EnvConfig(BaseSettings):
    config: Path = '~/.aiop'
    profile: str = None
    host: str = None
    apikey: str = None
    log_level: constants.LogLevel = None

    class Config:
        env_prefix = 'aiop_'


class Config(pydantic.BaseModel):
    host: str = pydantic.Field(None, regex=constants.HOST_REGEX)
    apikey: str = None
    log_level: constants.LogLevel = None


class Env(pydantic.BaseModel):
    id: int
    tag: Optional[str] = pydantic.Field(None, regex=constants.REF_REGEX)


class ConfigFile(Config):
    default: str = None
    profiles: Dict[str, Config] = {}
    envs: List[Env] = []


def load_config(profile=None, host=None, apikey=None, log_level=None):
    env = EnvConfig()
    config_path = env.config.expanduser()
    # allow initial log level to be set by environment variable
    logger.setLevel(log_level or env.log_level or constants.DEFAULT_LOG_LEVEL)

    config = Config(host='https://aiops.inside.ai')

    if config_path.is_file():
        logging.info(f"Loading config file '{config_path}'")
        # base level configs are defaults and are applied first
        fields = toml.loads(config_path.read_text())
        config_file = ConfigFile.parse_obj(fields)

        config = _merge(config, config_file)

        # next is profile-level configs
        profile = profile or env.profile or config_file.default
        if profile in config_file.profiles:
            logging.info(f"Using profile '{profile}'")
            config = _merge(config, config_file.profiles[profile])
        elif profile:
            logging.error(f"Unrecognized profile {profile}")
            exit(1)
        else:
            logging.info("No profile given, using defaults")
    else:
        config_file = ConfigFile()

    # then, environment
    config = _merge(config, env)

    # finally, command line arguments
    config = _merge(config, Config(host=host, apikey=apikey, log_level=log_level))

    logger.setLevel(config.log_level or constants.DEFAULT_LOG_LEVEL)

    logger.info("Config: %s", config_file)

    return config, config_path, config_file


def _merge(c1, c2):
    d = c1.dict(exclude_none=True)
    d.update(c2.dict(exclude_none=True))
    config = Config.parse_obj(d)
    return config
