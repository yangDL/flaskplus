# -*- coding: utf-8 -*-

import redis
import MySQLdb

from flaskplus.error import DBException


class DBUtils:
    def __init__(self, db_host, db_port, db_usr, db_pwd, db_name):
        self.db_host = db_host
        self.db_port = db_port
        self.db_usr = db_usr
        self.db_pwd = db_pwd
        self.db_name = db_name

        self.connect()

    def connect(self):
        try:
            self.db = MySQLdb.connect(host=self.db_host, port=self.db_port, user=self.db_usr, passwd=self.db_pwd,
                                      db=self.db_name, charset='utf8', connect_timeout=3)
        except Exception as e:
            raise e
        assert self.db is not None

    def check_db(self):
        try:
            self.db.ping(True)
        except:
            self.connect()

    def query_exist(self, sql, *args):
        assert sql
        if 'COUNT' not in sql and 'count' not in sql:
            raise DBException('SQL语句不是SELECT COUNT(id)模式')

        row = self.query_single(sql, args)
        assert row
        return row[0] > 0

    def query_single(self, sql, *args):
        """ 执行SQL，返回一行记录，比如select
        """
        assert sql
        try:
            self.check_db()
            self.db.autocommit(True)
            cursor = self.db.cursor()
            cursor.execute(sql, args)
            row = cursor.fetchone()
        except Exception as e:
            raise DBException(sql)
        finally:
            cursor.close()
        return row

    def query_multi(self, sql, *args):
        """ 执行SQL，返回多行记录，比如select
        """
        assert sql
        try:
            self.check_db()
            self.db.autocommit(True)
            cursor = self.db.cursor()
            cursor.execute(sql, args)
            rows = cursor.fetchall()
        except Exception as e:
            raise DBException(sql)
        finally:
            cursor.close()
        return rows


    def insert(self, sql, *args):
        """ 执行INSERT SQL，返回受影响的行数和插入数据的主键
        """
        assert sql
        try:
            self.check_db()
            cursor = self.db.cursor()
            nrows = cursor.execute(sql, args)
            inserted_id = int(self.db.insert_id())
            self.db.commit()
        except Exception as e:
            print(str(e))
            self.db.rollback()
            raise DBError(sql)
        finally:
            cursor.close()
        return nrows, inserted_id


    def execute(self, sql, *args):
        """ 执行SQL，返回受影响的行数，比如insert, update, delete语句
        """
        assert sql
        try:
            self.check_db()
            cursor = self.db.cursor()
            nrows = cursor.execute(sql, args)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise DBError(sql)
        finally:
            cursor.close()
        return nrows



#MySQL和Redis全局对象
g_db_ins = None
g_redis_ins = None


def init_db(db_host, db_port, db_usr, db_pwd, db_name):
    global g_db_ins
    g_db_ins = DBUtils(db_host, db_port, db_usr, db_pwd, db_name)

def get_db():
    return g_db_ins


def init_redis(redis_ip, redis_port):
    global g_redis_ins
    g_redis_ins = redis.Redis(host=redis_ip, port=redis_port)

def get_redis():
    return g_redis_ins
