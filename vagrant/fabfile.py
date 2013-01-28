import os

from fabric.api import task, env, run, settings, cd, open_shell, put
from fabric.contrib import files
from fabtools.vagrant import ssh_config, _settings_dict
import fabtools  # NOQA
from fabtools import require

here = os.path.abspath(os.path.dirname(__file__))


@task
def vagrant(name=''):
    config = ssh_config(name)
    extra_args = _settings_dict(config)
    env.update(extra_args)
    env['user'] = 'root'


@task
def remote_bootstrap():
    env['use_remote_bootstrap'] = True


@task
def shell():
    """Open a shell on the environment"""
    open_shell()


@task
def install_pytheon():
    require.deb.packages(['python2.6', 'build-essential', 'git'])
    require.user('pytheon', home='/var/lib/pytheon', shell='/bin/bash')
    if not fabtools.files.is_dir('/var/lib/pytheon/.ssh'):
        run('mkdir -p /var/lib/pytheon/.ssh')
        run('cp -f /root/.ssh/authorized_keys /var/lib/pytheon/.ssh')
        run("chown -R pytheon:pytheon /var/lib/pytheon/.ssh")

    with settings(name='pytheon'):
        with cd('/var/lib/pytheon'):
            if not fabtools.files.is_file('pytheon_bootstrap.py'):
                if env.get('use_remote_bootstrap', False):
                    run('wget -c --no-check-certificate https://raw.github.com/pytheon/pytheon.deploy/master/deploy/pytheon_bootstrap.py')
                else:
                    put(
                        os.path.join(here, '../deploy/pytheon_bootstrap.py'),
                        '/var/lib/pytheon/'
                    )

        if not fabtools.files.is_dir('/var/lib/pytheon/eggs'):
            with cd('/var/lib/pytheon'):
                run('python2.6 pytheon_bootstrap.py --eggs=/var/lib/pytheon/eggs/')


@task
def upgrade_pytheon():
    with settings(name='pytheon'):
        with cd('/var/lib/pytheon'):
            run('/var/lib/pytheon/bin/pytheon-upgrade')


@task
def install_sample_buildout():
    require.user('user1', create_home=True, shell='/bin/bash')
    with settings(name='user1'):
        files.append(
            '/home/user1/.bashrc',
            'export PYTHEON_ADMIN=/var/lib/pytheon/bin/pytheon-admin'
        )
        run(  # TODO use $PYTHEON_ADMIN here
            '/var/lib/pytheon/bin/pytheon-admin -d https://github.com/pytheon/sample_buildout.git --host=example.com'
        )


@task
def uninstall_sample_buildout():
    pass


@task
def uninstall_pytheon():
    run('rm -rf /var/lib/pytheon')
