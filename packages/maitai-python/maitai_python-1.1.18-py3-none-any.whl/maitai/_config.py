import json
import os
import threading
from typing import List

import requests
from betterproto import Casing
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from maitai._config_listener_thread import ConfigListenerThread
from maitai._utils import __version__ as version
from maitai_common.config import config_service
from maitai_gen.application import Application
from maitai_gen.config import Config as ActionConfig
from maitai_gen.key import Key, KeyMap


class Config:
    maitai_host = os.environ.get("MAITAI_HOST", 'https://api.trymaitai.ai')
    maitai_host = maitai_host.rstrip('/')
    maitai_ws = os.environ.get("MAITAI_WS", 'wss://09hidyy627.execute-api.us-west-2.amazonaws.com/production')

    def __init__(self):
        retry_strategy = Retry(
            total=3,
            backoff_factor=1
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)

        self._session = requests.Session()
        self._session.mount("http://", adapter)
        self._session.mount("https://", adapter)

        self._api_key = None
        self._applications: dict[str, Application] = {}
        self._company_id = None
        self.websocket_listener_thread = None
        self.config_listener_thread = None
        self._application_action_configs: dict[str, dict[str, ActionConfig]] = {}
        self.initialized = False
        self.auth_keys: KeyMap = KeyMap(
            openai_api_key=Key(id=-1, key_value=os.environ.get("OPENAI_API_KEY")),
            groq_api_key=Key(id=-1, key_value=os.environ.get("GROQ_API_KEY")),
            anthropic_api_key=Key(id=-1, key_value=os.environ.get("ANTHROPIC_API_KEY")),
        )

    @property
    def api_key(self):
        if self._api_key is None:
            if self.initialized:
                raise ValueError("Maitai API Key has not been set. Either pass it directly into the client, or by setting the environment variable MAITAI_API_KEY.")
            else:
                api_key = os.environ.get("MAITAI_API_KEY")
                if not api_key:
                    raise ValueError("Maitai API Key has not been set. Either pass it directly into the client, or by setting the environment variable MAITAI_API_KEY.")
                self.initialize(api_key=api_key)
        return self._api_key

    @api_key.setter
    def api_key(self, value):
        self._api_key = value

    def initialize(self, api_key, retry=0):
        if self.initialized and self.api_key == api_key:
            return
        self.api_key = api_key
        self.initialized = True
        try:
            self._initialize_company()
            self.refresh_applications()
            self._initialize_websocket()
        except Exception as e:
            try:
                self._load_config_from_file()
            except Exception:
                raise e
            self.initialized = False
            if retry < 5:
                t = threading.Timer(interval=2 ** retry, function=self.initialize, args=(api_key, retry))
                t.daemon = True
                t.start()

    def get_application(self, application_ref_name: str) -> Application:
        return self._applications.get(application_ref_name)

    def get_application_action_config(self, application_ref_name: str, action_type: str) -> ActionConfig:
        return self._application_action_configs.get(application_ref_name, {}).get(action_type, config_service.get_default_config())

    def _initialize_company(self):
        host = self.maitai_host
        url = f'{host}/company/'
        headers = {
            'Content-Type': 'application/json',
            'x-api-key': self.api_key,
            'x-client-version': version,
        }

        response = self._session.get(url, headers=headers, timeout=15)
        self._session.close()
        if response.status_code != 200:
            raise Exception(f"Failed to initialize Maitai client: {response.text}")

        self._company_id = response.json().get("id")

    def refresh_applications(self):
        host = self.maitai_host
        url = f'{host}/application/'
        headers = {
            'Content-Type': 'application/json',
            'x-api-key': self.api_key,
            'x-client-version': version,
        }

        response = self._session.get(url, headers=headers, timeout=15)
        self._session.close()
        if response.status_code != 200:
            raise Exception(f"Failed to initialize Maitai client: {response.text}")
        applications = [Application().from_dict(app_json) for app_json in response.json()]
        return self.store_application_metadata(applications)

    def store_application_metadata(self, applications: List[Application]):
        for application in applications:
            self._applications[application.application_ref_name] = application
            for action_type in application.action_types:
                if application.application_ref_name not in self._application_action_configs:
                    self._application_action_configs[application.application_ref_name] = {}
                self._application_action_configs[application.application_ref_name][action_type.action_type] = action_type.meta
        self._dump_application_metadata()

    def _dump_application_metadata(self):
        filename = os.path.expanduser("~/.maitai/config.json")
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w") as f:
            config_object = {}
            for ref_name, intent_map in self._application_action_configs.items():
                config_object[ref_name] = {}
                for intent_name, intent_config in intent_map.items():
                    config_object[ref_name][intent_name] = intent_config.to_pydict(casing=Casing.SNAKE, include_default_values=False)
            f.write(json.dumps(config_object, indent=2))

    def _load_config_from_file(self):
        filename = os.path.expanduser("~/.maitai/config.json")
        with open(filename, "r") as f:
            config_object = json.load(f)
            for ref_name, intent_map in config_object.items():
                if ref_name not in self._application_action_configs:
                    self._application_action_configs[ref_name] = {}
                for intent_name, intent_config in intent_map.items():
                    self._application_action_configs[ref_name][intent_name] = ActionConfig().from_pydict(intent_config)

    def _initialize_websocket(self):
        self.config_listener_thread = ConfigListenerThread(self, self.maitai_ws, "APPLICATION_CONFIG_CHANGE", self._company_id)
        self.config_listener_thread.daemon = True
        self.config_listener_thread.start()

    def cleanup(self):
        if self.config_listener_thread:
            self.config_listener_thread.terminate()
            self.config_listener_thread = None


config = Config()

import atexit

atexit.register(config.cleanup)
