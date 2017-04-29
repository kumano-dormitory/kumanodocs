# Requirements

- Python >= 3.4.3
- Django >= 1.8
- django-bootstrap-form >= 3.2
- texlive

# Install

```
$ pip install -r freeze.txt
$ cd kumanodocs
$ cp secret_key.py.example secret_key.py 
$ vi secret_key.py
$ cd ..
$ ./manage.py syncdb  # add super user
$ sudo updmap-sys --setoption kanjiEmbed ipaex
```
You can generate key from
http://www.miniwebtool.com/django-secret-key-generator/

# Run App

```
$ ./manage.py runserver
```
