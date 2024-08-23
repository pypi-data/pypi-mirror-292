"""Config parsers."""

import configparser
import os
from typing import Dict

import yaml

from cyberfusion.SoftwareDiscoverer.interfaces import ConfigParserInterface


class ConfigParser(ConfigParserInterface):
    """Config parser."""

    def __init__(self) -> None:
        """Do nothing."""
        pass

    @staticmethod
    def parse() -> dict:
        """Parse config."""
        raise NotImplementedError


class ElasticsearchConfigParser(ConfigParser):
    """Config parser."""

    def __init__(self) -> None:
        """Do nothing."""
        pass

    @staticmethod
    def parse() -> dict:
        """Parse config."""
        path = os.path.join(
            os.path.sep, "etc", "elasticsearch", "elasticsearch.yml"
        )

        with open(path, "r") as f:
            return yaml.safe_load(f)


class SambaConfigParser(ConfigParser):
    """Config parser."""

    def __init__(self) -> None:
        """Do nothing."""
        pass

    @staticmethod
    def parse() -> dict:
        """Parse config."""
        path = os.path.join(os.path.sep, "etc", "samba", "smb.conf")

        config = configparser.ConfigParser()
        config.read(path)

        return dict(config)


class RedisConfigParser(ConfigParser):
    """Config parser."""

    def __init__(self) -> None:
        """Do nothing."""
        pass

    @staticmethod
    def parse() -> dict:
        """Parse config."""
        result = {}

        path = os.path.join(os.path.sep, "etc", "redis", "redis.conf")

        with open(path, "r") as f:
            for line in f.read().splitlines():
                if not line:  # Empty
                    continue

                if line.startswith("#"):  # Comment
                    continue

                k, v = line.split(" ", 1)

                result[k] = v

        return result


class RabbitMQConfigParser(ConfigParser):
    """Config parser."""

    def __init__(self) -> None:
        """Do nothing."""
        pass

    @staticmethod
    def parse() -> dict:
        """Parse config."""
        result: Dict[str, str] = {}

        path = os.path.join(os.path.sep, "etc", "rabbitmq", "rabbitmq.conf")

        if not os.path.exists(path):
            return result

        with open(path, "r") as f:
            for line in f.read().splitlines():
                if not line:  # Empty
                    continue

                if line.startswith("#"):  # Comment
                    continue

                k, v = line.split("=", 1)

                k = k.rstrip()
                v = v.lstrip()

                result[k] = v

        return result
