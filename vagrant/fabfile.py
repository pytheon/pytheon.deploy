import os

from fabric.api import task, env, run, settings, cd, open_shell, put
from fabric.contrib import files
from fabric.contrib.project import upload_project
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
    env['branch'] = 'master'


@task
def remote_bootstrap():
    env['use_remote_bootstrap'] = True


@task
def remote_sample_buildout():
    env['use_remote_samble_buildout'] = True


@task
def shell():
    """Open a shell on the environment"""
    open_shell()


@task
def dev():
    env['branch'] = 'dev'


@task
def master():
    env['branch'] = 'master'


@task
def install_pytheon():
    require.deb.packages(['python2.6', 'build-essential', 'git', 'curl'])
    require.user('pytheon', home='/var/lib/pytheon', shell='/bin/bash')
    if not fabtools.files.is_dir('/var/lib/pytheon/.ssh'):
        run('mkdir -p /var/lib/pytheon/.ssh')
        run('cp -f /root/.ssh/authorized_keys /var/lib/pytheon/.ssh')
        run("chown -R pytheon:pytheon /var/lib/pytheon/.ssh")

    with settings(name='pytheon'):
        with cd('/var/lib/pytheon'):
            if not fabtools.files.is_file('pytheon_bootstrap.py'):
                if env.get('use_remote_bootstrap', False):
                    run(
                        'wget -c --no-check-certificate https://raw.github.com/pytheon/pytheon.deploy/%s/deploy/pytheon_bootstrap.py'
                        % env['branch']
                    )
                else:
                    put(
                        os.path.join(here, '../deploy/pytheon_bootstrap.py'),
                        '/var/lib/pytheon/'
                    )

        if not fabtools.files.is_dir('/var/lib/pytheon/eggs'):
            with cd('/var/lib/pytheon'):
                run('python2.6 pytheon_bootstrap.py --eggs=/var/lib/pytheon/eggs/ --branch=%s' % env['branch'])


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
        if env.get('remote_sample_buildout', False):
            run(  # TODO use $PYTHEON_ADMIN here
                '/var/lib/pytheon/bin/pytheon-admin -d https://github.com/pytheon/sample_buildout.git --host=example.com'
            )
        else:
            run('rm -rf /tmp/sample_buildout')
            upload_project(
                os.path.join(here, 'src/sample_buildout/'),
                '/tmp/'
            )
            run(  # TODO use $PYTHEON_ADMIN here
                '/var/lib/pytheon/bin/pytheon-admin -d /tmp/sample_buildout --host=example.com'
            )


@task
def uninstall_pytheon():
    run('rm -rf /var/lib/pytheon')


@task
def uninstall_sample_buildout():
    run('deluser user1')
    run('rm -rf /home/user1/')


@task
def install_develop_tools():
    require.deb.packages(['vim', 'mc', 'tree', 'curl'])
