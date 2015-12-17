import exception
import logging
import os
import time
import yaml


LOG = logging.getLogger('roadrunner.core')


class DefinitionSet(object):
    "Set of definitions"
    log = logging.getLogger('roadrunner.core.Definition')

    def __init__(self, fpath):

        self.definitions = []
        self.fpath = fpath
        if not os.path.isfile(fpath):
            raise exception.DefinitionSetNotFound(fpath)

        with open(self.fpath, 'r') as f:
            self._raw_definitions = yaml.safe_load(f)

        for defname, defbody in self._definitions.items():
            self.log.debug("Definition found: %s", defname)
            self.definitions.append(Definition(defname, defbody))

    def run(self):
        pass


class Definition(object):
    def __init__(self, name, body):
        self.name = name
        self.body = body

    def do_bootstrap(self):
        self.add_juju_repo(self.body['version'])
        self.install_juju(self.body['version'])
        self.do_bootstrap_hooks('bootstrap', 'pre')
        self.do_bootstrap_actual()
        self.do_bootstrap_hooks('bootstrap', 'post')

    def add_juju_repo(self, version):
        p = Process(['sudo', 'add-apt-repository', '-y',
                     'ppa:freyes/juju-%s' % version])
        p.wait()

        p = Process(['sudo', 'apt-get', 'update'])
        p.wait()
        assert p.returncode == 0

    def install_juju(self):
        p = Process(['sudo', 'apt-get', 'install', '-y',
                     'juju-core=%s' % version])
        p.wait()

        assert p.returncode == 0

    def do_hooks(self, section, when):
        try:
            for cmd in self.body[section]['hooks'][when]:
                p = Process(cmd)
                p.monitor()
                self.log.debug("Exit code: %d", p.returncode)
                assert p.returncode == 0
        except KeyError as ex:
            log.debug(str(ex))
            log.info("%s hooks for %s not found", when, section)

    def do_bootstrap_actual(self, timeout=None):

        p = Process(['juju', 'bootstrap', '-e', self.environment])
        p.monitor()

    def __str__(self):
        return "Definition<%s>" % self.name


class Process(subprocess.Popen):
    log = logging.getLogger('roadrunner.core.Process')

    def __init__(self, *args, **kwargs):
        self.log.debug('Running: %s', args[0])
        subprocess.Popen.__init__(self, *args, **kwargs)

    def monitor(self, timeout=None):
        done = False
        start = time.time()
        while not done:
            time.sleep(1)
            done = p.poll() is not None

            if timeout and time.time() - start >= timeout:
                raise exception.DefinitionTimeout()
