# yhttp-dev

A set of development and test fixtures for `yhttp` application development.


## Contribution

### Dependencies
Install `postgresql` brefore use of this project.
```bash
apt install postgresql
```

### Prepare

Create and grant the `postgresql` role with `createdb` permission to 
authenticate the current `unix` user within `postgresql` using the peer 
authentication.
```bash
echo "CREATE USER ${USER} WITH CREATEDB" | sudo -u postgres psql
# Or
echo "ALTER USER ${USER} CREATEDB" | sudo -u postgres psql
```

### Virtualenv

Create virtual environment:
```bash
make venv
```

Delete virtual environment:
```bash
make venv-delete
```

Activate the virtual environment:
```bash
source ./activate.sh
```


### Install (editable mode)
Install this project as editable mode and all other development dependencies:
```bash
make env
```

# Lint
```bash
make lint
```


### Distribution
Execute these commands to create `Python`'s standard distribution packages
at `dist` directory:
```bash
make sdist
make wheel
```

Or 
```bash
make dist
```
to create both `sdidst` and `wheel` packages.


### Clean build directory
Execute: 
```bash
make clean
```
to clean-up previous `dist/*` and `build/*` directories.


### PyPI

> **_WARNING:_** Do not do this if you'r not responsible as author and 
> or maintainer of this project.

Execute
```bash
make clean
make pypi
```
to upload `sdists` and `wheel` packages on [PyPI](https://pypi.org).
