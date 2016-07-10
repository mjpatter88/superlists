Provisioning and Deploying a new site
=======================

## Provisioning
* Assume we have a user account and home folder
* apt-get install nginx git
* Setup Python, pyenv, etc.
* Add Nginx config for virtual host
* Add Systemd service job for Gunicorn

## Deployment
* Create directory structure in ~/sites
* Pull down source code into folder named source
* Pyenv activate
* pip install -r requirements.txt
* manage.py migrate for database
* collectstatic for static files
* Set DEBUG = False and ALLOWED_HOSTS in settings.py
* Restart Gunicorn job
* Run FTs to check everything works

## Folder structure:
Assume we have a user account at /home/username

/home/username
|-- sites
    |-- SITENAME
         |-- database
         |-- source
         |-- static
         |-- virtualenv