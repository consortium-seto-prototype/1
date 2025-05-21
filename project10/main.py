from flask import Flask, request, render_template, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from database import db, User, Stamp, GamePlayRight, PlayHistory

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
login_manager.login_message = "ログインが必要です。ログインしてください。"

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
            # flash("ログインしました", "success")
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
    # flash("ログアウトしました", "info")
    return redirect(url_for('home'))

# スタンプラリー画面
@app.route('/stamp', methods=['GET', 'POST'])
@login_required
def stamp():
    # ユーザーのスタンプ情報を取得（なければデフォルト0）
    stamp = Stamp.query.filter_by(user_id=current_user.id).first()
    total_stamps = stamp.stamp_count if stamp else 0
    print("スタンプの合計:")
    print(total_stamps)

    if total_stamps == 0:
        return render_template('stamp.html')
    if total_stamps == 1:
        return render_template('stamp2.html')
    if total_stamps == 2:
        return render_template('stamp3.html')
    if total_stamps == 3:
        return render_template('stamp4.html')
    if total_stamps == 4:
        return render_template('stamp5.html')
    if total_stamps == 5:
        return render_template('stamp6.html')
    if total_stamps == 6:
        return render_template('stamp7.html')
    if total_stamps == 7:
        return render_template('stamp8.html')
    if total_stamps == 8:
        return render_template('stamp9.html')
    if total_stamps == 9:
        return render_template('stamp10.html')
    if total_stamps == 10:
        return render_template('index.html')


# 取得したスタンプをデータベースに追加する処理
@app.route('/get_stamp', methods=['POST'])
@login_required
def get_stamp():
    # ユーザーのスタンプ情報を取得（なければデフォルト0）
    stamp = Stamp.query.filter_by(user_id=current_user.id).first()
    total_stamps = stamp.stamp_count if stamp else 0

    info = ["/info4", "/info3", "/info2", "/info", "/info4", "/info3", "/inf2", "/info", "/info4", "/info4"] 

    if request.method == 'POST':
        # # 既存のスタンプを取得（なければ新規作成）
        # stamp = Stamp.query.filter_by(user_id=current_user.id).first()
        if not stamp:
            stamp = Stamp(user_id=current_user.id, stamp_count=1)
            db.session.add(stamp)
            print("1つ目のスタンプを取得しました。")
        else:
            if stamp.stamp_count < 10:
                stamp.stamp_count += 1  # スタンプを1つ増やす
                # print(stamp.stamp_count)
                print("スタンプを取得しました。")
                # print(stamp.stamp_count + "個スタンプを取得しました。")
            else:
                # flash("スタンプは10個までです!", "warning")
                print("スタンプは10個までです。")
                return jsonify({"message": "スタンプは10個までです!", "redirect": None}), 400
                return redirect(url_for('stamp'))

        db.session.commit()
        # flash("スタンプを獲得しました！", "success")
        # print("スタンプを取得しました。")


        return jsonify({"message": "スタンプを獲得しました！", "redirect": info[stamp.stamp_count - 1]})
        # return redirect(url_for('stamp2'))



# カードゲーム画面
@app.route('/game')
@login_required
def game():
    stamp = Stamp.query.filter_by(user_id=current_user.id).first()
    total_stamps = stamp.stamp_count if stamp else 0

    return render_template('game.html', total_stamps=total_stamps)
    # user_stamp = Stamp.query.filter_by(user_id=current_user.id).first()
    
    # if user_stamp and user_stamp.stamp_count == 10:
    #     frash()
    #     return render_template('game.html')  # スタンプ10個以上でゲーム画面
    # else:
    #     flash("スタンプを10個集めてからプレイできます", "warning")
    #     return render_template('game.html')
        # return redirect(url_for('stamp'))  # スタンプ画面にリダイレクト

# 情報表示画面
@app.route('/info_home')
@login_required
def info_home():
    stamp = Stamp.query.filter_by(user_id=current_user.id).first()
    total_stamps = stamp.stamp_count if stamp else 0

    return render_template('info_home.html', total_stamps=total_stamps)


