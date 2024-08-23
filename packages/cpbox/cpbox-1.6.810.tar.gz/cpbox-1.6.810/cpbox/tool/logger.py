import logging
import logging.handlers
import socket
import os
import json

from cpbox.tool import net
from cpbox.tool import file
from cpbox.tool import timeutil
from cpbox.tool import system

class Holder():

    def __init__(self):
        self.basic_handlers = []
        pass

holder = Holder()

try:
    from threading import get_ident
except ImportError:
    from thread import get_ident

# This is the even log part we want: 2018-11-12T15:34:34+08:00 117.50.2.88 15051.50683 cp mid-call {"fail":0,"service":"id_service.next_id","rt_1":1.1670589447021,"rt":1.1730194091797,"env":"prod"}
# python strftime can not print timezone as +08:00
# logstash grok ISO8601_TIMEZONE will let this go: 2018-11-12T15:36:46+0800 172.16.1.150 28114.139798089959232 $appname test {"env": "dev", "time": "2018-11-12 15:36:46.359019"}
# ${time_iso_8601} ${client_ip} ${pid}.${rnd/thread_id} {$app_name} ${event_key} ${payload_json_encoded}

syslog_full_msg_pre = '%(time_iso_8601)s %(local_ip)s %(app_name)s_event_log[%(pid)d]: '
syslog_client_msg_pre = '%(app_name)s_event_log[%(pid)d]: '
basic_msg_pre = '%(time_iso_8601)s %(local_ip)s %(pid)d.%(tid)d '

readable_format = basic_msg_pre + '%(levelname)s %(name)s@%(filename)s:%(lineno)d %(message)s'

event_log_by_filelog_format = syslog_full_msg_pre + basic_msg_pre + '%(message)s'
clog_by_filelog_format = syslog_full_msg_pre + basic_msg_pre + '%(clog_message)s'

event_log_by_syslog_format = syslog_client_msg_pre + basic_msg_pre + '%(message)s'
clog_by_syslog_format = syslog_client_msg_pre + basic_msg_pre + '%(clog_message)s'

class BasicContextFilter(logging.Filter):

    def __init__(self):
        self.local_ip = net.get_local_ip_address()

    def filter(self, record):
        record.time_iso_8601 = timeutil.local_now_ios8061_str()
        record.local_ip = self.local_ip
        record.pid = os.getpid()
        record.tid = get_ident()
        return True

class ContextFilter(logging.Filter):

    def __init__(self, app_name):
        self.local_ip = net.get_local_ip_address()
        self.app_name = app_name

    def filter(self, record):
        record.time_iso_8601 = timeutil.local_now_ios8061_str()
        record.local_ip = self.local_ip
        record.app_name = self.app_name
        record.pid = os.getpid()
        record.tid = get_ident()
        return True

class ClogContextFilter(logging.Filter):

    def __init__(self, app_name, env):
        self.local_ip = net.get_local_ip_address()
        self.app_name = app_name
        self.env = env

    def buildCLogMessage(self, record):
        clog_data = {}
        clog_data['env'] = self.env
        clog_data['app'] = self.app_name
        clog_data['pid'] = os.getpid()
        clog_data['tid'] = get_ident()

        clog_data['level'] = record.levelname
        clog_data['filename'] = record.filename
        clog_data['lineno'] = record.lineno
        clog_data['msg'] = record.getMessage()

        return 'cpbox clog %s' % json.dumps(clog_data)

    def filter(self, record):
        record.time_iso_8601 = timeutil.local_now_ios8061_str()
        record.app_name = self.app_name
        record.env = self.env
        record.local_ip = self.local_ip
        record.pid = os.getpid()
        record.tid = get_ident()
        record.clog_message = self.buildCLogMessage(record)
        return True

def getLogger(name=''):
    logger = logging.getLogger(name)
    return logger

def _get_rotating_filehandler(filename):
    file.ensure_dir_for_file(filename)
    handler = logging.handlers.RotatingFileHandler(filename, mode='a', maxBytes=1024 * 1024 * 128, backupCount=3)
    os.chmod(filename, 0o666)
    return handler

