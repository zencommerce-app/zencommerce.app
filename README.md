# Zen-Commerce

Order management application for online sellers.

 * https://zencommerce.app
 * https://blog.zencommerce.app

## Manage multiple Etsy shops in one place

 * Multiple Etsy shops under one setup
 * Dashboard for unified view of all your Orders and Transactions
 * Workflow steps to process orders with ease

## Mission

Our mission is to make life more easy and pleasant and save time for the people we love. Etsy marketplace shop owners are mostly creative persons, who create a great handicraft items. It is great when hobbies and ideas become a successful business.

## License

Application code distributed under the terms of GNU GPLv3 license. This lets you do almost anything you want with a project, except distributing closed source versions.


## Obtaining Etsy API keys

In order to use Zen-Commerce application you need to register on https://www.etsy.com/developers/documentation/getting_started/register

This gives you your API key and allows you to start working on your application. When your application is created, it starts with Provisional Access to our production systems to use during development.

Etsy will provide you with a Keystring and Shared secret to use with API. Put these values into Zen-Commerce settings.
You should find placeholders 'settings.py':


    ETSY_KEYSTRING = PUT_YOUR_KEY_HERE
    ETSY_SHARED_SECRET = PUT_YOUR_SHARED_SECRET_HERE


## Installation and requirements

Application use Django 2.x framework and Python 3.x. It is designed to be deployed on Heroku Cloud platform (https://www.heroku.com ).

First you need to create a virtual environment and install required Python packages:

    virtualenv venv -p python3

    source ./venv/bin/activate

    pip install -r requirements.txt

The most important packages are - Django, Gunicorn, Heroku app support, PostgreSQL, Redis Queue, Sentry integration.

Known issues:
 * 'psycopg2' package installation may result in error. You may use 'psycopg2-binary' pre-built package as well.

Next step is setting up your PostgreSQL server. Zen-Commerce uses specific featured and wouldn't run on SQLite or MySQL.
You may get latest PostgreSQL on https://www.postgresql.org

## Settings.py and local_settings.py

Application's configuration is stored in a file named "settings.py".
This is natural way in a Django world. Most of values are ok by default.
Some of settings should be set in order to use Zen-Commerce:

    OAUTH_CALLBACK_URI = "http://YOURDOMAIN/man/oauth_callback"
    ETSY_KEYSTRING = 'KEYSTRING'
    ETSY_SHARED_SECRET = 'SECRET'
    SECRET_KEY = 'YOUR UNIQUE DJANGO SECRET KEY'
    SENTRY_DSN = 'https://BLABLABLA@sentry.io/BLABLABLA'
    DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'DB_NAME',
        'USER': 'DB_USER',
        'PASSWORD': 'DB_PASSWORD',
        'HOST': 'DB_HOST',
        'PORT': 'DB_PORT',
    }
}

After all is set up run these make commands from terminal:

    make migrate
    make loaddata
    make gunicorn

This will apply migrations, load initial data from fixtures and start a dev server at http://127.0.0.1:8000

To run a worker for background jobs:

1. New terminal window and

    redis-server /usr/local/etc/redis.conf

2. New terminal window and

    source ./venv/bin/activate

    python ./zencommerce/worker.py

Useful step:

    python ./zencommerce/manage.py createsuperuser

This will help you to create a root/superuser in application.


## Documentation

Documentation for project is maintained using Sphinx (http://www.sphinx-doc.org )

To work on documentation you will need to install it via PIP:

    pip install sphinx

If you need only to read documentation, you may use RTD https://zencommerceapp.readthedocs.io


## Contact us

Zen-Commerce team will be happy to hear a word from you.

