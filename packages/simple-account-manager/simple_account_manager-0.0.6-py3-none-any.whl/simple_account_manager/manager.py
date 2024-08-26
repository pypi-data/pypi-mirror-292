"""Module that defines the main class Manager."""

from base64 import b64encode
import configparser
from dataclasses import asdict
import hashlib
import json
from pathlib import Path

from cryptography.fernet import Fernet

from src.simple_account_manager.account import Account


class Manager:
    """The account manager class.

    Args:
        master_key (str): The master key. If given, override master_file.
        master_file (Path): The file to read master key from, in Python
            config format. If not given, default to
            `$HOME/.simple_account_manager/master_key.cfg`.
    """

    def __init__(self, master_key: str = None, master_file: Path = None):
        self._version = '1.0'
        self._accounts = []
        if master_key is None:
            if master_file is None:
                master_file = Path.home(
                ) / '.simple_account_manager' / 'master_key.cfg'
            master_key = Manager._load_master_key(master_file)
        self._fernet = self._get_fernet(master_key)

    @property
    def version(self) -> str:
        """The version property."""

        return self._version

    @property
    def accounts(self) -> list[Account]:
        """The accounts property."""

        return self._accounts

    def save_json(self,
                  json_path: Path,
                  encrypt_username=False,
                  encrypt_password=True):
        """Save accounts to json file with encryption."""

        doc = {'accounts': {'version': self.version, 'data': []}}
        for account in self._accounts:
            d = asdict(
                account,
                dict_factory=lambda x: {k: v
                                        for (k, v) in x if v is not None})
            if encrypt_username:
                d['encrypted_username'] = self._encrypt(d['username'])
                del d['username']
            if encrypt_password:
                d['encrypted_password'] = self._encrypt(d['password'])
                del d['password']
            doc['accounts']['data'].append(d)
        with open(json_path, 'w', encoding='UTF-8') as fp:
            json.dump(doc, fp)

    def load_json(self, json_path: Path):
        """Load json file with encrypted fields to accounts."""

        accounts = []
        with open(json_path, 'r', encoding='UTF-8') as fp:
            doc = json.load(fp)
        version = doc['accounts']['version']
        for d in doc['accounts']['data']:
            username = d.get('username')
            if username is None:
                username = self._decrypt(d['encrypted_username'])
            password = d.get('password')
            if password is None:
                password = self._decrypt(d['encrypted_password'])
            account = Account(name=d['name'],
                              username=username,
                              password=password,
                              categories=d.get('categories'),
                              domain=d.get('domain'),
                              notes=d.get('notes'))
            accounts.append(account)
        self._version = version
        self._accounts = accounts

    def _encrypt(self, data: str) -> str:
        return self._fernet.encrypt(data.encode('UTF-8')).decode('UTF-8')

    def _decrypt(self, encrypted_data: str) -> str:
        return self._fernet.decrypt(
            encrypted_data.encode('UTF-8')).decode('UTF-8')

    @staticmethod
    def _load_master_key(master_file: Path) -> str:
        config = configparser.ConfigParser()
        with open(master_file, 'r', encoding='UTF-8') as fp:
            config.read_file(fp)
        # read key
        return config['encryption']['master_key'].strip()

    @staticmethod
    def _get_fernet(master_key: str) -> Fernet:
        m = hashlib.sha256()
        m.update(master_key.encode('UTF-8'))
        return Fernet(b64encode((m.hexdigest()[:32]).encode('UTF-8')))
