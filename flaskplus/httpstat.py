# -*- coding: utf-8 -*-


class HTTPStat:
    def __init__(self):
        self.req_total = 0
        self.req_success = 0
        self.req_logic_err = 0
        self.req_sys_err = 0

    def incr_succ(self):
        self.req_total += 1
        self.req_success += 1

    def incr_logic_err(self):
        self.req_total += 1
        self.req_logic_err += 1

    def incr_sys_err(self):
        self.req_total += 1
        self.req_sys_err += 1

    def dump(self):
        data = {}
        data['req.total'] = self.req_total
        data['req.success'] = self.req_success
        data['req.logic.error'] = self.req_logic_err
        data['req.sys.error'] = self.req_sys_err
        return data



g_stat = None

def init_stat():
    global g_stat
    g_stat = HTTPStat()


def get_stat():
    return g_stat
