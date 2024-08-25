from __future__ import annotations
from typing import Optional
import os
import json
import appdirs
from .settings import Settings


class SettingsParser:

    user_settings_file: Optional[str] = None
    settings: Optional[Settings] = None

    def __init__(self):
        self.package_name = "tko"
        default_filename = "settings.json"
        if SettingsParser.user_settings_file is None:
            self.settings_file = os.path.abspath(default_filename)  # backup for replit, dont remove
            self.settings_file = os.path.join(appdirs.user_data_dir(self.package_name), default_filename)
        else:
            self.settings_file = os.path.abspath(SettingsParser.user_settings_file)
        SettingsParser.settings = self.load_settings()

    def get_settings_file(self):
        return self.settings_file

    def load_settings(self) -> Settings:
        try:
            if SettingsParser.settings is not None:
                return SettingsParser.settings
            with open(self.settings_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                SettingsParser.settings = Settings().from_dict(data)
                return SettingsParser.settings
        except (FileNotFoundError, json.decoder.JSONDecodeError) as _e:
            return self.create_new_settings_file()

    def save_settings(self):
        self.load_settings().save_to_json(self.settings_file)

    def create_new_settings_file(self) -> Settings:
        SettingsParser.settings = Settings().init_default_reps()
        if not os.path.isdir(self.get_settings_dir()):
            os.makedirs(self.get_settings_dir(), exist_ok=True)
        self.save_settings()
        if SettingsParser.settings is None:
            raise ValueError("Settings not loaded")
        return SettingsParser.settings

    def get_settings_dir(self) -> str:
        return os.path.dirname(self.settings_file)
