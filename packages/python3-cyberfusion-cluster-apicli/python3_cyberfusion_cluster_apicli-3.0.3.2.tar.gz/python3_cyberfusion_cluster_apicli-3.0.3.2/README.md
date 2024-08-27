# python3-cyberfusion-cluster-apicli

API client for Core API.

# Install

## PyPI

Run the following command to install the package from PyPI:

    pip3 install python3-cyberfusion-cluster-apicli

## Debian

Run the following commands to build a Debian package:

    mk-build-deps -i -t 'apt -o Debug::pkgProblemResolver=yes --no-install-recommends -y'
    dpkg-buildpackage -us -uc

# Configure

## Config file options

* Section `clusterapi`, key `serverurl`
* Section `clusterapi`, keys `username` and `password` (optional)
* Section `clusterapi`, key `apikey` (optional)

## Class options

* `config_file_path`. Non-default config file path.
* `authenticate`. Endpoint is called without token when set.

# Usage

## Basic

```python
from cyberfusion.ClusterApiCli import ClusterApiRequest

endpoint = "/api/v1/certificates"

r = ClusterApiRequest()
```

## Request

First, set the request:

```python
r.GET(endpoint)
r.PATCH(endpoint)
r.PUT(endpoint)
r.POST(endpoint)
r.DELETE(endpoint)
```

Then execute the request:

```
print(r.execute())
```
