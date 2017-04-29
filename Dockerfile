# ほんとはalpineが良かったけどtexliveのインストールに手間取ったので。
FROM python:3.4

RUN echo "deb http://ftp.jp.debian.org/debian/ jessie main contrib non-free" > /etc/apt/sources.list
RUN apt-get update
RUN apt-get install -y texlive-lang-cjk
RUN updmap-sys --setoption kanjiEmbed ipaex
ADD freeze.txt .
RUN pip install -r freeze.txt
RUN apt-get install sqlite3

WORKDIR /app
ADD ./static /var/static
ADD django/django/contrib/admin/static/admin /var/static/admin

CMD gunicorn kumanodocs.wsgi:application -c config/gunicorn.conf.py
