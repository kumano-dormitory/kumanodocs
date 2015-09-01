# Requirements

- Python >= 3.4.3
- Django >= 1.8
- django-bootstrap-form >= 3.2
- lualatex >= beta-0.79.1

# Install

```
$ pip install -r freeze.txt
$ mv secret_key.py kumanodocs/
$ ./manage.py syncdb  # add super user
```

# Run App

```
$ ./manage.py runserver
```
