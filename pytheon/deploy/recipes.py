# -*- coding: utf-8 -*-
"""Recipe deploy"""
import os
import grp
import uuid
import pprint
import signal
import getpass
import logging
from hashlib import sha1
from os.path import join
from shutil import rmtree
from z3c.recipe.scripts import Scripts
from collective.recipe.template.genshitemplate import Recipe as Template

from pytheon.deploy import Config
from pytheon.deploy import patches
from pytheon import utils

try:
    from io import StringIO
except ImportError:
    from cStringIO import StringIO

WSGI_SCRIPT = """
for k in ('site', 'sitecustomize'):
    if k in sys.modules:
        del sys.modules[k]
del k
import site # imports custom buildout-generated site.py
sys.path = [p for p in reversed(sys.path)] # reverse paths to use eggs first

import logging
from paste.deploy import loadapp

configfile = %r

try:
    from paste.script.util.logging_config import fileConfig
    fileConfig(configfile)
except:
    logging.basicConfig(stream=sys.stderr, level=logging.WARN)

application = loadapp("config:" + configfile)
"""

if utils.PY3:
    INITIALIZATION = """
def execfile(f):
    exec(compile(open(f).read(), f, 'exec'), locals(), globals())
"""

else:
    INITIALIZATION = ""

INITIALIZATION += """
import os
%(environ_string)s
lib_dir = %(lib_dir)r
if os.path.isfile(os.path.join(lib_dir, 'environ.py')):
    execfile(os.path.join(lib_dir, 'environ.py'))
from pytheon import load_pkg_resources
"""

BUILDOUT = """
from pytheon.deploy import patches
import os
os.chdir(%r)
if '--with-git-update' in sys.argv:
    sys.argv.remove('--with-git-update')
    from pytheon import utils
    utils.call('git', 'pull', 'origin', utils.current_branch())
if 'pytheon.cfg' not in sys.argv:
    sys.argv.extend(['-c', 'pytheon.cfg'])
"""

SERVE = """
if 'pytheon-serve' in sys.argv[0]:
    sys.argv[1:] = %r
"""

def safe_options(func):
    def wrapper(self, *args, **kwargs):
        self.log('running %s', getattr(func, 'func_name', getattr(func, '__name__', '')))
        buildout_options = self.buildout['buildout'].copy()
        #self.log('> buildout["buildout"] = %r', buildout_options)
        options = self.options.copy()
        result = func(self, *args, **kwargs)
        keys = self.options.keys()
        for k in keys:
            if k not in options:
                del self.options[k]
        for k, v in options.items():
            self.options[k] = v
        for k, v in options.items():
            if k in ('bin-directory',):
                self.buildout['buildout'][k] = v
        #self.log('< buildout["buildout"] = %r', self.buildout["buildout"])
        return result
    return wrapper


