import logging
from typing import Optional
from dataclasses import dataclass

class Config:
    _instance = None
    _config = None

    def __new__(cls, config_file_path: str = "config.yml"):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            if config_file_path is not None:
                cls._load_config(config_file_path)
        return cls._instance._config

    @classmethod
    def _load_config(cls, config_file_path: str):
        from yacs.config import CfgNode as CN
        cfg = CN()
        cfg.set_new_allowed(True)
        cfg.merge_from_file(config_file_path)
        cls._config = cfg

    @classmethod
    def get_config(cls):
        if cls._config is None:
            raise ValueError("Config has not been loaded. Please initialize ConfigSingleton with a config file path.")
        return cls._config


@dataclass
class LoggingConfig:
    logger_level: int = logging.DEBUG
    console_log_level: int = logging.INFO
    file_log_level: Optional[int] = logging.DEBUG
    file_log_name: Optional[str] = "./logs/debug.log"
    logging_format: str = "[%(asctime)s] %(name)s:%(levelname)s - %(message)s"

cfg = Config()
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', 
                    filename=cfg.log_file_path)
