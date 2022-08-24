# finx-tracker
Web app to track PnL for options & futures strategies.

This codebase aims to 
- do few things well
- ingest trades & positions from broker
- allow users to declare portfolio specific strategies
- expose trades for user to link trades to strategies
- report PnL on portfolio/strategy/grouping levels

## Running

### Getting started
Run this,
```
docker-compose build
make db.migrate
# run this, cd ../finx-ib-reports && make download.annual && finx-tracker
make import.trades
make 
```

### Importing trades
cp ../finx-ib-reports/data/* data
docker-compose -f local.yml run django-cli python manage.py runscript import_trades

### Importing positions
cp ../finx-ib-reports/data/* data
docker-compose -f local.yml run django-cli python manage.py runscript import_positions


### DB / Migrations 
```
docker-compose -f local.yml run django-cli python manage.py makemigrations [optional: app_name]
docker-compose -f local.yml run django-cli python manage.py migrate [optional: app_name]
```

## Test coverage

To run the tests, check your test coverage, and generate an HTML coverage report:

    $ coverage run -m pytest
    $ coverage html
    $ open htmlcov/index.html


## License
BSD-v3. See license file
