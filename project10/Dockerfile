FROM python:3.9
# Apacheとmod_wsgiの依存関係をインストール
RUN apt-get update && apt-get install -y \
    apache2 \
    apache2-dev \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*
# 作業ディレクトリの設定
WORKDIR /app
# 依存関係のインストール - バージョンを厳密に指定
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# mod_wsgiの設定
RUN mod_wsgi-express install-module > /etc/apache2/mods-available/wsgi.load
RUN chmod 644 /etc/apache2/mods-available/wsgi.load
RUN a2enmod wsgi
# アプリケーションのコピー
COPY . .
# ファイル権限の設定
RUN chmod 644 /app/wsgi.py /app/main.py /app/database.py
# データベースディレクトリのパーミッション設定
RUN mkdir -p /app/instance && chown -R www-data:www-data /app/instance
RUN chown -R www-data:www-data /app
# Apache設定ファイルのコピー
COPY apache/flask.conf /etc/apache2/sites-available/000-default.conf
# ポートの公開
EXPOSE 80
# Apacheの起動
CMD ["apache2ctl", "-D", "FOREGROUND"]