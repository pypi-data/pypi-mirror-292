#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pathlib
import toml
import dacite
from logflex.models.config_model import Configuration, GeneralSettings, FileHandlerSettings, SyslogHandlerSettings, ColorSettings


FACILITY_MAP = {
    "LOG_KERN": 0,
    "LOG_USER": 1,
    "LOG_MAIL": 2,
    "LOG_DAEMON": 3,
    "LOG_AUTH": 4,
    "LOG_SYSLOG": 5,
    "LOG_LPR": 6,
    "LOG_NEWS": 7,
    "LOG_UUCP": 8,
    "LOG_CRON": 9,
    "LOG_AUTHPRIV": 10,
    "LOG_FTP": 11,
    "LOG_LOCAL0": 16,
    "LOG_LOCAL1": 17,
    "LOG_LOCAL2": 18,
    "LOG_LOCAL3": 19,
    "LOG_LOCAL4": 20,
    "LOG_LOCAL5": 21,
    "LOG_LOCAL6": 22,
    "LOG_LOCAL7": 23,
}


class ConfigLoader:
    def __init__(self, config_path=None):
        self.config_path = pathlib.Path(config_path or (os.getcwd() + '/config.toml'))
        self.config = self._load_config()

    def _load_config(self) -> Configuration:
        if self.config_path.exists():
            return self._load_config_from_file()
        else:
            return self._load_config_from_env()

    def _load_config_from_file(self) -> Configuration:
        raw_config = toml.load(self.config_path)
        return dacite.from_dict(data_class=Configuration, data=raw_config, config=dacite.Config(strict=True))

    def _load_config_from_env(self) -> Configuration:
        def get_env_value(cls, field):
            key = cls.env_keys().get(field)
            if isinstance(key, dict):
                return {k: os.getenv(v) for k, v in key.items()}
            return os.getenv(key)

        general_settings = GeneralSettings(
            log_level=get_env_value(GeneralSettings, 'log_level'),
            verbose=get_env_value(GeneralSettings, 'verbose') in ('true', '1', 't'),
            trace=get_env_value(GeneralSettings, 'trace') in ('true', '1', 't'),
            color_settings=ColorSettings(
                enable_color=get_env_value(GeneralSettings, 'color_settings')['enable_color'] in ('true', '1', 't'),
                datefmt=get_env_value(GeneralSettings, 'color_settings')['datefmt'],
                reset=get_env_value(GeneralSettings, 'color_settings')['reset'] in ('true', '1', 't'),
                log_colors={
                    'DEBUG': get_env_value(GeneralSettings, 'color_settings')['log_colors']['DEBUG'],
                    'INFO': get_env_value(GeneralSettings, 'color_settings')['log_colors']['INFO'],
                    'WARNING': get_env_value(GeneralSettings, 'color_settings')['log_colors']['WARNING'],
                    'ERROR': get_env_value(GeneralSettings, 'color_settings')['log_colors']['ERROR'],
                    'CRITICAL': get_env_value(GeneralSettings, 'color_settings')['log_colors']['CRITICAL'],
                },
                style=get_env_value(GeneralSettings, 'color_settings')['style']
            )
        )

        file_handler_settings = FileHandlerSettings(
            logdir=get_env_value(FileHandlerSettings, 'logdir'),
            logfile=get_env_value(FileHandlerSettings, 'logfile'),
            when=get_env_value(FileHandlerSettings, 'when'),
            interval=int(get_env_value(FileHandlerSettings, 'interval', '1')),
            backup_count=int(get_env_value(FileHandlerSettings, 'backup_count', '7')),
            dedicate_error_logfile=get_env_value(FileHandlerSettings, 'dedicate_error_logfile')
        )

        syslog_handler_settings = SyslogHandlerSettings(
            use_syslog=get_env_value(SyslogHandlerSettings, 'use_syslog') in ('true', '1', 't'),
            syslog_address=get_env_value(SyslogHandlerSettings, 'syslog_address', 'localhost'),
            syslog_port=int(get_env_value(SyslogHandlerSettings, 'syslog_port', '514'))
        )

        return Configuration(
            general=general_settings,
            file_handler=file_handler_settings,
            syslog_handler=syslog_handler_settings
        )

class ConfigBuilder:
    @staticmethod
    def _generate_default_config() -> dict:
        default_config = {}
        for cls in [GeneralSettings, FileHandlerSettings, SyslogHandlerSettings]:
            for field in cls.__dataclass_fields__:
                default_value = ConfigBuilder._get_default_value(cls, field)
                if default_value is not None:
                    default_config[field] = default_value
        return default_config

    @staticmethod
    def _get_default_value(cls, field: str):
        default_value = getattr(cls(), field, None)
        if isinstance(default_value, dict):
            return {}
        return default_value

    @staticmethod
    def build_config(**kwargs) -> Configuration:
        default_config = ConfigBuilder._generate_default_config()

        config_kwargs = {**default_config, **kwargs}

        general_settings = ConfigBuilder._create_general_settings(config_kwargs)
        file_handler_settings = ConfigBuilder._create_file_handler_settings(config_kwargs)
        syslog_handler_settings = ConfigBuilder._create_syslog_handler_settings(config_kwargs)

        return Configuration(
            general=general_settings,
            file_handler=file_handler_settings,
            syslog_handler=syslog_handler_settings
        )

    @staticmethod
    def _create_general_settings(config_kwargs) -> GeneralSettings:
        return GeneralSettings(
            log_level=config_kwargs.get('log_level', 'INFO'),
            verbose=config_kwargs.get('verbose', False),
            trace=config_kwargs.get('trace', False),
            color_settings=ColorSettings(
                enable_color=config_kwargs.get('color_enable', True),
                datefmt=config_kwargs.get('color_datefmt', None),
                reset=config_kwargs.get('color_reset', True),
                log_colors=config_kwargs.get('color_log_colors', {
                    'DEBUG': 'cyan',
                    'INFO': 'green',
                    'WARNING': 'yellow',
                    'ERROR': 'red',
                    'CRITICAL': 'red,bg_white'
                }),
                secondary_log_colors={},
                style=config_kwargs.get('color_style', '%')
            )
        )

    @staticmethod
    def _create_file_handler_settings(config_kwargs) -> FileHandlerSettings:
        return FileHandlerSettings(
            logdir=config_kwargs.get('file_logdir', None),
            logfile=config_kwargs.get('file_logfile', None),
            when=config_kwargs.get('file_when', 'midnight'),
            interval=config_kwargs.get('file_interval', 1),
            backup_count=config_kwargs.get('file_backup_count', 7),
            dedicate_error_logfile=config_kwargs.get('file_dedicate_error_logfile', None)
        )

    @staticmethod
    def _create_syslog_handler_settings(config_kwargs) -> SyslogHandlerSettings:
        return SyslogHandlerSettings(
            use_syslog=config_kwargs.get('use_syslog', False),
            syslog_address=config_kwargs.get('syslog_address', 'localhost'),
            syslog_port=config_kwargs.get('syslog_port', 514),
            syslog_facility=config_kwargs.get('syslog_facility', 'LOG_USER')
        )
