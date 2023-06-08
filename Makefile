.PHONY: list
list:
	@LC_ALL=C $(MAKE) -pRrq -f $(firstword $(MAKEFILE_LIST)) : 2>/dev/null | awk -v RS= -F: '/(^|\n)# Files(\n|$$)/,/(^|\n)# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | egrep -v -e '^[^[:alnum:]]' -e '^$@$$'

### data import ###############################################################

import.positions:
	docker-compose -f local-aws.yml run django-cli python manage.py runscript import_positions

import.trades:
	docker-compose -f local-aws.yml run django-cli python manage.py runscript import_trades

### docker stuff ##############################################################

docker.cleanup:
	docker rm $(docker ps -aq)

docker.build:
	docker-compose -f local-aws.yml build

# docker.push:
# 	docker-compose -f local-aws.yml build

docker.up.django:
	docker-compose -f local-aws.yml up django

docker.django-cli:
	docker-compose -f local-aws.yml run django-cli python manage.py shell

### development commands ######################################################

### aws

db.migrate:
	docker-compose -f local-aws.yml run django-cli python manage.py migrate

db.makemigrations:
	docker-compose -f local-aws.yml run django-cli python manage.py makemigrations

# dump data from aws db
db.pg_dump:
	docker-compose -f local-aws.yml run django-cli python manage.py runscript db_dump


### local

local.docker.test:
	docker-compose -f local.yml run django-cli python manage.py test

# import data into local db
local.db.pg_restore:
	docker-compose -f local.yml run django-cli python manage.py runscript db_import

local.db.migrate:
	docker-compose -f local-aws.yml run django-cli python manage.py migrate

local.db.makemigrations:
	docker-compose -f local-aws.yml run django-cli python manage.py makemigrations