class Base(object):

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options
        self.logger = logging.getLogger(name.title())

        if 'inherit' in self.options:
            inherit_options = self.buildout[self.options['inherit']]
            for k, v in inherit_options.items():
                if k not in self.options:
                    self.options[k] = v

        if 'project_name' not in self.options:
            self.options['project_name'] = os.path.basename(os.getcwd())
        if 'uuid' not in self.options:
            self.options['uuid'] = str(uuid.uuid4())
        if 'password' not in self.options:
            if utils.PY3:
                self.options['password'] = str(sha1(str(uuid.uuid4()).encode('ascii')).hexdigest())
            else:
                self.options['password'] = str(sha1(str(uuid.uuid4())).hexdigest())

        self.options['uid'] = getpass.getuser()
        self.options['gid'] = grp.getgrgid(os.getegid())[0]
        self.options['eggs'] = self.options.get('eggs', 'PasteDeploy')
        self.options['eggs'] += '\n' + self.buildout['buildout'].get('requirements-eggs', '')

        self.curdir = os.path.realpath(buildout['buildout']['directory'])
        self.deploy_dir = utils.realpath(options.get('deploy-dir',
                            join(self.buildout['buildout']['parts-directory'], self.name)))
        self.bin_dir = self.buildout['buildout']['bin-directory']
        self.lib_dir = utils.realpath(self.deploy_dir, 'lib')
        self.var_dir = utils.realpath(self.deploy_dir, 'var')
        self.etc_dir = utils.realpath(self.deploy_dir, 'etc')
        self.run_dir = utils.realpath(self.var_dir, 'run')
        dirnames = dict(
            curdir=self.curdir,
            deploy_dir=self.deploy_dir,
            lib_dir=self.lib_dir,
            etc_dir=self.etc_dir,
            var_dir=self.var_dir,
            log_dir=utils.realpath(self.var_dir, 'log'),
            run_dir=self.run_dir,
          )
        for k, v in dirnames.items():
            self.options[k] = v

        if os.path.isfile(join(self.lib_dir, 'environ.py')):
            execfile(join(self.lib_dir, 'environ.py'))

        environ_string = ''
        for envvar in options.get('environ', '').split('\n'):
            envvar = envvar.strip()
            if envvar:
                k, v = envvar.split('=', 1)
                environ_string += '\nos.environ[%r] = %r' % (k.upper(), v)
                os.environ[k.upper()] = str(v)
        initialization = self.options.get('initialization', '')
        initialization += INITIALIZATION % dict(environ_string=environ_string, lib_dir=self.lib_dir)
        self.options['initialization'] = initialization

    def log(self, *args):
        self.logger.info(*args)

    def install_config(self, template, **kwargs):
        if 'output' in kwargs:
            output = kwargs.pop('output')
        else:
            output = join(self.etc_dir, template)
        for k, v in kwargs.items():
            if isinstance(v, list):
                v = '\n'.join(v)
            self.options[k.replace('_', '-')] = v
        self.options['input'] = utils.template_path(template)
        self.options['output'] = output
        self.options['mode'] = '644'
        tmpl = Template(self.buildout, self.name, self.options)
        tmpl.install()
        return self.options['output']

    @safe_options
    def install_script(self, name, **kwargs):
        if name != self.name:
            name = '%s_%s' % (self.name, name)
        for k, v in kwargs.items():
            if isinstance(v, list):
                v = '\n'.join(v)
            k = k.replace('_', '-')
            if k in ('bin-directory',):
                self.buildout['buildout'][k] = v
            else:
                self.options[k] = v
        self.log('using %s', ', '.join(self.options['eggs'].split('\n')))
        scripts = Scripts(self.buildout, name, self.options)
        scripts.install()

    @property
    def django_setttings(self):
        if 'settings' in self.options:
            settings = self.options['settings']
        else:
            settings = join(self.curdir, 'settings.py')
        return settings

    @property
    def is_django(self):
        return os.path.isfile(self.django_setttings)

    @property
    def addons_requires(self):
        eggs = ''
        if 'CELERY_URL' in os.environ:
            if self.is_django:
                eggs += '\ncelery\ndjango-celery'
            else:
                eggs += '\ncelery'
        return eggs

