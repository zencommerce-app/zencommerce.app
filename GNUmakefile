default: gunicorn

loaddata:
	python3 ./zencommerce/manage.py loaddata initial_data.json

migrate:
	python3 ./zencommerce/manage.py makemigrations && python3 ./zencommerce/manage.py migrate

gunicorn: migrate
	gunicorn --pythonpath="$(PWD)/zencommerce" zencommerce.wsgi

runserver: migrate
	python3 ./zencommerce/manage.py runserver

redis:
	redis-server /usr/local/etc/redis.conf
