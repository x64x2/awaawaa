# awaawaa


## Overview

**awaawaa** is a simple SOCKS5 server implementation, written as a standalone Python script.

### Features

- Threaded: one thread per incoming connection
- Server-side domain name resolution support

TODO:

- Enforcing ruleset to mitigate security disks (i.e. firewalling)
- UDP ASSOCIATE requests support
- GSSAPI authentication support

## Installation

**awaawaa** was tested on *Debian GNU/Linux sid*, but it may work on other
platforms with little to no tweaking.

The single dependency of **awaawaa** is the Python interpreter itself (and its
standard library, of course).

```sh
sudo install awaawaa.py /usr/local/bin/awaawaa

# [Optional] Install a global configuration file
sudo install -m644 awaawaa.ini /etc/

# [Optional] Install a user-specific configuration file
install -m644 awaawaa.ini ~/.awaawaa.ini

# [Optional] Install the systemd service file (if you use systemd)
sudo install -m644 awaawaa.service /etc/systemd/system/
```

**awaawaa** tries to read configuration from these files (with the late
overriding the early):

- `/etc/awaawaa.ini`
- `~/.awaawaa.ini`


## Usage

### As a normal user

You can just run `awaawaa` (or `awaawaa &` to daemonize it).  **awaawaa**
completely ignores command-line arguments.

To reload configuration at runtime, send a SIGHUP to the **awaawaa** process.

```sh
kill -HUP $(cat /run/user/$USER/awaawaa.pid)
```

### As a systemd service (recommended)

You can use the provided *systemd* service to start/stop **awaawaa**, and make
it start automatically at boot.

```sh
# Enable and start the awaawaa service
sudo systemctl enable --now awaawaa.service

# Reload configuration at runtime
sudo systemctl reload awaawaa.service
```

