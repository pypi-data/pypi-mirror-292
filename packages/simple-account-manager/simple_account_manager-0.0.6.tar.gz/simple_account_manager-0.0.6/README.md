# Simple Account Manager

[![Pylint](https://github.com/huangyunict/simple_account_manager/actions/workflows/pylint.yml/badge.svg)](https://github.com/huangyunict/simple_account_manager/actions/workflows/pylint.yml)
[![Python application](https://github.com/huangyunict/simple_account_manager/actions/workflows/python-app.yml/badge.svg)](https://github.com/huangyunict/simple_account_manager/actions/workflows/python-app.yml)
[![Upload Python Package](https://github.com/huangyunict/simple_account_manager/actions/workflows/python-publish.yml/badge.svg)](https://github.com/huangyunict/simple_account_manager/actions/workflows/python-publish.yml)

Simple Account Manager is a simple account manager library written in Python.
It provides a clean library interface to manager accounts with secured
username and password. The main design goal is **simple**, with simple file
format and minimal dependencies.

## Master key file format

The master key could be directly passed by the `master_key` parameter when
creating the `Manager` object.

A better way is to store the master key in the master key file, and pass
the file path as the `master_file` parameter. The default master key file
is `~/.simple_account_manager/master_key.cfg`.

The master key file is in Python's config format and parsed by the
[configparser](https://docs.python.org/3/library/configparser.html) library.
Example content:

```cfg
[metadata]
version = 1.0

[encryption]
master_key = ExamplePassword
```

## JSON file format

The plain JSON example: [example.plain.json](docs/example.plain.json).

The JSON example with encrypted password: [example.encrypted.json](docs/example.encrypted.json).