class Wsgi(Base):

    @property
    def config(self):
        deploy = join(self.etc_dir, 'deploy.ini')
        current = Config.from_file(deploy)

        http_host = os.environ.get('IP', '127.0.0.1')
        if 'PORT' in os.environ:
            http_port = os.environ('PORT')
        else:
            filename = join(self.etc_dir, 'http_port.txt')
            if os.path.isfile(filename):
                http_port = open(filename).read().strip()
            else:
                http_port = current['server:pytheon'].port or utils.get_free_port()
                f = open(join(self.etc_dir, 'http_port.txt'), 'w')
                f.write(str(http_port))
                f.close()

        self.options['bind'] = '%s:%s' % (http_host, http_port)

        filename = join(self.curdir, 'deploy-%s.ini' % self.options['project_name'])
        if not os.path.isfile(filename):
            filename = join(self.curdir, 'deploy.ini')
        config = Config.from_file(filename, here=self.curdir, __file__=deploy)
        config['server:pytheon'] = dict(use='egg:Paste#http', host=http_host, port=http_port)

        if self.is_django:
            config['app:main'] = {
                    'paste.app_factory': 'pytheon.deploy.django_utils:make_django',
                  }

        fd = StringIO()
        config.write(fd)
        fd.seek(0)
        data = fd.read()
        data = data.replace('%(here)s', self.curdir)

        fd = open(deploy, 'w')
        fd.write(data)
        fd.close()

        return deploy

    def install_wsgi(self):
        eggs = Scripts(self.buildout, self.options['recipe'], self.options)
        reqs, ws = eggs.working_set()

        filename = self.buildout['buildout'].get('dump-picked-versions-file')
        if filename:
            config = Config()
            config.versions = dict([(pkg.project_name, pkg.version) for pkg in ws])
            config.write(filename)

        extra_paths = self.options.get('extra-paths', '')
        extra_paths = extra_paths.split()
        if self.is_django:
            extra_paths.append(os.path.dirname(self.django_setttings))

        self.install_script(name='scripts', extra_paths=extra_paths)

        # now we can switch in offline mode
        self.buildout['buildout']['offline'] = 'true'

        config = self.config
        addons_requires = self.addons_requires
        self.install_script(
                name='wsgi',
                bin_directory=self.lib_dir,
                entry_points='pytheon_wsgi.py=logging:warn',
                scripts='pytheon_wsgi.py=pytheon_wsgi.py',
                arguments='"%s run as a main module", __file__',
                extra_paths=extra_paths,
                eggs=self.options['eggs']+'\npytheon.deploy\nPasteDeploy\nsqlalchemy' + addons_requires,
                script_initialization=WSGI_SCRIPT % config,
                )
        wsgi_script = os.path.join(self.lib_dir, 'pytheon_wsgi.py')


        # bin/touch script
        self.install_script(
                name='touch',
                scripts='touch-wsgi=touch-wsgi',
                extra_paths='', eggs='',
                entry_points='touch-wsgi=os:utime',
                arguments='%r, (t, t)' % wsgi_script,
                script_initialization='import time; t = time.time()')

        if utils.PY3:
            # add lib dir to extra_paths so cherrypy can find the wsgi script
            dirname = os.path.dirname(wsgi_script)
            self.install_script(
                    name='cherrypy',
                    scripts='pytheon-serve\nceleryd=celeryd',
                    extra_paths=[dirname]+extra_paths,
                    entry_points='pytheon-serve=pytheon.deploy.scripts:cherrypy_serve',
                    eggs=self.options['eggs']+'\npytheon.deploy\nPasteDeploy' + addons_requires,
                    script_initialization=SERVE % ([config, self.options['bind']],)
                    )
        elif self.options.get('use', 'gunicorn') == 'gunicorn':
            self.options['bind'] = 'unix:%s' % join(self.run_dir, 'gunicorn.sock')
            gu_config = self.install_config('gunicorn_config.py')
            # add lib dir to extra_paths so gunicorn can find the wsgi script
            dirname = os.path.dirname(wsgi_script)
            self.install_script(
                    name='gunicorn',
                    scripts='gunicorn=pytheon-serve\nceleryd=celeryd',
                    extra_paths=[dirname]+extra_paths,
                    eggs=self.options['eggs']+'\npytheon.deploy\ngunicorn\nsqlalchemy' + addons_requires,
                    script_initialization=SERVE % (["-c", gu_config, "pytheon_wsgi:application"],))
        else:
            self.install_script(
                    name='pastescript',
                    scripts='paster=pytheon-serve\nceleryd=celeryd',
                    extra_paths=extra_paths,
                    eggs=self.options['eggs']+'\npytheon.deploy\nPasteScript\nsqlalchemy' + addons_requires,
                    script_initialization=SERVE % (["serve", "--server-name=pytheon", config],))

        if self.is_django:
            self.install_script(
                    name='django',
                    scripts='manage',
                    eggs=self.options['eggs']+'\npytheon.deploy\nsqlalchemy' + addons_requires,
                    entry_points='manage=pytheon.deploy.django_utils:manage',
                    extra_paths=extra_paths,
                    arguments='%r' % config)

        if 'CELERY_URL' in os.environ:
            celeryconfig = join(self.lib_dir, 'celeryconfig.py')
            if not os.path.isfile(celeryconfig):
                self.install_config('celeryconfig.py', output=celeryconfig)

        if not os.path.isfile(join(self.bin_dir, 'pytheon-update')):
            self.install_script(
                    name='buildout',
                    scripts='buildout=pytheon-update',
                    eggs='pytheon.deploy\nzc.buildout',
                    script_initialization=BUILDOUT % self.curdir,
                    )

        return tuple()

    update = install = install_wsgi

