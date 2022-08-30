docker.cleanup:
	docker rm $(docker ps -aq)

docker.build:
	docker-compose -f local.yml build

docker.up.django:
	docker-compose -f local.yml up django

import.positions:
	# cp ../finx-ib-reports/data/*_open_positions.csv data
	docker-compose -f local.yml run django-cli python manage.py runscript import_positions

import.trades:
	cp ../finx-ib-reports/data/*_trades.csv data
	docker-compose -f local.yml run django-cli python manage.py runscript import_trades

db.migrate:
	docker-compose -f local.yml run django-cli python manage.py migrate

db.makemigrations:
	docker-compose -f local.yml run django-cli python manage.py makemigrations