@app.route('/info')
@login_required
def info():
    stamp = Stamp.query.filter_by(user_id=current_user.id).first()
    total_stamps = stamp.stamp_count if stamp else 0

    return render_template('info.html', total_stamps=total_stamps)

@app.route('/info2')
@login_required
def info2():
    stamp = Stamp.query.filter_by(user_id=current_user.id).first()
    total_stamps = stamp.stamp_count if stamp else 0

    return render_template('info2.html', total_stamps=total_stamps)

@app.route('/info3')
@login_required
def info3():
    stamp = Stamp.query.filter_by(user_id=current_user.id).first()
    total_stamps = stamp.stamp_count if stamp else 0

    return render_template('info3.html', total_stamps=total_stamps)

@app.route('/info4')
@login_required
def info4():
    stamp = Stamp.query.filter_by(user_id=current_user.id).first()
    total_stamps = stamp.stamp_count if stamp else 0

    return render_template('info4.html', total_stamps=total_stamps)

@app.route('/test')
def index():
    return render_template('test.html')

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

@app.route('/spots2')
def get_spots2():
    spots = [
        {"name": "アロハカフェ", "latitude": 35.183932, "longitude": 137.1115, "radius": 20},
        # {"name": "14号館", "latitude": 35.184473, "longitude": 137.110925, "radius": 20},
    ]
    return jsonify(spots)

@app.route('/spots3')
def get_spots3():
    spots = [
        {"name": "セブンイレブン", "latitude": 35.18421, "longitude": 137.11190, "radius": 20},
        # {"name": "14号館", "latitude": 35.184473, "longitude": 137.110925, "radius": 20},
    ]
    return jsonify(spots)

@app.route('/spots4')
def get_spots4():
    spots = [
        {"name": "愛和食堂", "latitude": 35.18422, "longitude": 137.1123, "radius": 20},
        # {"name": "14号館", "latitude": 35.184473, "longitude": 137.110925, "radius": 20},
    ]
    return jsonify(spots)

@app.route('/spots5')
def get_spots5():
    spots = [
        {"name": "愛知工業大学図書館", "latitude": 35.18372, "longitude": 137.1130592000358, "radius": 25},
        # {"name": "14号館", "latitude": 35.184473, "longitude": 137.110925, "radius": 20},
    ]
    return jsonify(spots)

@app.route('/spots6')
def get_spots6():
    spots = [
        {"name": "セントラルテラス", "latitude": 35.1841977879422, "longitude": 137.11394978400818, "radius": 30},
        # {"name": "14号館", "latitude": 35.184473, "longitude": 137.110925, "radius": 20},
    ]
    return jsonify(spots)

@app.route('/spots7')
def get_spots7():
    spots = [
        {"name": "計算センター", "latitude": 35.18455, "longitude": 137.11455, "radius": 25},
        # {"name": "14号館", "latitude": 35.184473, "longitude": 137.110925, "radius": 20},
    ]
    return jsonify(spots)

@app.route('/spots8')
def get_spots8():
    spots = [
        {"name": "自販機", "latitude": 35.18414, "longitude": 137.1149616, "radius": 25},
        # {"name": "14号館", "latitude": 35.184473, "longitude": 137.110925, "radius": 20},
    ]
    return jsonify(spots)

@app.route('/spots9')
def get_spots9():
    spots = [
        {"name": "AITプラザ", "latitude": 35.18427735911909, "longitude": 137.11178969075672, "radius": 25},
        # {"name": "14号館", "latitude": 35.184473, "longitude": 137.110925, "radius": 20},
    ]
    return jsonify(spots)

@app.route('/spots10')
def get_spots10():
    spots = [
        {"name": "14号館", "latitude": 35.184473, "longitude": 137.110925, "radius": 20},
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
    app.run(debug=True, host='0.0.0.0', port=8000)