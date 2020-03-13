Quickstart
==========

1. Create 'local_settings.py' where 'settings.py' located (./zencommerce/zencommerce/)

    ETSY_KEYSTRING = '*************'
    ETSY_SHARED_SECRET = ''*************''

2. Virtualenv:

    virtualenv venv -p python3

    source ./venv/bin/activate

    pip install -r requirements.txt

3. Install Postgres, create a database 'zencommerce' (user and password - default, postgres/postgres)

4. Init DB

    python ./zencommerce/manage.py migrate

5. Create user

    python ./zencommerce/manage.py createsuperuser

6. Run dev server

    python ./zencommerce/manage.py runserver

    http://127.0.0.1:8000

7. Start redis and worker

    New terminal window

    redis-server /usr/local/etc/redis.conf

    New terminal window

    source ./venv/bin/activate

    python ./zencommerce/worker.py

