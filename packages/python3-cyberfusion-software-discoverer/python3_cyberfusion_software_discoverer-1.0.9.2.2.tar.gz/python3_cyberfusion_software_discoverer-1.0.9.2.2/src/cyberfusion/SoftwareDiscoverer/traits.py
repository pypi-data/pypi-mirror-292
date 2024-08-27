"""Traits."""

from cyberfusion.SoftwareDiscoverer.interfaces import TraitInterface


class Trait(TraitInterface):
    """Trait."""

    def __init__(self) -> None:
        """Do nothing."""
        pass


class ElasticsearchAuthenticationTrait(Trait):
    """Trait."""

    pass


class ElasticsearchHTTPSSLTrait(Trait):
    """Trait."""

    pass


class ElasticsearchClusterTrait(Trait):
    """Trait."""

    pass


class RabbitMQSSLTrait(Trait):
    """Trait."""

    pass


class RabbitMQManagementSSLTrait(Trait):
    """Trait."""

    pass


class RabbitMQClusterTrait(Trait):
    """Trait."""

    pass


class RedisSlaveTrait(Trait):
    """Trait."""

    pass


class RedisPasswordTrait(Trait):
    """Trait."""

    pass


class SambaIsActiveDirectoryDomainControllerTrait(Trait):
    """Trait."""

    pass
