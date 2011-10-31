#/bin/sh
python ../manage.py sqlreset history | mysql ffxivarmoury --default-character-set=utf8 -u root -p
cat bootstrap.sql | mysql ffxivarmoury --default-character-set=utf8 -u root -p
python ./loader.py
