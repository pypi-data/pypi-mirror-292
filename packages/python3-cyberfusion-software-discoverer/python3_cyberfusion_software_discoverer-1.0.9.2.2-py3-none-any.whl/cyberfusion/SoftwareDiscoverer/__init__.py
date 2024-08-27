"""Provides registries."""

from cyberfusion.SoftwareDiscoverer import discoverers
from cyberfusion.SoftwareDiscoverer.registries import discoverer_registry

discoverer_registry.add(
    [
        discoverers.ElasticsearchDiscoverer,
        discoverers.MetabaseDiscoverer,
        discoverers.MeilisearchDiscoverer,
        discoverers.Fail2banDiscoverer,
        discoverers.PowerDNSDiscoverer,
        discoverers.ApacheDiscoverer,
        discoverers.NginxDiscoverer,
        discoverers.FastRedirectDiscoverer,
        discoverers.KeepalivedDiscoverer,
        discoverers.HAProxyDiscoverer,
        discoverers.SupervisorDiscoverer,
        discoverers.MySQLDDiscoverer,
        discoverers.PostfixDiscoverer,
        discoverers.NullmailerDiscoverer,
        discoverers.DnsdistDiscoverer,
        discoverers.DovecotDiscoverer,
        discoverers.ProFTPDDiscoverer,
        discoverers.RabbitMQDiscoverer,
        discoverers.SingleStoreDiscoverer,
        discoverers.PostgreSQLDiscoverer,
        discoverers.RedisDiscoverer,
        discoverers.SambaDiscoverer,
        discoverers.RabbitMQConsumeDiscoverer,
        discoverers.SwayDiscoverer,
        discoverers.RealPathsWatcherDiscoverer,
    ]
)
