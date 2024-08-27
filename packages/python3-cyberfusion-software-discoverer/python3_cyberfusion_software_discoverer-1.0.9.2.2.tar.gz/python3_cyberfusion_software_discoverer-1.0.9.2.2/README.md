# python3-cyberfusion-software-discoverer

Library to discover software installed on system.

# Install

## PyPI

Run the following command to install the package from PyPI:

    pip3 install python3-cyberfusion-software-discoverer

## Debian

Run the following commands to build a Debian package:

    mk-build-deps -i -t 'apt -o Debug::pkgProblemResolver=yes --no-install-recommends -y'
    dpkg-buildpackage -us -uc

# Configure

No configuration is supported.

# Usage

## Example

```python
from cyberfusion.SoftwareDiscoverer import discoverer_registry
from cyberfusion.SoftwareDiscoverer import discoverers
from cyberfusion.SoftwareDiscoverer import traits

# Loop through all discoverers

for discoverer in discoverer_registry:
  if discoverer.discover():
    print("Present")

    for trait in discoverer.traits:
      print(f"Has trait {trait}")
  else:
    print("Not present")

# Get single discoverer

discoverer = discoverer_registry.get(discoverers.ElasticsearchDiscoverer)
has_cluster_trait = traits.ElasticsearchClusterTrait in discoverer.traits
```
