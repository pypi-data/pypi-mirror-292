
# Deploy django project with fabric

### Installation
1. Add `djfabric` to `requirements.txt`
`.env` example:
```
DOMAIN=example.com
HOST=123.123.123.123
HOST_PASSWORD=123
PROJECT_NAME=proj
DB_NAME=projdb
DEV_EMAIL=pmaigutyak@gmail.com
CELERY=off
```

```fabfile.py``` example:
```

from djfabric.fab import setup, restart, deploy

setup()

```
To fix `except IOError, e:`:
```
Traceback (most recent call last):
  File "/home/dev/venvs/mp2/bin/fab", line 5, in <module>
    from fabric.main import main
  File "/home/dev/venvs/mp2/lib/python3.8/site-packages/fabric/main.py", line 22, in <module>
    from fabric import api, state, colors
  File "/home/dev/venvs/mp2/lib/python3.8/site-packages/fabric/api.py", line 12, in <module>
    from fabric.decorators import (hosts, roles, runs_once, with_settings, task,
  File "/home/dev/venvs/mp2/lib/python3.8/site-packages/fabric/decorators.py", line 9, in <module>
    from Crypto import Random
  File "/home/dev/venvs/mp2/lib/python3.8/site-packages/Crypto/Random/__init__.py", line 28, in <module>
    from Crypto.Random import OSRNG
  File "/home/dev/venvs/mp2/lib/python3.8/site-packages/Crypto/Random/OSRNG/__init__.py", line 32, in <module>
    from Crypto.Random.OSRNG.posix import new
  File "/home/dev/venvs/mp2/lib/python3.8/site-packages/Crypto/Random/OSRNG/posix.py", line 66
    except IOError, e:
```
do:
```
pip uninstall pycryptodome
pip install pycryptodome==3.18.0
```
