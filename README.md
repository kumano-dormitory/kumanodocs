# Requirements

- Python >= 3.4.3
- Django >= 1.8
- django-bootstrap-form >= 3.2
- texlive

# Install

```
$ pip install -r freeze.txt
$ mv secret_key.py kumanodocs/
$ ./manage.py syncdb  # add super user
$ sudo updmap-sys --setoption kanjiEmbed ipaex
```

# Run App

```
$ ./manage.py runserver
```
