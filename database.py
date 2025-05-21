from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import CheckConstraint

import csv
import os

db = SQLAlchemy()

# ユーザテーブル
class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # パスワードをハッシュ化
    def set_password(self, password):
        self.password = generate_password_hash(password)

    # 入力されたパスワードが登録されているパスワードハッシュと一致するかを確認
    def check_password(self, password):
        return check_password_hash(self.password, password)

# # スポットテーブル
class Spot(db.Model):
    __tablename__ = 'spot'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    order_number = db.Column(db.Integer, unique=True)  # 順番
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)

# スタンプテーブル
class Stamp(db.Model):
    __tablename__ = 'stamp'

    # id = db.Column(db.Integer, primary_key=True)
    # user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # spot_id = db.Column(db.Integer, db.ForeignKey('spot.id'), nullable=True)

    # entered_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    # exited_at = db.Column(db.DateTime)  

    # lat = db.Column(db.Float, nullable=True)
    # lng = db.Column(db.Float, nullable=True)

    # user = db.relationship('User', backref=db.backref('stamps', lazy=True))
    # spot = db.relationship('Spot', backref=db.backref('stamps', lazy=True))

    # これまでのやつ
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    stamp_count = db.Column(db.Integer, nullable=False, default=0)
    
    # 各スタンプの獲得状況（True = 獲得済み, False = 未獲得）
    stamp_1 = db.Column(db.Boolean, default=False)
    stamp_2 = db.Column(db.Boolean, default=False)
    stamp_3 = db.Column(db.Boolean, default=False)
    stamp_4 = db.Column(db.Boolean, default=False)


    # stamp_count は 0〜6 の間のみ許可
    __table_args__ = (CheckConstraint('stamp_count BETWEEN 0 AND 4', name='check_stamp_count'),)

    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class StampRecord(db.Model):
    __tablename__ = 'stampsrecord'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    spot_id = db.Column(db.Integer, db.ForeignKey('spot.id'), nullable=True)

    entered_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    exited_at = db.Column(db.DateTime)  

    lat = db.Column(db.Float, nullable=True)
    lng = db.Column(db.Float, nullable=True)

    user = db.relationship('User', backref=db.backref('stamps', lazy=True))
    spot = db.relationship('Spot', backref=db.backref('stamps', lazy=True))



# 使用しない可能性大

# # ゲームプレイ権テーブル
# class GamePlayRight(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     is_unlocked = db.Column(db.Boolean, default=False)
#     unlocked_at = db.Column(db.DateTime)

# # プレイ履歴テーブル
# class PlayHistory(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     score = db.Column(db.Integer, nullable=False)
#     played_at = db.Column(db.DateTime, default=datetime.utcnow)
