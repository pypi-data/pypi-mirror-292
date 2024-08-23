# Akamai Network Lists


## Development

This project is using [hatch](https://hatch.pypa.io/latest/) as it's build system. For this reason I also used it to manage the development environment. The following commands can be used to create and activate a virtual environment. Alternatively you're free to use the Python `venv` module.

You may need to [install](https://hatch.pypa.io/latest/install/) `hatch` (`pip install hatch`)

```bash
hatch env create
hatch shell
```


The main "binary" is located in `bin/akamai-network-lists.py`. The reason is because the akamai-cli tool has it's own format a python module must adhere to. It [looks for files](https://github.com/akamai/cli/blob/20c6521bfe3cb129bc5a41c81e206bba27e40efd/pkg/commands/command.go#L372) under the `bin` directory that [match the pattern](https://github.com/akamai/cli/blob/20c6521bfe3cb129bc5a41c81e206bba27e40efd/pkg/commands/command.go#L286) of `akamai-command-name`.

We also [need to list our dependencies](https://github.com/akamai/cli/blob/20c6521bfe3cb129bc5a41c81e206bba27e40efd/pkg/packages/python.go#L128) in a `requirements.txt` file, as we are using `pyproject.toml` to define our build system requirements and dependencies, this means we can solely include `.` in `requirements.txt` and this module will be installed.

There is some information in the [README.md](https://github.com/akamai/cli/blob/20c6521bfe3cb129bc5a41c81e206bba27e40efd/README.md#command-package-metadata) for akamai-cli, but a lot of the specifics seem un-written..

## Build

```bash
python3 -m pip install --upgrade build
python3 -m pip install --upgrade twine

python3 -m build
python3 -m twine upload dist/*
```


## Install in akamai-cli

```bash
# i'm using ubuntu 22.04 and there's an issue with the default python pip package
# for that reason i need to use a later version of python that the akamai-cli
# can use, the following three lines may not be necessary on any other configuration
python3.11 -m venv test_venv
source test_venv/bin/activate
PYTHONUSERBASE="test_venv/lib/python3.11/site-packages"

akamai install https://github.com/ryanlinnit-sky/akamai-cli-network-lists.git

akamai network-lists
```
