"""Discoverers."""

import json
import os
import subprocess
from typing import List

from cyberfusion.SoftwareDiscoverer import paths
from cyberfusion.SoftwareDiscoverer import traits as _traits
from cyberfusion.SoftwareDiscoverer.config_parsers import (
    ElasticsearchConfigParser,
    RabbitMQConfigParser,
    RedisConfigParser,
    SambaConfigParser,
)
from cyberfusion.SoftwareDiscoverer.interfaces import (
    DiscovererInterface,
    TraitInterface,
)


class Discoverer(DiscovererInterface):
    """Discoverer."""

    def __init__(self) -> None:
        """Do nothing."""
        pass

    def discover(self) -> bool:
        """Discover."""
        raise NotImplementedError

    @property
    def traits(self) -> List[TraitInterface]:
        """Get traits."""
        return []


class ElasticsearchDiscoverer(Discoverer):
    """Discoverer."""

    def __init__(self) -> None:
        """Do nothing."""
        pass

    def discover(self) -> bool:
        """Discover."""
        return os.path.exists(
            os.path.join(
                os.path.sep,
                "usr",
                "share",
                "elasticsearch",
                "bin",
                "elasticsearch",
            )
        )

    @property
    def traits(self) -> List[TraitInterface]:
        """Get traits."""
        result: List[TraitInterface] = []

        if self._has_authentication_trait:
            result.append(_traits.ElasticsearchAuthenticationTrait)

        if self._has_http_ssl_trait:
            result.append(_traits.ElasticsearchHTTPSSLTrait)

        if self._has_cluster_trait:
            result.append(_traits.ElasticsearchClusterTrait)

        return result

    @property
    def _has_authentication_trait(self) -> bool:
        """Get trait."""
        config = ElasticsearchConfigParser.parse()

        try:
            return config["xpack.security.enabled"]
        except KeyError:
            return False

    @property
    def _has_http_ssl_trait(self) -> bool:
        """Get trait."""
        config = ElasticsearchConfigParser.parse()

        try:
            return config["xpack.security.http.ssl.enabled"]
        except KeyError:
            return False

    @property
    def _has_cluster_trait(self) -> bool:
        """Get trait."""
        config = ElasticsearchConfigParser.parse()

        try:
            return config["discovery.seed_hosts"]
        except KeyError:
            return False


class MetabaseDiscoverer(Discoverer):
    """Discoverer."""

    def __init__(self) -> None:
        """Do nothing."""
        pass

    def discover(self) -> bool:
        """Discover."""
        return os.path.exists(
            os.path.join(
                os.path.sep,
                "opt",
                "metabase",
            )
        )


class MeilisearchDiscoverer(Discoverer):
    """Discoverer."""

    def __init__(self) -> None:
        """Do nothing."""
        pass

    def discover(self) -> bool:
        """Discover."""
        return os.path.exists(os.path.join(paths.PATH_USR_BIN, "meilisearch"))


class Fail2banDiscoverer(Discoverer):
    """Discoverer."""

    def __init__(self) -> None:
        """Do nothing."""
        pass

    def discover(self) -> bool:
        """Discover."""
        return os.path.exists(
            os.path.join(paths.PATH_USR_BIN, "fail2ban-server")
        )


class SwayDiscoverer(Discoverer):
    """Discoverer."""

    def __init__(self) -> None:
        """Do nothing."""
        pass

    def discover(self) -> bool:
        """Discover."""
        return os.path.exists(os.path.join(paths.PATH_USR_BIN, "sway-server"))


class RealPathsWatcherDiscoverer(Discoverer):
    """Discoverer."""

    def __init__(self) -> None:
        """Do nothing."""
        pass

    def discover(self) -> bool:
        """Discover."""
        return os.path.exists(
            os.path.join(paths.PATH_USR_BIN, "cluster-real-paths-watcher")
        )


class PowerDNSDiscoverer(Discoverer):
    """Discoverer."""

    def __init__(self) -> None:
        """Do nothing."""
        pass

    def discover(self) -> bool:
        """Discover."""
        return os.path.exists(os.path.join(paths.PATH_USR_SBIN, "pdns_server"))


