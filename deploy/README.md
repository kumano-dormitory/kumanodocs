# 運用メモ

## 概略

gunicorn + nginxで運用することを念頭に置く

- gunicorn で kumanodocs/wsgi.py を起動
- gunicorn は localhost:8000 に向けて公開
- nginx のリバースプロキシで localhost:8000 にアクセス

## Dependency

- gunicorn 
- nginx
- systemd (あってもなくても)

## やること

※ deployディレクトリの中の各ファイルは、ファイルパスなどを各自の環境に合わせて書き換えること。

```
$ cp deploy/nginx.conf /etc/nginx.conf
$ cp deploy/kumanodocs.service /etc/systemd/system/
$ cp -r django/contrib/admin/static/admin static/
$ systemctl start nginx.service
$ systemctl start kumanodocs.service
```
