from flask import Flask, render_template, request, redirect, url_for,flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from database import db, User, Stamp



app = Flask(__name__)
app.secret_key = 'secret_key'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydb.db'  # SQLiteの設定
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# db をアプリケーションに初期化
db.init_app(app)

# Flask-Login のセットアップ
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = '/'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 初回だけ実行してデータベース作成
with app.app_context():
    db.create_all()

# ホーム画面
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']

        user = User.query.filter_by(name=name).first()
        if user and user.check_password(password):
            login_user(user)
            flash("ログインしました", "success")
            return redirect(url_for('stamp'))
            # return redirect(url_for('index'))
        else:
            flash("ユーザ名かパスワードが間違っています。", "danger")

    return render_template('home.html')

# ユーザ登録
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']

        if User.query.filter_by(name=name).first():
            flash("ユーザー名が既に存在します", "danger")
        else:
            new_user = User(name=name)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            flash("登録完了！ログインしてください", "success")
            return redirect(url_for('home'))

    return render_template('register.html')

# ログアウト
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("ログアウトしました", "info")
    return redirect(url_for('home'))

# スタンプラリー画面
@app.route('/stamp', methods=['GET', 'POST'])
@login_required
def stamp():
    # ユーザーのスタンプ情報を取得（なければデフォルト0）
    stamp = Stamp.query.filter_by(user_id=current_user.id).first()
    total_stamps = stamp.stamp_count if stamp else 0

    if request.method == 'POST':
        # # 既存のスタンプを取得（なければ新規作成）
        # stamp = Stamp.query.filter_by(user_id=current_user.id).first()
        
        if not stamp:
            stamp = Stamp(user_id=current_user.id, stamp_count=1)
            db.session.add(stamp)
        else:
            if stamp.stamp_count < 10:
                stamp.stamp_count += 1  # スタンプを1つ増やす
            else:
                flash("スタンプは10個までです!", "warning")
                return redirect(url_for('stamp'))

        db.session.commit()
        flash("スタンプを獲得しました！", "success")
        return redirect(url_for('stamp'))

    return render_template('stamp.html', total_stamps=total_stamps)
# @app.route('/stamp')
# @login_required
# def stamp():
#     return render_template('stamp.html')

# 取得したスタンプをデータベースに追加する処理（未実装）
@app.route('/get_stamp', methods=['POST'])
@login_required
def get_stamp():
    # ユーザーのスタンプ情報を取得（なければデフォルト0）
    stamp = Stamp.query.filter_by(user_id=current_user.id).first()
    total_stamps = stamp.stamp_count if stamp else 0

    if request.method == 'POST':
        # # 既存のスタンプを取得（なければ新規作成）
        # stamp = Stamp.query.filter_by(user_id=current_user.id).first()
        if not stamp:
            stamp = Stamp(user_id=current_user.id, stamp_count=1)
            db.session.add(stamp)
        else:
            if stamp.stamp_count < 10:
                stamp.stamp_count += 1  # スタンプを1つ増やす
            else:
                flash("スタンプは10個までです!", "warning")
                return redirect(url_for('stamp'))

        db.session.commit()
        flash("スタンプを獲得しました！", "success")
        return redirect(url_for('stamp2'))



# カードゲーム画面
@app.route('/game')
@login_required
def game():
    # return render_template('game.html')
    # ユーザーのスタンプ数を取得
    user_stamp = Stamp.query.filter_by(user_id=current_user.id).first()
    
    if user_stamp and user_stamp.stamp_count == 10:
        return render_template('game.html')  # スタンプ10個以上でゲーム画面
    else:
        flash("スタンプを10個集めてからプレイできます", "warning")
        return redirect(url_for('stamp'))  # スタンプ画面にリダイレクト

# 情報表示画面
@app.route('/info')
@login_required
def info():
    return render_template('info.html')

@app.route('/stamp2')
def index():
    return render_template('stamp2.html')

@app.route('/spots')
def get_spots():
    spots = [
        # {"name": "セブン", "latitude": 35.18421, "longitude": 137.11190, "radius": 20},
        {"name": "14号館", "latitude": 35.184473, "longitude": 137.110925, "radius": 20},
        # {"name": "愛工大", "latitude": 35.1835, "longitude": 137.1130, "radius": 50},
        # {"name": "浅草寺", "latitude": 35.7148, "longitude": 139.7967, "radius": 400},
        # {"name": "テスト用", "latitude": 35.198600, "longitude": 137.093998, "radius": 30}
    ]
    return jsonify(spots)

@app.route('/test_spots')
def get_test_spots():
    test_spots = [
        {"name": "14号館", "latitude": 35.184473, "longitude": 137.110925, "radius": 20},
        {"name": "セブン", "latitude": 35.18421, "longitude": 137.11190, "radius": 20},
        {"name": "愛工大", "latitude": 35.1835, "longitude": 137.1130, "radius": 50},
        {"name": "浅草寺", "latitude": 35.7148, "longitude": 139.7967, "radius": 400}
    ]
    return jsonify(test_spots)    

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)