def _get_syslog_handler(syslog_ng_server):
    # SysLogHandler has no retry policy, in a long run script, server side will clost the connection which will cause the broken pipe error.
    # It's just a toy. We would like using UDP instead of TCP.
    return logging.handlers.SysLogHandler(address=(syslog_ng_server, 514), facility='local6')
    syslog_handler = None
    tcp_port = 601
    if net.is_open(syslog_ng_server, tcp_port):
        syslog_handler = logging.handlers.SysLogHandler(address=(syslog_ng_server, tcp_port), facility='local7', socktype=socket.SOCK_STREAM)
    else:
        syslog_handler = logging.handlers.SysLogHandler(address=(syslog_ng_server, 514), facility='local6')
    return syslog_handler

def _map_log_level(log_level_str):
    log_level = logging.INFO
    if log_level_str is not None:
        level = log_level_str.lower()
        log_level_conf = {
            'verbose': logging.NOTSET,
            'debug': logging.DEBUG,
            'info': logging.INFO,
            'warning': logging.WARNING,
            'warn': logging.WARNING,
            'error': logging.ERROR,
            'critical': logging.CRITICAL,
        }
        if level in log_level_conf:
            log_level = log_level_conf[level]
    return log_level

def setup_readable_logger_handler(app_name, log_level, handler):
    formatter = logging.Formatter(readable_format)
    filter = ContextFilter(app_name)

    handler.setFormatter(formatter)
    handler.setLevel(_map_log_level(log_level))
    handler.addFilter(filter)
    return handler

def setup_clog_file_handler(app_name, env, log_level, handler, format):
    filter = ClogContextFilter(app_name, env)
    handler.setFormatter(logging.Formatter(format))
    handler.setLevel(_map_log_level(log_level))
    handler.addFilter(filter)
    return handler

def setup_event_log_handler(app_name, handler, format):
    filter = ContextFilter(app_name)
    handler.setFormatter(logging.Formatter(format))
    handler.addFilter(filter)

    event_logger = logging.getLogger('event-log')
    event_logger.propagate = False
    event_logger.setLevel(logging.INFO)
    event_logger.addHandler(handler)
    return event_logger


def make_logger_for_test():
    basic_handlers = []
    stream_handler = logging.StreamHandler()

    formatter = logging.Formatter(readable_format)
    filter = BasicContextFilter()
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(_map_log_level('debug'))
    stream_handler.addFilter(filter)

    basic_handlers.append(stream_handler)

    root_logger = logging.getLogger()
    root_logger.handlers = []
    for h in basic_handlers:
        root_logger.setLevel(h.level)
        root_logger.addHandler(h)

def make_logger_for_app(app_name, env, logs_dir, log_level='debug', file_log=True, stdout=True):
    basic_handlers = []

    os_name = system.get_os_name()
    syslog_ng_server = os.environ['CPBOX_SYSLOG_NG_SERVER'] if 'CPBOX_SYSLOG_NG_SERVER' in os.environ else None
    if syslog_ng_server:
        event_log_syslog_handler = _get_syslog_handler(syslog_ng_server)
        setup_event_log_handler(app_name, event_log_syslog_handler, event_log_by_syslog_format)

        clog_syslog_handler = _get_syslog_handler(syslog_ng_server)
        setup_clog_file_handler(app_name, env, log_level, clog_syslog_handler, clog_by_syslog_format)
        basic_handlers.append(clog_syslog_handler)
    else:
        filename = logs_dir / 'syslog' / (app_name + '_event_log.log')
        event_log_file_handler = _get_rotating_filehandler(filename)
        setup_event_log_handler(app_name, event_log_file_handler, event_log_by_filelog_format)

        filename = logs_dir / 'syslog' / (app_name + '_clog_event_log.log')
        clog_file_handler = _get_rotating_filehandler(filename)
        setup_clog_file_handler(app_name, env, log_level, clog_file_handler, clog_by_filelog_format)
        basic_handlers.append(clog_file_handler)

    if file_log:
        filename = '%s/%s.log' % (logs_dir, app_name)
        app_filelog_handler = _get_rotating_filehandler(filename)
        setup_readable_logger_handler(app_name, log_level, app_filelog_handler)
        basic_handlers.append(app_filelog_handler)

    if stdout:
        import sys
        stream_handler = logging.StreamHandler(sys.stdout)
        setup_readable_logger_handler(app_name, log_level, stream_handler)
        basic_handlers.append(stream_handler)

    root_logger = logging.getLogger()
    root_logger.handlers = []
    for h in basic_handlers:
        root_logger.setLevel(h.level)
        root_logger.addHandler(h)
    holder.basic_handlers = basic_handlers

def shutdown():
    for handler in holder.basic_handlers:
        handler.close()