class ApacheDiscoverer(Discoverer):
    """Discoverer."""

    def __init__(self) -> None:
        """Do nothing."""
        pass

    def discover(self) -> bool:
        """Discover."""
        return os.path.exists(os.path.join(paths.PATH_USR_SBIN, "apache2"))


class NginxDiscoverer(Discoverer):
    """Discoverer."""

    def __init__(self) -> None:
        """Do nothing."""
        pass

    def discover(self) -> bool:
        """Discover."""
        return os.path.exists(os.path.join(paths.PATH_USR_SBIN, "nginx"))


class FastRedirectDiscoverer(Discoverer):
    """Discoverer."""

    def __init__(self) -> None:
        """Do nothing."""
        pass

    def discover(self) -> bool:
        """Discover."""
        return os.path.exists(
            os.path.join(
                os.path.sep, "opt", "fast-redirect", "bin", "fast-redirect"
            )
        )


class KeepalivedDiscoverer(Discoverer):
    """Discoverer."""

    def __init__(self) -> None:
        """Do nothing."""
        pass

    def discover(self) -> bool:
        """Discover."""
        return os.path.exists(os.path.join(paths.PATH_USR_SBIN, "keepalived"))


class HAProxyDiscoverer(Discoverer):
    """Discoverer."""

    def __init__(self) -> None:
        """Do nothing."""
        pass

    def discover(self) -> bool:
        """Discover."""
        return os.path.exists(os.path.join(paths.PATH_USR_SBIN, "haproxy"))


class SupervisorDiscoverer(Discoverer):
    """Discoverer."""

    def __init__(self) -> None:
        """Do nothing."""
        pass

    def discover(self) -> bool:
        """Discover."""
        return os.path.exists(os.path.join(paths.PATH_USR_BIN, "supervisord"))


class MySQLDDiscoverer(Discoverer):
    """Discoverer."""

    def __init__(self) -> None:
        """Do nothing."""
        pass

    def discover(self) -> bool:
        """Discover."""
        return os.path.exists(os.path.join(paths.PATH_USR_SBIN, "mysqld"))


class PostfixDiscoverer(Discoverer):
    """Discoverer."""

    def __init__(self) -> None:
        """Do nothing."""
        pass

    def discover(self) -> bool:
        """Discover."""
        return os.path.exists(os.path.join(paths.PATH_USR_SBIN, "postfix"))


class NullmailerDiscoverer(Discoverer):
    """Discoverer."""

    def __init__(self) -> None:
        """Do nothing."""
        pass

    def discover(self) -> bool:
        """Discover."""
        return os.path.exists(
            os.path.join(paths.PATH_USR_SBIN, "nullmailer-send")
        )


class DnsdistDiscoverer(Discoverer):
    """Discoverer."""

    def __init__(self) -> None:
        """Do nothing."""
        pass

    def discover(self) -> bool:
        """Discover."""
        return os.path.exists(os.path.join(paths.PATH_USR_BIN, "dnsdist"))


class DovecotDiscoverer(Discoverer):
    """Discoverer."""

    def __init__(self) -> None:
        """Do nothing."""
        pass

    def discover(self) -> bool:
        """Discover."""
        return os.path.exists(os.path.join(paths.PATH_USR_SBIN, "dovecot"))


class RabbitMQConsumeDiscoverer(Discoverer):
    """Discoverer."""

    def __init__(self) -> None:
        """Do nothing."""
        pass

    def discover(self) -> bool:
        """Discover."""
        return os.path.exists(
            os.path.join(paths.PATH_USR_BIN, "rabbitmq-consumer")
        )


class ProFTPDDiscoverer(Discoverer):
    """Discoverer."""

    def __init__(self) -> None:
        """Do nothing."""
        pass

    def discover(self) -> bool:
        """Discover."""
        return os.path.exists(os.path.join(paths.PATH_USR_SBIN, "proftpd"))


