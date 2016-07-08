# -*- coding: utf-8 -*-

from configparser import ConfigParser, NoSectionError, NoOptionError

from flaskplus.error import ConfigException


class Config:
    def __init__(self, *filenames):
        self.cfg = ConfigParser()
        try:
            for filename in filenames:
                self.cfg.read(filename)
        except Exception as e:
            raise ConfigException('加载配置文件[%s]错误' % filename)

    def get_str(self, section, key):
        try:
            return self.cfg.get(section, key)
        except NoSectionError:
            raise ConfigException('无配置项[%s]' % (section))
        except NoOptionError:
            raise ConfigException('无配置项[%s][%s]' % (section, key))

    def get_int(self, section, key):
        try:
            return int(self.cfg.get(section, key))
        except NoSectionError:
            raise ConfigException('无配置项[%s]' % (section))
        except NoOptionError:
            raise ConfigException('无配置项[%s][%s]' % (section, key))
        except ValueError:
            raise ConfigException('配置项[%s][%s]类型不是整数' % (section, key))


g_cfg = None

def init_cfg(*filename):
    global g_cfg
    g_cfg = Config(*filename)

def get_cfg():
    return g_cfg
