from json import dump

from PyQt6.QtCore import QObject

from src.LogicConfig.load_conf_file import load_conf_file


class LogicConfig(QObject):
    """

    This clas is responsible to deal with the config file.
    It loads and validates the config file in json format.
    """

    def __init__(self, program_path, update_language_callback, update_channel_callback):

        super().__init__()

        self._file_path = f"{program_path}/conf.json"

        self._update_language_callback = update_language_callback
        self._update_channel_callback = update_channel_callback

        self.config = dict()

        self.load()

    def load(self):
        """Loads initial conf file. It will create one if it does not exist"""

        self.config = load_conf_file(self._file_path)

    def update(self, new_json):
        """Updates conf file saving it to json and reloading it"""

        with open(self._file_path, "w") as json_file:
            dump(new_json, json_file, indent=4)

        # We will reload using function so we can validate new configs
        new_config = load_conf_file(self._file_path)

        if new_config["language"] != self.config["language"]:
            self._update_language_callback(new_config["language"])

        if new_config["channel"] != self.config["channel"]:
            self._update_channel_callback(new_config["channel"])

        self.config = new_config

    @property
    def language(self):
        return self.config["language"]

    @property
    def channel(self):
        return self.config["channel"]

    @property
    def shop(self):
        return self.config["shop"]

    @property
    def catch(self):
        return self.config["catch"]

    @property
    def stats_balls(self):
        return self.config["stats_balls"]
