#/bin/sh
python ../manage.py sqlreset history | mysql ffxivarmoury -u root -p
cat bootstrap.sql | mysql ffxivarmoury -u root -p
python ./loader.py