class RabbitMQDiscoverer(Discoverer):
    """Discoverer."""

    def __init__(self) -> None:
        """Do nothing."""
        pass

    def discover(self) -> bool:
        """Discover."""
        return os.path.exists(
            os.path.join(
                os.path.sep, "usr", "lib", "rabbitmq", "bin", "rabbitmq-server"
            )
        )

    @property
    def traits(self) -> List[TraitInterface]:
        """Get traits."""
        result: List[TraitInterface] = []

        if self._has_ssl_trait:
            result.append(_traits.RabbitMQSSLTrait)

        if self._has_management_ssl_trait:
            result.append(_traits.RabbitMQManagementSSLTrait)

        if self._has_cluster_trait:
            result.append(_traits.RabbitMQClusterTrait)

        return result

    @property
    def _has_ssl_trait(self) -> bool:
        """Get trait."""
        config = RabbitMQConfigParser.parse()

        try:
            return bool(config["ssl_options.certfile"])
        except KeyError:
            return False

    @property
    def _has_management_ssl_trait(self) -> bool:
        """Get trait."""
        config = RabbitMQConfigParser.parse()

        try:
            return bool(config["management.ssl.certfile"])
        except KeyError:
            return False

    @property
    def _has_cluster_trait(self) -> bool:
        """Get trait."""
        return (
            len(
                json.loads(
                    subprocess.run(
                        [
                            os.path.join(paths.PATH_USR_SBIN, "rabbitmqctl"),
                            "cluster_status",
                            "--formatter",
                            "json",
                        ],
                        check=True,
                        stdout=subprocess.PIPE,
                        text=True,
                    ).stdout
                )["running_nodes"]
            )
            != 1
        )


class SingleStoreDiscoverer(Discoverer):
    """Discoverer."""

    def __init__(self) -> None:
        """Do nothing."""
        pass

    def discover(self) -> bool:
        """Discover."""
        path = os.path.join(os.path.sep, "opt")

        if not os.path.exists(path):
            return False

        contents = os.listdir(path)

        for content in contents:
            if not content.startswith("singlestoredb-server-"):
                continue

            return os.path.exists(os.path.join(path, content, "memsqld"))

        return False


class PostgreSQLDiscoverer(Discoverer):
    """Discoverer."""

    def __init__(self) -> None:
        """Do nothing."""
        pass

    def discover(self) -> bool:
        """Discover."""
        path = os.path.join(os.path.sep, "usr", "lib", "postgresql")

        if not os.path.exists(path):
            return False

        contents = os.listdir(path)

        if not contents:
            return False

        return os.path.exists(
            os.path.join(path, contents[0], os.path.join("bin", "postgres"))
        )


class RedisDiscoverer(Discoverer):
    """Discoverer."""

    def __init__(self) -> None:
        """Do nothing."""
        pass

    def discover(self) -> bool:
        """Discover."""
        return os.path.exists(os.path.join(paths.PATH_USR_BIN, "redis-server"))

    @property
    def traits(self) -> List[TraitInterface]:
        """Get traits."""
        result: List[TraitInterface] = []

        if self._has_password_trait:
            result.append(_traits.RedisPasswordTrait)

        if self._has_slave_trait:
            result.append(_traits.RedisSlaveTrait)

        return result

    @property
    def _has_password_trait(self) -> bool:
        """Get trait."""
        config = RedisConfigParser.parse()

        return "requirepass" in config

    @property
    def _has_slave_trait(self) -> bool:
        """Get trait."""
        config = RedisConfigParser.parse()

        return "slaveof" in config


class SambaDiscoverer(Discoverer):
    """Discoverer."""

    def __init__(self) -> None:
        """Do nothing."""
        pass

    def discover(self) -> bool:
        """Discover."""
        return os.path.exists(
            os.path.join(os.path.sep, "etc", "samba", "smb.conf")
        )

    @property
    def traits(self) -> List[TraitInterface]:
        """Get traits."""
        result: List[TraitInterface] = []

        if self._has_is_active_directory_domain_controller_trait:
            result.append(_traits.SambaIsActiveDirectoryDomainControllerTrait)

        return result

    @property
    def _has_is_active_directory_domain_controller_trait(self) -> bool:
        """Get trait."""
        config = SambaConfigParser.parse()

        return (
            config["global"]["server role"]
            == "active directory domain controller"
        )
