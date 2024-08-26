"""Test module for the class Manager."""
import configparser
import json
from pathlib import Path

from src.simple_account_manager.account import Account
from src.simple_account_manager.manager import Manager


class TestManager:
    """Tests for the class Manager."""

    def test_new_manager_with_defaults(self):
        """Test for creating a new Manager object with defaults."""

        manager = Manager(master_key=TestManager._example_master_key)

        # Verify accounts.
        assert len(manager.accounts) == 0

    def test_manager_load_plain_json_with_master_file(self, tmp_path: Path):
        """Test for creating manager by loading json file and comparing the contents."""

        # Prepare master file.
        master_file = tmp_path / 'master.cfg'
        config = configparser.ConfigParser()
        config['metadata'] = {'version': '1.0'}
        config['encryption'] = {'master_key': TestManager._example_master_key}
        with open(master_file, 'w', encoding='UTF-8') as fp:
            config.write(fp)

        # Prepare json.
        foo_json_path = tmp_path / 'foo.json'
        with open(foo_json_path, 'w', encoding='UTF-8') as fp:
            json.dump(TestManager._example_json, fp)

        # Create account manager from the json file.
        manager = Manager(master_file=master_file)
        manager.load_json(foo_json_path)

        # Verify accounts.
        assert len(manager.accounts) == len(TestManager._example_accounts)
        assert manager.accounts == TestManager._example_accounts

    def test_manager_load_plain_json_with_master_key(self, tmp_path: Path):
        """Test for creating manager by loading json file and comparing the contents."""

        # Prepare json.
        foo_json_path = tmp_path / 'foo.json'
        with open(foo_json_path, 'w', encoding='UTF-8') as fp:
            json.dump(TestManager._example_json, fp)

        # Create account manager from the json file.
        manager = Manager(master_key=TestManager._example_master_key)
        manager.load_json(foo_json_path)

        # Verify accounts.
        assert len(manager.accounts) == len(TestManager._example_accounts)
        assert manager.accounts == TestManager._example_accounts

    def test_manager_save_plain_json(self, tmp_path: Path):
        """Test for saving json file by verifying json contents."""

        # Create account manager and append accounts.
        manager = Manager(master_key=TestManager._example_master_key)
        manager.accounts.extend(TestManager._example_accounts)

        # Write json.
        foo_json_path = tmp_path / 'foo.json'
        manager.save_json(foo_json_path,
                          encrypt_username=False,
                          encrypt_password=False)

        # Verify content.
        with open(foo_json_path, 'r', encoding='UTF-8') as fp:
            test_doc = json.load(fp)
        assert test_doc == TestManager._example_json

    def test_manager_encrypt_then_decrypt_json(self, tmp_path: Path):
        """Test for encrypting and decrypting json file."""

        # Create account manager and append accounts.
        old_manager = Manager(master_key=TestManager._example_master_key)
        old_manager.accounts.extend(TestManager._example_accounts)

        # Write json.
        foo_json_path = tmp_path / 'foo.json'
        old_manager.save_json(foo_json_path,
                              encrypt_username=True,
                              encrypt_password=True)

        # Load json.
        new_manager = Manager(master_key=TestManager._example_master_key)
        new_manager.load_json(foo_json_path)

        # Verify content.
        assert new_manager.accounts == old_manager.accounts

    # Example data for testing.
    _example_master_key = 'ExampleMasterKey'
    _example_accounts = [
        Account(name='Chase_A',
                username='user_A',
                password='pass A',
                categories=['web', 'bank'],
                domain='chase.com',
                notes='Chase account A'),
        Account(name='Chase_B',
                username='user_B',
                password='pass B',
                categories=['web', 'bank'],
                domain='chase.com',
                notes='Chase account B'),
        Account(name='Google_C',
                username='user_C',
                password='pass C',
                categories=['email', 'google'],
                domain='gmail.com',
                notes='Google account C'),
        Account(name='Google_D',
                username='user_D',
                password='pass D',
                categories=['email', 'google'],
                domain='gmail.com'),
        Account(name='Meta_E',
                username='user_E',
                password='pass E',
                categories=['social', 'meta'],
                domain='meta.com'),
        Account(name='Twitter_F',
                username='user_F',
                password='pass F',
                categories=['social', 'x'],
                domain='x.com'),
    ]
    _example_json = json.loads("""{
  "accounts": {
    "version": "1.0",
    "data": [
      {
        "name": "Chase_A",
        "username": "user_A",
        "password": "pass A",
        "categories": [
          "web",
          "bank"
        ],
        "domain": "chase.com",
        "notes": "Chase account A"
      },
      {
        "name": "Chase_B",
        "username": "user_B",
        "password": "pass B",
        "categories": [
          "web",
          "bank"
        ],
        "domain": "chase.com",
        "notes": "Chase account B"
      },
      {
        "name": "Google_C",
        "username": "user_C",
        "password": "pass C",
        "categories": [
          "email",
          "google"
        ],
        "domain": "gmail.com",
        "notes": "Google account C"
      },
      {
        "name": "Google_D",
        "username": "user_D",
        "password": "pass D",
        "categories": [
          "email",
          "google"
        ],
        "domain": "gmail.com"
      },
      {
        "name": "Meta_E",
        "username": "user_E",
        "password": "pass E",
        "categories": [
          "social",
          "meta"
        ],
        "domain": "meta.com"
      },
      {
        "name": "Twitter_F",
        "username": "user_F",
        "password": "pass F",
        "categories": [
          "social",
          "x"
        ],
        "domain": "x.com"
      }
    ]
  }
}""")
