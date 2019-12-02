web: gunicorn --pythonpath="$PWD/zencommerce" zencommerce.wsgi
worker: python ./zencommerce/worker.py
clock: python clock.py
