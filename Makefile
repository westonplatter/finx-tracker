docker.cleanup:
	docker rm $(docker ps -aq)

import.trades:
	cp ../finx-ib-reports/data/*_trades.csv data
	docker-compose -f local.yml run django-cli python manage.py runscript import_trades


db.migrate:
	docker-compose -f local.yml run django-cli python manage.py migrate

db.makemigrations:
	docker-compose -f local.yml run django-cli python manage.py makemigrations
