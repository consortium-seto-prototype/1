from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import csv
import zipfile
import io

from datetime import datetime
zip_filename = f"db_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"

import os
home_dir = os.path.expanduser('~')
desktop_path = os.path.join(home_dir, 'Desktop')
save_path = os.path.join(desktop_path, zip_filename)

# モデルをインポート
from database import db, User, Stamp

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydb.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def tables_to_zip():
    with app.app_context():
        # 各テーブルごとにcsvを作成
        tables = {
            'users.csv': User,
            'stamps.csv': Stamp
        }

        memory_zip = io.BytesIO()
        with zipfile.ZipFile(memory_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for filename, model in tables.items():
                csv_buffer = io.StringIO()
                writer = csv.writer(csv_buffer)

                # カラム名を取得してヘッダーとして書き込み
                columns = [col.name for col in model.__table__.columns]
                writer.writerow(columns)

                # データを書き込み
                for row in model.query.all():
                    writer.writerow([getattr(row, col) for col in columns])

                # ZIPに追加
                zipf.writestr(filename, csv_buffer.getvalue())

        # ZIPを保存
        with open(save_path, 'wb') as f:
            f.write(memory_zip.getvalue())

        # print(f" {zip_filename} を作成しました。")
        print(f" {save_path} に保存しました。")

if __name__ == '__main__':
    tables_to_zip()