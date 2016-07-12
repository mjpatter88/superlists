from fabric.contrib.files import append, exists, sed
from fabric.api import env, local, run, sudo
import random

REPO_URL = 'https://github.com/mjpatter88/superlists.git'
env.forward_agent = True  # Use my local ssh key to authenticate with github, etc.


def deploy():
    site_name = env.host.split('.')[0]
    site_folder = '/home/{}/sites/{}'.format(env.user, site_name)
    source_folder = site_folder + '/source'
    virtual_env_folder = '/home/{}/.pyenv/versions/{}'.format(env.user, site_name)

    _create_directory_structure_if_neccessary(site_folder)
    _get_latest_source(source_folder)
    _update_settings(source_folder, env.host)
    _update_virtualenv(source_folder, env.user, virtual_env_folder, site_name)
    _update_static_files(source_folder, virtual_env_folder)
    _update_database(source_folder, virtual_env_folder)

    _deploy_nginx_if_neccessary(source_folder, site_name)
    _deploy_gunicorn_if_neccessary(source_folder, site_name)
    _restart_nginx()


def _create_directory_structure_if_neccessary(site_folder):
    for subfolder in ('database', 'static', 'source'):
        run('mkdir -p {}/{}'.format(site_folder, subfolder))


def _get_latest_source(source_folder):
    if exists(source_folder + '/.git'):
        run('cd {} && git fetch'.format(source_folder))
    else:
        run('git clone {} {}'.format(REPO_URL, source_folder))
    current_local_commit = local('git log -n 1 --format=%H', capture=True)
    run('cd {} && git reset --hard {}'.format(source_folder, current_local_commit))


def _update_settings(source_folder, host_name):
    settings_path = source_folder + '/superlists/settings.py'
    sed(settings_path, 'DEBUG = True', 'DEBUG = False')
    sed(settings_path, 'ALLOWED_HOSTS = .+$', 'ALLOWED_HOSTS = ["{}"]'.format(host_name))

    secret_key_file = source_folder + '/superlists/secret_key.py'
    if not exists(secret_key_file):
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
        key = ''.join(random.SystemRandom().choice(chars) for _ in range(50))
        append(secret_key_file, "SECRET_KEY = '{}'".format(key))
    append(settings_path, '\nfrom .secret_key import SECRET_KEY')


def _update_virtualenv(source_folder, user_name, virtual_env_folder, site_name):
    pyenv_bin = '/home/{}/.pyenv/bin'.format(user_name)
    if not exists(virtual_env_folder):
        run('{}/pyenv virtualenv 3.5.2 {}'.format(pyenv_bin, site_name))
    run('{}/bin/pip install -r {}/requirements.txt'.format(virtual_env_folder, source_folder))


def _update_static_files(source_folder, virtual_env_folder):
    run('cd {} && {}/bin/python manage.py collectstatic --noinput'.format(source_folder, virtual_env_folder))


def _update_database(source_folder, virtual_env_folder):
    run('cd {} && {}/bin/python manage.py migrate --noinput'.format(source_folder, virtual_env_folder))

def _deploy_nginx_if_neccessary(source_folder, site_name, host_name):
    # write config file to sites-available
    new_config_file = '{}/deploy_tools/{}'.format(source_folder, site_name)
    run('cp {}/deploy_tools/nginx-template.conf {}'.format(source_folder, new_config_file))
    sed(new_config_file, 'HOSTNAME', host_name)
    sed(new_config_file, 'SITENAME', site_name)
    sudo('mv {} /etc/nginx/sites-available/'.format(new_config_file)

    # link to it from sites-enabled
    # TODO start here

def _deploy_gunicorn_if_neccessary(source_folder, site_name):
    # TODO: only do the following if the service file doesn't already exist
    gunicorn_dir = '/etc/systemd/system/'
    gunicorn_file_name = 'gunicorn-{}.service'.format(site_name)
    if not exists(gunicorn_dir + gunicorn_file_name):
        new_config_file = '{}/deploy_tools/{}'.format(source_folder, gunicorn_file_name)
        run('cp {}/deploy_tools/gunicorn-template.service {}'.format(source_folder, new_config_file))
        sed(new_config_file, 'SITENAME', site_name)
        sudo('mv {} {}'.format(new_config_file, gunicorn_dir))
        # TODO: also start the servie and enable it?

def _restart_nginx():
    sudo('service nginx reload')

