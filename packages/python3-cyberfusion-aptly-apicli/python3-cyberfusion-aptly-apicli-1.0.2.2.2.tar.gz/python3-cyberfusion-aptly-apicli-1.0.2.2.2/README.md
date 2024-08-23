# python3-cyberfusion-aptly-apicli

API library for [Aptly](https://www.aptly.info/).

# Install

## PyPI

Run the following command to install the package from PyPI:

    pip3 install python3-cyberfusion-aptly-apicli

## Generic

Run the following command to create a source distribution:

    python3 setup.py sdist

## Debian

Run the following commands to build a Debian package:

    mk-build-deps -i -t 'apt -o Debug::pkgProblemResolver=yes --no-install-recommends -y'
    dpkg-buildpackage -us -uc

# Configure

## Config file options

* Section `aptly-api`, key `serverurl`
* Section `aptly-api`, key `username` (optional)
* Section `aptly-api`, key `apikey` (optional)

## Class options

* `config_file_path`. Non-default config file path.

# Usage

## Example

```python
from cyberfusion.AptlyApiCli import AptlyApiRequest

r = AptlyApiRequest()

# Upload temporary file

endpoint = "/api/files/aptly-0.9"

with open("aptly_0.9~dev+217+ge5d646c_i386.deb", "rb") as f:
    r.POST(endpoint, data={}, files={"file": f})

print(r.execute())

# Add package

endpoint = "/api/repos/repo1/file/aptly-0.9"

r = AptlyApiRequest()
r.POST(endpoint, data={})
print(r.execute())
```
