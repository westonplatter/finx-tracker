# finx-tracker
Web app focused on tracking PnL for options/futures focused portfolios.

Success for the codebase, 
(1) code is does few things well
(2) keep it simple and direct - add comments if there's complexity or cleverness

## License
BSD-v3. See license file

## Personal notes 

### Importing trades
docker-compose -f local.yml run django-cli python manage.py runscript import_trades

## Getting started
Run this, 
```
```



## History Dump 

9328  dc -f local up
9336  dc -f local.yml up
9341  dc -f local.yml setup.cfg
9378  dc -f local.yml down
9406  dc -f local.yml postgres
9410  dc -f local.yml build
9411  dc -f local.yml run django-cli python --version
9412  dc -f local.yml run django-cli python manage.py 
9413  dc -f local.yml run django-cli python manage.py dbshell
9414  dc -f local.yml run django-cli python manage.py startapp trades trades
9415  dc -f local.yml run django-cli python manage.py startapp --help
9416  dc -f local.yml run django-cli python manage.py startapp trades finx_tracker
9417  dc -f local.yml run django-cli python manage.py startapp trades
9418  dc -f local.yml run django-cli python manage.py inspectdb
9421  dc -f local.yml run django-cli python manage.py --help
9422  dc -f local.yml run django-cli python manage.py makemigrateions trades
9423  dc -f local.yml run django-cli python manage.py reset_db
9424  dc -f local.yml run django-cli python manage.py migrate trades
9425  dc -f local.yml run django-cli python manage.py makemigrations trades
9427  dc -f local.yml run django-cli python manage.py shell
9437  dc -f local.yml run django-cli python manage.py startapp portfolios
9443  dc -f local.yml run django-cli python manage.py makemigrations 
9483  dc -f local.yml up postgres
9543  dc -f local.yml up -d postgres
9550  dc build
9552  dc -f local.yml run django-cli python manage.py runscript import_trades
9553  dc -f local.yml run django-cli python manage.py runscript gen_gs_trades
9554  dc -f local.yml run django-cli python manage.py runscript gen_gs_report
9555  dc -f local.yml run django-cli python manage.py runscript -v 2gen_gs_report 
9556  dc -f local.yml run django-cli python manage.py runscript -v2 gen_gs_report 
9591  dc  ps
9592  dc -f local.yml run django-cli python manage.py runscript -v2 x_import.py
9593  dc -f local.yml run django-cli python manage.py runscript -v2 gen_gs_report
9594  dc -f local.yml run django-cli python manage.py makemigrations
9595  dc -f local.yml run django-cli python manage.py migrate
9603  dc -f local.yml run django-cli python manage.py runscript -v2 import_trades
9604  dc -f local.yml run django-cli python manage.py runscript -v2 gen_gs_trades2
9605  dc -f local.yml run django-cli python manage.py runscript -v2 gen_gs_report2
9611  dc -f local.yml stop  


## DB / Migrations 
```
docker-compose -f local.yml run django-cli python manage.py makemigrations [optional: app_name]
docker-compose -f local.yml run django-cli python manage.py migrate [optional: app_name]
```

### Test coverage

To run the tests, check your test coverage, and generate an HTML coverage report:

    $ coverage run -m pytest
    $ coverage html
    $ open htmlcov/index.html

