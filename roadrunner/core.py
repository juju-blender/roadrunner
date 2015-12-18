import exception
import logging
import os
import shlex
import subprocess
import time
import yaml


LOG = logging.getLogger('roadrunner.core')


class DefinitionSet(object):
    "Set of definitions"
    log = logging.getLogger('roadrunner.core.DefinitionSet')

    def __init__(self, fpath):

        self.dry_run = False
        self.definitions = []
        self.fpath = fpath
        if not os.path.isfile(fpath):
            raise exception.DefinitionSetNotFound(fpath)

        with open(self.fpath, 'r') as f:
            self._raw_definitions = yaml.safe_load(f)

        for defname, defbody in self._raw_definitions.items():
            self.log.debug("Definition found: %s", defname)
            self.definitions.append(Definition(defname, defbody))

    def run(self):
        for definition in self.definitions:
            definition.dry_run = self.dry_run
            definition.run()


class Definition(object):
    log = logging.getLogger('roadrunner.core.Definition')

    def __init__(self, name, body):
        self.name = name
        self.body = body
        self.dry_run = False
        self.environment = self.body['environment']

    def run(self):
        if 'bootstrap' in self.body:
            self.do_bootstrap()

        if 'deployer' in self.body:
            self.do_deployer()

        if 'juju-upgrade' in self.body:
            self.do_juju_upgrade()

    # bootstrap
    def do_bootstrap(self):
        self.add_juju_repo(self.body['version'])
        self.install_juju(self.body['version'])
        self.do_hooks('bootstrap', 'pre')
        self.do_bootstrap_actual()
        self.do_hooks('bootstrap', 'post')

    def do_bootstrap_actual(self, timeout=None):

        p = Process(['juju', 'bootstrap', '-e', self.environment],
                    dry_run=self.dry_run)
        p.monitor()

        assert p.returncode == 0

    # deployer
    def do_deployer(self):
        self.do_hooks('deployer', 'pre')
        self.do_deployer_actual()
        self.do_hooks('deployer', 'post')

    def do_deployer_actual(self):
        cmd = ['juju', 'deployer', '-c', self.body['deployer']['file']]
        cmd += shlex.split(self.body['deployer']['arguments'])
        p = Process(cmd, dry_run=self.dry_run)
        p.monitor()

        assert p.returncode == 0

    # juju upgrade-juju
    def do_juju_upgrade(self):
        self.do_hooks('juju-upgrade', 'pre')
        self.do_juju_upgrade_actual()
        self.do_hooks('juju-upgrade', 'post')

    def do_juju_upgrade_actual(self):
        cmd = ['juju', 'upgrade-juju', '--version',
               str(self.body['juju-upgrade']['version'])]

        p = Process(cmd, dry_run=self.dry_run)
        p.monitor()

        assert p.returncode == 0

    def add_juju_repo(self, version):
        p = Process(['sudo', 'add-apt-repository', '-y',
                     'ppa:freyes/juju-%s' % version], dry_run=self.dry_run)
        p.monitor()

        p = Process(['sudo', 'apt-get', 'update'], dry_run=self.dry_run)
        p.monitor()
        assert p.returncode == 0

    def install_juju(self, version):
        p = Process(['sudo', 'apt-get', 'install', '-y',
                     'juju-core=%s' % version], dry_run=self.dry_run)
        p.monitor()

        assert p.returncode == 0

    def do_hooks(self, section, when):
        # TODO(freyes): make this a decorator (?)
        try:
            for cmd in self.body[section]['hooks'][when]:
                # example cmd -> {'bash': 'echo foobar'}
                #                {'testament': 'swa.testament'}
                if "bash" in cmd:
                    p = Process(shlex.split(cmd['bash']), dry_run=self.dry_run)
                elif 'testament' in cmd:
                    p = TestamentProcess(cmd['testament'],
                                         dry_run=self.dry_run)
                else:
                    raise exception.HookPrefixUnknown(cmd)

                p.monitor()
                self.log.debug("Exit code: %d", p.returncode)
                assert p.returncode == 0
        except KeyError as ex:
            self.log.debug(str(ex))
            self.log.info("%s hooks for %s not found", when, section)

    def __str__(self):
        return "Definition<%s>" % self.name


class Process(subprocess.Popen):
    log = logging.getLogger('roadrunner.core.Process')

    def __init__(self, *args, **kwargs):

        self.log.debug('Running: %s', args[0])
        self._dry_run = kwargs.pop('dry_run', False)
        if not self._dry_run:
            subprocess.Popen.__init__(self, *args, **kwargs)
        else:
            self.returncode = 0

    def monitor(self, timeout=None):
        if self._dry_run:
            return

        done = False
        start = time.time()
        while not done:
            time.sleep(1)
            done = p.poll() is not None

            if timeout and time.time() - start >= timeout:
                raise exception.DefinitionTimeout()


class TestamentProcess(Process):
    log = logging.getLogger('roadrunner.core.TestamentProcess')

    def __init__(self, fpath, **kwargs):
        Process.__init__(self, ['testament', fpath], **kwargs)
