from pathlib import Path
from typing import Union

from platformdirs import user_config_dir
from yaml import Dumper, Loader, dump, load

from gradebook_tray.utils.log import get_logger

logger = get_logger(__name__)

class Config:
    def __init__(self, path: Union[str, Path, None] = None):
        if path is None:
            path = Path(user_config_dir("studentvue-tray")) / "config.yml"
        else:
            path = Path(path)

        logger.info(f"Using config file: {path}")

        self._path = path
        if not path.exists():
            self._initialize()
        else:
            self._load()

    def _initialize(self):
        logger.info("Welcome! First time setup")
        self._data = {
            "username": "",
            "password": "",
            "endpoint": "",
            "update_interval": 3600, # 1 hour
            "db_path": Path(user_config_dir("studentvue-tray")) / "data.db",
        }
        self._save()

    def _load(self):
        with open(self._path, "r") as f:
            self._data = load(f, Loader=Loader)

    def _save(self):
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._path, "w") as f:
            dump(self._data, f, Dumper=Dumper)

    def __getitem__(self, key: str):
        try:
            return self._data[key]
        except KeyError:
            raise ValueError(f"Key {key} not found in config file")

    def __setitem__(self, key: str, value):
        self._data[key] = value
        self._save()

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return iter(self._data)


config = Config()
