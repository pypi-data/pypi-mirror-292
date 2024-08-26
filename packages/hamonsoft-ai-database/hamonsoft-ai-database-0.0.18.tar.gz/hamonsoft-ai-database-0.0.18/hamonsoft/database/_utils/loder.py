# -*- coding: utf-8 -*-

import configparser


class ConfigLoader:
    config = configparser.RawConfigParser()

    @staticmethod
    def load(config_file):
        ConfigLoader.config.optionxform = str
        ConfigLoader.config.read(config_file)
