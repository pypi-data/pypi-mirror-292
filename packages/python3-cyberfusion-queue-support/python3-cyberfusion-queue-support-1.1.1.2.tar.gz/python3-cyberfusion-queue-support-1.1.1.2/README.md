# python3-cyberfusion-queue-support

Library to queue actions.

# Install

## PyPI

Run the following command to install the package from PyPI:

    pip3 install python3-cyberfusion-queue-support

## Generic

Run the following command to create a source distribution:

    python3 setup.py sdist

## Debian

Run the following commands to build a Debian package:

    mk-build-deps -i -t 'apt -o Debug::pkgProblemResolver=yes --no-install-recommends -y'
    dpkg-buildpackage -us -uc

# Configure

No configuration is supported.

# Usage

## Example

```python
from cyberfusion.QueueSupport import Queue
from cyberfusion.QueueSupport.items.chmod import ChmodItem

queue = Queue()

item = ChmodItem(path="/tmp/example.txt", mode=0o600)
print(item.outcomes)

queue.add(item)

preview = True or False

outcomes = queue.process(preview=preview)

for outcome in outcomes:
    print(str(outcome))
```
