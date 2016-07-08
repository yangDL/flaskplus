# -*- coding: utf-8 -*-

import sys
import time
import json
import logging
import datetime
import traceback

import redis

from flask import Flask, jsonify, request, Response, make_response

from logging.handlers import RotatingFileHandler

import flaskplus.db_utils as db_utils
import flaskplus.config as config
import flaskplus.httpstat as httpstat
from flaskplus.error import *


class MyResponse(Response):
    @classmethod
    def force_type(cls, rv, environ=None):
        if isinstance(rv, list) or isinstance(rv, dict):
            rv = {'data': rv, 'code': ERR_SUCCESS, 'msg': ''}
        elif isinstance(rv, Response):
            return rv
        elif isinstance(rv, APIError):
            rv = rv.to_dict()
        else:
            rv = {'data': {}, 'code': ERR_INNER_SVR, 'msg': '内部错误:%s' % str(rv)}

        rv = jsonify(rv)
        resp = super(MyResponse, cls).force_type(rv, environ)
        resp.headers['Content-Type'] = 'application/json; charset=utf-8'
        return resp

class FlaskPlus(Flask):
    static_path = None

    def __init__(self, name):
        Flask.__init__(self, name)
        self.response_class = MyResponse

        self._setup_hooks()

        # 注意这里的初始化顺序!
        self._init_stat()
        self._init_config()
        self._init_log()
        self._init_redis()
        self._init_db()

        logging.info('API开始服务请求')

    def _setup_hooks(self):
        self.register_error_handler(APIError, self.base_error_handler)
        self.register_error_handler(Exception, self.generic_exception_handler)
        self.before_first_request(self.before_first_handler)
        self.before_request(self.before_handler)
        self.after_request(self.after_handler)
        self.teardown_request(self.teardown_handler)

        health_url = '/%s/health' % self.name
        self.add_url_rule(health_url, 'health', self.on_health)
        return

    def on_health(self):
        return self.stat.dump()

    def _init_stat(self):
        httpstat.init_stat()
        self.stat = httpstat.get_stat()

    def _init_log(self):
        log_level_map = {'debug': logging.DEBUG, 'info': logging.INFO, 'warn': logging.WARN,
                         'error': logging.ERROR, 'fatal': logging.FATAL}

        log_path = self.cfg.get_str('log', 'path')
        log_level = self.cfg.get_str('log', 'level')

        file_handler = RotatingFileHandler('%s/%s.log' % (log_path, self.name), maxBytes=1024*1024*100, backupCount=20)
        formatter = logging.Formatter("%(asctime)s %(filename)s %(funcName)s:%(lineno)s [%(levelname)s] %(message)s")
        file_handler.setFormatter(formatter)

        logger = logging.getLogger()
        logger.addHandler(file_handler)
        logger.setLevel(log_level_map.get(log_level.lower(), logging.INFO))
        logging.info('初始化日志成功')

    def base_error_handler(self, e):
        return e.to_dict()

    def generic_exception_handler(self, e):
        logging.error('服务器抛出异常: %s[%s]' % (str(e), traceback.format_exc()))
        return APIError(ERR_INNER_SVR, '服务器内部错误: %s' % str(e))

    def _init_config(self):
        try:
            config.init_cfg('./conf/sys.ini')
            self.cfg = config.get_cfg()
        except Exception as e:
            logging.error('初始化config失败，程序直接退出。')
            sys.exit(-1)

        assert self.cfg is not None
        logging.info('初始化配置文件成功')

    def _init_redis(self):
        try:
            red_ip = self.cfg.get_str('redis', 'ip')
            red_port = self.cfg.get_int('redis', 'port')
            db_utils.init_redis(red_ip, red_port)
        except Exception as e:
            logging.error('初始化redis失败，程序直接退出。')
            sys.exit(-1)

        self.redis = db_utils.get_redis()
        assert self.redis is not None
        logging.info('初始化redis成功')

    def _init_db(self):
        try:
            db_host = self.cfg.get_str('mysql', 'ip')
            db_port = self.cfg.get_int('mysql', 'port')
            db_usr = self.cfg.get_str('mysql', 'user')
            db_pwd = self.cfg.get_str('mysql', 'passwd')
            db_name = self.cfg.get_str('mysql', 'dbname')
            db_utils.init_db(db_host, db_port, db_usr, db_pwd, db_name)
        except Exception as e:
            logging.error('初始化mysql失败，程序直接退出。exception: [%s]' % str(e))
            sys.exit(-1)

        self.db = db_utils.get_db()
        assert self.db is not None
        logging.info('初始化mysql成功')

    def before_first_handler(self):
        return

    def before_handler(self):
        """解密、认证、过载保护、防刷
        """
        return

    def after_handler(self, response):
        data = response.data.decode('utf-8')
        if not data:
            return response
        try:
            jdata = json.loads(data)
        except:
            return response

        code = jdata.get('code', 0)
        if code == 0:
            self.stat.incr_succ()
        elif code < 0:
            self.stat.incr_sys_err()
        else:
            self.stat.incr_logic_err()
        return response

    def teardown_handler(self, exc):
        """ 统计、加密、日志
        """
        return


def make_error(code, msg):
    return jsonify({'code': code, 'msg': msg, 'data': {}})
