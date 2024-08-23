import os
import socket
import sys
from pathlib import Path

from cpbox.app.appconfig import appconfig
from cpbox.tool import file
from cpbox.tool import functocli
from cpbox.tool import logger
from cpbox.tool import spec
from cpbox.tool import system
from cpbox.tool import template
from cpbox.tool import utils

is_windows = os.name == 'nt'

class DevOpsAppConfig:

    def __init__(self, app_name, provider):
        appconfig.init(app_name, provider.get_env(), provider.get_app_config())


class DevOpsAppConfigContext:

    def __init__(self, app_name, kwargs):

        self.app_base_name = app_name
        self.kwargs = kwargs
        self.sandbox_version = kwargs.get('sandbox_version', 0)

        self.env = self._get_env()
        self.app_name = self._determine_app_name()

        self.construct_baisc_dir()

    def _determine_app_name(self):
        app_name = self.app_base_name
        if self.sandbox_version != 0:
            app_name = '%s-sandbox-%03d' % (app_name, self.sandbox_version)
        return app_name

    def construct_baisc_dir(self):
        default_data_dir = '/opt/data' if not is_windows else 'D:\\opt\\data'
        data_dir = Path(os.environ.get('CPBOX_DATA_DIR', default_data_dir))

        self.app_storage_dir = data_dir / self.app_name

        self.app_persistent_storage_dir = self.app_storage_dir / 'persistent'
        self.app_runtime_storage_dir = self.app_storage_dir / 'runtime'
        self.app_logs_dir = self.app_runtime_storage_dir / 'logs'

    def is_dev(self):
        return self.env == 'dev' or self.env == 'test'

    def _get_env(self):
        env = 'dev'
        if 'PUPPY_ENV' in os.environ:
            env = os.environ['PUPPY_ENV']
        if 'CPBOX_ENV' in os.environ:
            env = os.environ['CPBOX_ENV']
        if 'env' in self.kwargs:
            env = self.kwargs['env']
        return env

    def get_sandbox_code_dir(self):
        sandbox_code_dir = None
        base_dir = self.app_persistent_storage_dir
        if self.sandbox_version != 0:
            sandbox_code_dir = '%s/sandbox-code-%03d' % (base_dir, self.sandbox_version)
            sandbox_code_dir = Path(sandbox_code_dir)
        return sandbox_code_dir

    def get_root_dir(self):
        if hasattr(sys.modules['__main__'], '__file__'):
            root_dir = Path(sys.argv[0]).resolve().parent
            return root_dir
        else:
            root_dir = Path.cwd()
            return root_dir

    def ensure_dir_and_write_permission(self):
        file.ensure_dir(self.app_persistent_storage_dir)
        file.ensure_dir(self.app_runtime_storage_dir)
        file.ensure_dir(self.app_logs_dir)
        file.ensure_dir(self.app_logs_dir / 'syslog')


class DevOpsApp(object):

    def __init__(self, app_name, **kwargs):
        self.config_context = DevOpsAppConfigContext(app_name, kwargs)
        self.env = self.config_context.env

        self.construct_baisc_dir()

        self.logger = self._make_logger(app_name, kwargs)

        self.file_lock = None

    def _make_logger(self, app_name, kwargs):
        log_level = kwargs.get('log_level', 'info')
        logger.make_logger_for_app(app_name, self.env, self.app_logs_dir, log_level)
        return logger.getLogger(app_name)

    def construct_baisc_dir(self):

        context = self.config_context
        context.construct_baisc_dir()
        context.ensure_dir_and_write_permission()

        hostname = socket.gethostname()
        self.hostname_fqdn = hostname
        self.hostname_short = hostname.split('.', 1)[0]

        self.root_dir = context.get_sandbox_code_dir() if context.sandbox_version else context.get_root_dir()
        self._roles_dir = self.root_dir / 'roles'

        app_root_dir = self._roles_dir / context.app_base_name

        self.app_root_dir = app_root_dir
        self.app_config_dir = app_root_dir / 'config'
        self.app_templates_dir = app_root_dir / 'templates'
        self.app_scripts_dir = app_root_dir / 'scripts'

        self.app_storage_dir = context.app_storage_dir
        self.app_persistent_storage_dir = context.app_persistent_storage_dir
        self.app_runtime_storage_dir = context.app_runtime_storage_dir
        self.app_logs_dir = context.app_logs_dir

    def run_cmd_ret(self, cmd, log=True):
        return self.run_cmd(cmd, log=log)[1]

    def run_cmd(self, cmd, log=True):
        if log:
            self.logger.info('run_cmd: %s', cmd)
        return system.run_cmd(cmd)

    def shell_run(self, cmd, keep_pipeline=True, exit_on_error=True, dry_run=False, log=True):
        if log:
            self.logger.info('shell_run: %s', cmd)
        if dry_run:
            return 0
        return system.shell_run(cmd, keep_pipeline=keep_pipeline, exit_on_error=exit_on_error)

    def remove_container(self, name, force=False, dry_run=False):
        cmd = 'docker rm %s' % (name)
        if force:
            cmd = 'docker rm -f %s' % (name)
        self.shell_run(cmd, exit_on_error=False, dry_run=dry_run)

    def container_is_running(self, name):
        cmd = 'docker ps | grep %s' % (name)
        return self.run_cmd(cmd, log=False)[0] == 0

    def stop_container(self, name, timeout=300, dry_run=False):
        cmd = 'docker stop --time %d %s' % (timeout, name)
        self.shell_run(cmd, exit_on_error=False, dry_run=dry_run)

    def _check_lock(self):
        filepath = self.app_runtime_storage_dir / 'locks' / file.compute_lock_filepath(sys.argv)
        file_lock = file.obtain_lock(filepath)
        if file_lock is None:
            pid = 0
            with open(filepath, 'r') as f:
                pid = f.read()
            self.logger.warning('lock file exists, pid: %s => %s', pid, filepath)
            sys.exit(1)
        else:
            self.file_lock = file_lock

    def template_to(self, template_filename, dst, payload, app_name=None):
        template_payload = {'payload': payload}
        src = self.app_templates_dir_for(app_name) / template_filename
        template.render_to_file(src, template_payload, dst)
        self.logger.info('template_to: %s => %s', src, dst)

    def read_app_config(self, config_filebasename, app_name=None):
        if '.yml' not in config_filebasename:
            config_filebasename = config_filebasename + '.yml'
        data = utils.load_yaml(self.app_config_dir_for(app_name) / config_filebasename, {})
        return data

    def app_templates_dir_for(self, app_name=None):
        if app_name is None:
            return self.app_templates_dir
        return self._roles_dir / app_name / 'templates'

    def app_config_dir_for(self, app_name=None):
        if app_name is None:
            return self.app_config_dir
        return self._roles_dir / app_name / 'config'

    @functocli.keep_method
    def check_health(self):
        print('%s is good' % (sys.argv[0]))

    @staticmethod
    def run_app(app, log_level='info', default_method=None, common_args_option=None):
        common_args_option_basic = {
            'args': ['env', 'sandbox_version'],
            'default_values': {
                'env': None,
                'sandbox_version': 0,
            }
        }
        functocli.run_app(app, log_level, default_method, common_args_option, common_args_option_basic)
