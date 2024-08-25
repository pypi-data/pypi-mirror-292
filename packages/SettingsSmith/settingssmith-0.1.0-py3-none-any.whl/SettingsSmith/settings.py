import os
import json
from types import NoneType
import appdirs


class Settings:
    def __init__(
        self,
        default_settings: dict | str,
        app_name: str,
        app_version: str,
        config_dir: str | None = None,
        overwrite: bool = False,
        load_previous_version: bool = True,
    ):
        """Main settings class to manage settings for an application. It will load the
        settings from the last version of the application if it exists. If the settings
        file does not exist, it will create it with the default settings provided. If
        the overwrite flag is set to True, it will overwrite the settings file with the
        default settings provided.

        Args:
            default_settings (dict | str): dictionary of settings or file path to json file containing a dict of settings
            app_name (str): application version
            app_version (str): aaplication version
            config_dir (str | None, optional): overwrite the default settings directory. Defaults to None.
            overwrite (bool, optional): whether to overwrite the existing settings file. Defaults to False.
            load_previous_version (bool, optional): wether to attempt to bring settings over from previous app version. Defaults to True.
        """
        self.app_name = app_name
        self.app_version = app_version

        self.config_dir = (
            config_dir
            if config_dir is not None
            else appdirs.user_config_dir(app_name, app_version)
        )
        self.config_file = os.path.join(self.config_dir, "settings.json")

        if isinstance(default_settings, str):
            with open(default_settings, "r") as f:
                default_settings = json.load(f)

        if overwrite:
            self.settings = default_settings
            self._save()
        else:
            self.settings = default_settings
            self._load(load_previous_version)

    def get(self, *keys):
        """Returns the setting for the specified keys. If no keys are provided, it will
        return all settings. Multiple keys are provided to handle nested settings."""
        if keys:
            value = self.settings
            for key in keys:
                value = value[key]
            return value
        else:
            return self.settings

    def set(self, value, *keys):
        """Sets the value for the specified keys. Multiple keys are provided to handle
        nested settings."""
        if keys:
            setting = self.settings
            for key in keys[:-1]:
                setting = setting.setdefault(key, {})
            setting[keys[-1]] = value
        else:
            self.settings = value
        self._save()

    def delete(self, *keys):
        """Deletes the setting for the specified keys. Multiple keys are provided to
        handle nested settings."""
        if keys:
            setting = self.settings
            for key in keys[:-1]:
                setting = setting[key]
            del setting[keys[-1]]
        else:
            self.settings = {}
        self._save()

    def _save(self):
        os.makedirs(self.config_dir, exist_ok=True)
        with open(self.config_file, "w") as f:
            json.dump(self.settings, f, indent=4)

    def _load(self, load_previous_version: bool):
        if os.path.exists(self.config_file):
            with open(self.config_file, "r") as f:
                self.settings = json.load(f)
        if load_previous_version:
            previous_settings = None
            previous_settings_files = []
            for root, dirs, files in os.walk(os.path.dirname(self.config_dir)):
                for file in files:
                    if file == "settings.json":
                        previous_settings_files.append(os.path.join(root, file))
            if previous_settings_files:
                previous_settings_files.sort()
                with open(previous_settings_files[-1], "r") as f:
                    previous_settings = json.load(f)

            if previous_settings:
                for key in self.settings:
                    if key in previous_settings:
                        self.settings[key] = previous_settings[key]
        self._save()
