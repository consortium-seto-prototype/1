from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import csv
import zipfile
import io
import os
from datetime import datetime
from database import db, User, Spot, Stamp, StampRecord

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydb.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def db_to_csv():
    with app.app_context():
        now = datetime.now().strftime('%Y%m%d_%H%M%S')
        zip_filename = f"db_{now}.zip"

        home_dir = os.path.expanduser('~')
        desktop_path = os.path.join(home_dir, 'Desktop')
        save_path = os.path.join(desktop_path, zip_filename)

        # 各テーブルごとにcsvを作成
        tables = {
            'users.csv': User,
            'stamps.csv': Stamp,
            'stamprecode.csv': StampRecord,
            'spot.csv': Spot
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

# if __name__ == '__main__':
#     db_to_csv()