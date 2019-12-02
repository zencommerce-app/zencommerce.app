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


## Installation and requirements

Application use Django 2.x framework and Python 3.x. It is designed to be deployed on Heroku Cloud platform (https://www.heroku.com ).

First you need to create a virtual environment and install required Python packages:

    virtualenv venv -p python3

    source ./venv/bin/activate

    pip install -r requirements.txt

The most important packages are - Django, Gunicorn, Heroku app support, PostgreSQL, Redis Queue, Sentry integration.

Known issues:
 * 'psycopg2' package installation may result in error. You may use 'psycopg2-binary' pre-built package as well.
