# coding: utf-8
import sys
import logging
# ログ設定
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
# アプリケーションのパスを追加
sys.path.insert(0, '/app')
from main import app as application
if __name__ == "__main__":
    application.run()