class Supervisor(Base):

    def install_supervisor(self, programs=None):

        if utils.PY3:
            return ()

        if programs is None:
            programs = []

        if 'CELERY_URL' in os.environ:
            if self.is_django:
                programs.insert(0, "celeryd = %s celeryd" % join(self.bin_dir, 'manage'))
            else:
                programs.insert(0, "celeryd = %s" % join(self.bin_dir, 'celeryd'))

        if programs:
            config = self.install_config('supervisor.conf', programs=programs)
        else:
            config = self.install_config('supervisor.conf')

        self.install_script(
                name='supervisor',
                eggs='supervisor\nmeld3',
                scripts='supervisorctl=pytheonctl',
                script_initialization='import sys; sys.argv[1:1] = ["-c", %r]' % config,
                arguments='sys.argv[1:]')
        self.install_script(
                name='supervisor',
                eggs='supervisor\nmeld3',
                scripts='supervisord=pytheond',
                script_initialization='import sys; sys.argv[1:] = ["-c", %r]' % config)

        # restart supervisor
        pid = join(self.run_dir, 'supervisord.pid')
        if os.path.isfile(pid):
            pid = int(open(pid).read().strip())
            try:
                os.kill(pid, signal.SIGHUP)
            except OSError:
                # start deamon if process does not exist
                utils.call('bin/pytheond')

        return tuple()

    update = install = install_supervisor

class Apache(Wsgi):


    def install(self):
        self.install_wsgi()
        self.install_config('apache.conf')
        return tuple()

    update = install

class Nginx(Wsgi, Supervisor):

    def install_nginx_config(self):
        static_paths =  self.options.get('static_paths', '').strip()
        www_root = utils.realpath(self.var_dir, 'www')
        rmtree(www_root)
        locations = []
        if static_paths:
            static_paths = [p.split('=') for p in static_paths.split('\n') if p.strip() and '=' in p]
            for location, path in static_paths:
                location = location.strip()
                path = path.strip()
                path = os.path.realpath(path.replace('%(here)s', self.curdir))
                if path.startswith(self.curdir) and '/' not in location.strip('/'):
                    location = '/%s/' % location.strip('/')
                    www_root = utils.realpath(self.var_dir, 'www')
                    os.symlink(path, os.path.realpath(join(www_root, location.strip('/'))))
                    locations.append(location)
        self.install_config('nginx.conf', www=www_root, locations=locations)

    def install(self):
        self.install_wsgi()
        self.install_nginx_config()
        self.install_supervisor(programs=['server = %s' % join(self.bin_dir, 'pytheon-serve')])
        return tuple()

    update = install

class Deploy(Nginx):

    def install(self):
        self.install_wsgi()
        self.install_config('apache.conf')
        self.install_nginx_config()
        self.install_supervisor(programs=['server = %s' % join(self.bin_dir, 'pytheon-serve')])
        return tuple()

    update = install

