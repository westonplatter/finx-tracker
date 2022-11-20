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
Tracker is built in with a soft linking data dependency to [finx-reports-ib](https://github.com/westonplatter/finx-reports-ib). The following scripted steps assume that it's setup in a adjacent directory. Checkout the `finx-reports-ib` for more info on it.

```
mkdir -finx 
cd finx
git clone git@github.com:westonplatter/finx-tracker.git
git clone git@github.com:westonplatter/finx-reports-ib.git
cd finx-tracker.git
docker-compose -f local.yml build
make db.migrate
# run this, cd ../finx-ib-reports && make download.annual && finx-tracker
make import.trades
```

### Importing trades
Run this,
```
cp ../finx-ib-reports/data/* data
docker-compose -f local.yml run django-cli python manage.py runscript import_trades
```

### Importing positions
Run this,

```bash
cp ../finx-reports-ib/data/* data
docker-compose -f local.yml run django-cli python manage.py runscript import_positions
```

### Running the UI
Run this,

```bash
make docker.up.django
```



### DB / Migrations 
Run this,
```
docker-compose -f local.yml run django-cli python manage.py makemigrations [optional: app_name]
docker-compose -f local.yml run django-cli python manage.py migrate [optional: app_name]
```

## Test coverage
To run django based tests,
```
docker-compose -f local.yml run django-cli python manage.py test
```

## License
BSD-v3. See license file
