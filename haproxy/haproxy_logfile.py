# -*- coding: utf-8 -*-
from haproxy.haproxy_logline import HaproxyLogLine


class HaproxyLogFile(object):

    @classmethod
    def commands(cls):
        """Returns a list of all methods that start with cmd_"""
        cmds = [cmd[4:] for cmd in dir(cls) if cmd.startswith('cmd_')]
        return cmds

    def cmd_counter(self):
        pass

    def cmd_http_methods(self):
        pass
