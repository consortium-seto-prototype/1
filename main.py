from flask import Flask, request, render_template, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
# from database import db, User, Stamp
from database import db, User, Spot, Stamp

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
login_manager.login_message = "※ ログインが必要です。ログインしてください。"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def set_spots():
    spots = [
        {"name": "AITプラザ", "order_number": 1, "lat": 35.198600, "lng": 137.093998},
        {"name": "愛和食堂", "order_number": 2, "lat": 35.184473, "lng": 137.110925},
        {"name": "キャリアセンター", "order_number": 3, "lat": 35.184473, "lng": 137.110925},
        {"name": "14号館", "order_number": 4, "lat": 35.184473, "lng": 137.110925},
    ]

    # Spot に同じ名前のスポットがなければ追加（重複防止）
    for s in spots:
        existing = Spot.query.filter_by(name=s['name']).first()
        if not existing:
            new_spot = Spot(
                name=s['name'],
                order_number=s['order_number'],
                lat=s['lat'],
                lng=s['lng'],
            )
            db.session.add(new_spot)
    db.session.commit()

# 初回だけ実行してデータベース作成
with app.app_context():
    db.create_all()
    set_spots()


# -------------------------------------------スタンプを保存する関数-------------------------------------------
# @login_required
def save_stamp(stamp_num):
    # QRコードを読み取るため、ユーザがログインしているかを確認する
    if current_user.is_authenticated:
        # ユーザーのスタンプ情報を取得（なければデフォルト0）
        stamp = Stamp.query.filter_by(user_id=current_user.id).first()
        total_stamps = stamp.stamp_count if stamp else 0

        # それぞれのスタンプの取得状況を変数に代入
        stamp_status = {}
        stamp_status[0] = stamp.stamp_1 if stamp and stamp.stamp_1 is not None else False
        stamp_status[1] = stamp.stamp_2 if stamp and stamp.stamp_2 is not None else False
        stamp_status[2] = stamp.stamp_3 if stamp and stamp.stamp_3 is not None else False
        stamp_status[3] = stamp.stamp_4 if stamp and stamp.stamp_4 is not None else False

        # すでに取得済みの場合
        if stamp_status[stamp_num - 1] :
            print(f"{stamp_num}番目のスタンプは取得済みです。")
            return (stamp_num)

        if not stamp:
            stamp = Stamp(user_id=current_user.id, stamp_count=1)
            # setattr(stamp, "stamp_1", True) # 最初のスタンプをtrueに
            setattr(stamp, f"stamp_{stamp_num}", True)
            db.session.add(stamp)
            # print("1つ目のスタンプを取得しました。")
            print(f"{stamp_num}番目のスタンプを取得しました。")

        else:
            if stamp.stamp_count < 4:
                stamp.stamp_count += 1  # スタンプを1つ増やす
                setattr(stamp, f"stamp_{stamp_num}", True)
                # print("スタンプを取得しました。")
                print(f"{stamp_num}番目のスタンプを取得しました。")
            else:
                print("スタンプは4個までです。")
                return jsonify({"message": "スタンプは4個までです!", "redirect": None}), 400
                return redirect(url_for('stamp'))

        db.session.commit()
        
        total_stamps = stamp.stamp_count if stamp else 0
        print("スタンプの合計:", total_stamps) 
    else:
        # ログインしていなかったらログイン画面にリダイレクト
        return redirect(url_for('home'))

    return(stamp_num)


# -------------------------------------------ホーム画面-------------------------------------------
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        # remember = request.form.get('remember') == 'on'

        user = User.query.filter_by(name=name).first()
        if user and user.check_password(password):
            # rememberでログイン状態を保持している
            login_user(user, remember=True)
            return redirect(url_for('stamp'))
            # return redirect(url_for('test2'))
        else:
            flash("※ユーザ名かパスワードが間違っています。", "danger")

    return render_template('home.html')


# ---------------------------------QRスタンプ読み取った際ログアウト状態だった時用のホーム画面---------------------------------
@app.route('/home2', methods=['GET', 'POST'])
def home2():
    # QRで読み取ったスタンプの番号をhtmlから取得
    stp_num = request.args.get('stp_num', default=0, type=int)

    if request.method == 'GET':
        flash("※ ログインが必要です。ログインしてください。", "warning")

    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']

        user = User.query.filter_by(name=name).first()
        if user and user.check_password(password):
            # rememberでログイン状態を保持している
            login_user(user, remember=True)
            if stp_num == 1:
                return redirect(url_for('test_get_stamp'))
            elif stp_num == 2:
                return redirect(url_for('test_get_stamp2'))
            elif stp_num == 3:
                return redirect(url_for('test_get_stamp3'))
            elif stp_num == 4:
                return redirect(url_for('test_get_stamp4'))
            elif stp_num == 5:
                return redirect(url_for('test_get_stamp5'))
            elif stp_num == 6:
                return redirect(url_for('test_get_stamp6'))
            else :
                # QRコードを読み取らずにアクセスした場合(ユーザは使わないはず)
                # flash("※ アクセス権がありません。", "danger")
                return render_template('test2.html')

        else:
            flash("※ ユーザ名かパスワードが間違っています。", "danger")
            return render_template('home2.html', stp_num=stp_num)

    return render_template('home2.html', stp_num=stp_num)


# -------------------------------------------ユーザ登録用の画面-------------------------------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']

        if User.query.filter_by(name=name).first():
            flash("※ ユーザー名が既に存在します", "danger")
        else:
            new_user = User(name=name)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()

            # Stampを自動で作成
            new_stamp = Stamp(user_id=new_user.id)
            db.session.add(new_stamp)
            db.session.commit()

            flash("登録完了! ログインしてください", "success")
            return redirect(url_for('home'))

    return render_template('register.html')


# -------------------------------------------ログアウト画面-------------------------------------------
@app.route('/logout')
@login_required
def logout():
    logout_user()
    # flash("ログアウトしました", "info")
    return redirect(url_for('home'))


# -------------------------------------------スタンプラリー画面-------------------------------------------
@app.route('/stamp', methods=['GET', 'POST'])
@login_required
def stamp():
    # ユーザーのスタンプ情報を取得（なければデフォルト0）
    stamp = Stamp.query.filter_by(user_id=current_user.id).first()
    total_stamps = stamp.stamp_count if stamp else 0
    print("スタンプの合計:", total_stamps)
    info = ["", "2", "3", "4", "", "2", "3", "4", "", "2"] 

    # それぞれのスタンプの取得状況を変数に代入
    stamp_status = {}
    stamp_status[0] = stamp.stamp_1 if stamp and stamp.stamp_1 is not None else False
    stamp_status[1] = stamp.stamp_2 if stamp and stamp.stamp_2 is not None else False
    stamp_status[2] = stamp.stamp_3 if stamp and stamp.stamp_3 is not None else False
    stamp_status[3] = stamp.stamp_4 if stamp and stamp.stamp_4 is not None else False

    if stamp_status[0] == 0:
        stp_num = 1
        return render_template('stamp.html', stp_num=stp_num)
    if stamp_status[1] == 0:
        stp_num = 2
        return render_template('stamp2.html', stp_num=stp_num)
    if stamp_status[2] == 0:
        stp_num = 3
        return render_template('stamp3.html', stp_num=stp_num)
    if stamp_status[3] == 0:
        stp_num = 4
        return render_template('stamp4.html', stp_num=stp_num)
    if total_stamps == 4:
        return render_template('index.html')
        

# -----------------------------------取得したスタンプをデータベースに追加する処理-----------------------------------
# 取得したスタンプをデータベースに追加する処理
@app.route('/get_stamp', methods=['POST'])
@login_required
def get_stamp():
    # ユーザーのスタンプ情報を取得（なければデフォルト0）
    stamp = Stamp.query.filter_by(user_id=current_user.id).first()
    total_stamps = stamp.stamp_count if stamp else 0

    data = request.get_json()
    stp_num = data.get('stp_num')
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    print("スタンプ番号：", stp_num, "緯度：", latitude, "経度：", longitude)

    if request.method == 'POST':
                
        get_stamp = save_stamp(stp_num)
        print("取得したスタンプ：", get_stamp)
        return jsonify({
            "message": "スタンプを獲得しました！",
            "redirect": "/info" + str(get_stamp)
            })
        
        
        # if not stamp:
        #     stamp = Stamp(user_id=current_user.id, stamp_count=1)
        #     setattr(stamp, 'stamp_1', True)
        #     db.session.add(stamp)
        #     print("1つ目のスタンプを取得しました。")
        # else:
        #     if stamp.stamp_count < 4:
        #         stamp.stamp_count += 1  # スタンプを1つ増やす
        #         # setattr(stamp, 'stamp_1', True)
        #         print("スタンプを取得しました。")
        #         # print(stamp.stamp_count + "個スタンプを取得しました。")
        #     else:
        #         print("スタンプは4個までです。")
        #         return jsonify({"message": "スタンプは4個までです!", "redirect": None}), 400
        #         return redirect(url_for('stamp'))

        # db.session.commit()
        # flash("スタンプを獲得しました！", "success")
        # print("スタンプを取得しました。")


        # return jsonify({"message": "スタンプを獲得しました！", "redirect": info[stamp.stamp_count - 1]})
        # return redirect(url_for('info_home'))


# -------------------------------------------カードゲーム画面-------------------------------------------
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


# ----------------------------------------情報表示するホーム画面----------------------------------------
@app.route('/info_home')
@login_required
def info_home():
    stamp = Stamp.query.filter_by(user_id=current_user.id).first()
    total_stamps = stamp.stamp_count if stamp else 0

    # それぞれのスタンプの取得状況を変数に代入
    stamp1_status = stamp.stamp_1 if stamp and stamp.stamp_1 is not None else False
    stamp2_status = stamp.stamp_2 if stamp and stamp.stamp_2 is not None else False
    stamp3_status = stamp.stamp_3 if stamp and stamp.stamp_3 is not None else False
    stamp4_status = stamp.stamp_4 if stamp and stamp.stamp_4 is not None else False

    # print(stamp1_status)
    # print(stamp2_status)
    # print(stamp3_status)
    # print(stamp4_status)
    # print(stamp5_status)
    # print(stamp6_status)

    return render_template('info_home.html', total_stamps=total_stamps, stamp1_status=stamp1_status, stamp2_status=stamp2_status, stamp3_status=stamp3_status, stamp4_status=stamp4_status)


# ----------------------------------------情報表示画面1----------------------------------------
@app.route('/info1')
@login_required
def info1():
    stamp = Stamp.query.filter_by(user_id=current_user.id).first()
    total_stamps = stamp.stamp_count if stamp else 0

    return render_template('info1.html', total_stamps=total_stamps)

# ----------------------------------------情報表示画面2----------------------------------------
@app.route('/info2')
@login_required
def info2():
    stamp = Stamp.query.filter_by(user_id=current_user.id).first()
    total_stamps = stamp.stamp_count if stamp else 0

    return render_template('info2.html', total_stamps=total_stamps)

# ----------------------------------------情報表示画面3----------------------------------------
@app.route('/info3')
@login_required
def info3():
    stamp = Stamp.query.filter_by(user_id=current_user.id).first()
    total_stamps = stamp.stamp_count if stamp else 0

    return render_template('info3.html', total_stamps=total_stamps)

# ----------------------------------------情報表示画面4----------------------------------------
@app.route('/info4')
@login_required
def info4():
    stamp = Stamp.query.filter_by(user_id=current_user.id).first()
    total_stamps = stamp.stamp_count if stamp else 0

    return render_template('info4.html', total_stamps=total_stamps)


# -------------------------------------テスト用（QRコード）-------------------------------------
@app.route('/test')
@login_required
def index():
    return render_template('test.html')


# -----------------------------------研究室紹介用のスタンプラリー画面-----------------------------------
@app.route('/test2', methods=['GET', 'POST'])
@login_required
def test2():
    stamp = Stamp.query.filter_by(user_id=current_user.id).first()
    total_stamps = stamp.stamp_count if stamp else 0

    # if request.method == 'GET':
    #     save_stamp()
    #     total_stamps = stamp.stamp_count if stamp else 0
    #     if total_stamps != 1 :
    #         info_num = "info" + str(info[total_stamps])
    #     return redirect(url_for(info_num))

    return render_template('test2.html')


# -------------------------------------研究室紹介用のスタンプDB保存する処理（スタンプ6個分）-------------------------------------
@app.route('/test_get_stamp', methods=['GET'])
def test_get_stamp():
    # ユーザがログインしているかどうかを確認
    if current_user.is_authenticated:
        stamp = Stamp.query.filter_by(user_id=current_user.id).first()
        total_stamps = stamp.stamp_count if stamp else 0
        stamp_number = 1

        get_stamp = save_stamp(stamp_number)
        total_stamps = stamp.stamp_count if stamp else 0
        info_num = "info" + str(get_stamp)
        return redirect(url_for(info_num))
    # ログアウト状態していなければ
    else :
        stamp_number = 1
        print("ログインしていません。", stamp_number)
        return redirect(url_for('home2', stp_num=stamp_number))

@app.route('/test_get_stamp2', methods=['GET'])
def test_get_stamp2():
    if current_user.is_authenticated:
        stamp = Stamp.query.filter_by(user_id=current_user.id).first()
        total_stamps = stamp.stamp_count if stamp else 0
        stamp_number = 2

        get_stamp = save_stamp(stamp_number)
        total_stamps = stamp.stamp_count if stamp else 0
        info_num = "info" + str(get_stamp)
        return redirect(url_for(info_num))
    else :
        stamp_number = 2
        print("ログインしていません。", stamp_number)
        return redirect(url_for('home2', stp_num=stamp_number))

@app.route('/test_get_stamp3', methods=['GET'])
def test_get_stamp3():
    if current_user.is_authenticated:
        stamp = Stamp.query.filter_by(user_id=current_user.id).first()
        total_stamps = stamp.stamp_count if stamp else 0
        stamp_number = 3

        get_stamp = save_stamp(stamp_number)
        total_stamps = stamp.stamp_count if stamp else 0
        info_num = "info" + str(get_stamp)
        return redirect(url_for(info_num))
    else :
        stamp_number = 3
        print("ログインしていません。", stamp_number)
        return redirect(url_for('home2', stp_num=stamp_number))

@app.route('/test_get_stamp4', methods=['GET'])
def test_get_stamp4():
    if current_user.is_authenticated:
        stamp = Stamp.query.filter_by(user_id=current_user.id).first()
        total_stamps = stamp.stamp_count if stamp else 0
        stamp_number = 4

        get_stamp = save_stamp(stamp_number)
        total_stamps = stamp.stamp_count if stamp else 0
        info_num = "info" + str(get_stamp)
        return redirect(url_for(info_num))
    else :
        stamp_number = 4
        print("ログインしていません。", stamp_number)
        return redirect(url_for('home2', stp_num=stamp_number))

@app.route('/test_get_stamp5', methods=['GET'])
def test_get_stamp5():
    if current_user.is_authenticated:
        stamp = Stamp.query.filter_by(user_id=current_user.id).first()
        total_stamps = stamp.stamp_count if stamp else 0
        stamp_number = 5

        get_stamp = save_stamp(stamp_number)
        total_stamps = stamp.stamp_count if stamp else 0
        info_num = "info" + str(get_stamp)
        return redirect(url_for(info_num))
    else :
        stamp_number = 5
        print("ログインしていません。", stamp_number)
        return redirect(url_for('home2', stp_num=stamp_number))

@app.route('/test_get_stamp6', methods=['GET'])
def test_get_stamp6():
    if current_user.is_authenticated:
        stamp = Stamp.query.filter_by(user_id=current_user.id).first()
        total_stamps = stamp.stamp_count if stamp else 0
        stamp_number = 6

        get_stamp = save_stamp(stamp_number)
        total_stamps = stamp.stamp_count if stamp else 0
        info_num = "info" + str(get_stamp)
        return redirect(url_for(info_num))
    else :
        stamp_number = 6
        print("ログインしていません。", stamp_number)
        return redirect(url_for('home2', stp_num=stamp_number))


# ----------------------------------------↓スタンプラリーの座標↓----------------------------------------
@app.route('/spots')
def get_spots():
    spots = [
        # {"name": "セブン", "latitude": 35.18421, "longitude": 137.11190, "radius": 20},
        {"name": "14号館", "latitude": 35.184473, "longitude": 137.110925, "radius": 20},
        # {"name": "愛工大", "latitude": 35.1835, "longitude": 137.1130, "radius": 50},
        # {"name": "浅草寺", "latitude": 35.7148, "longitude": 139.7967, "radius": 400},
        # {"name": "テスト用", "latitude": 35.198600, "longitude": 137.093998, "radius": 30}

        # {"name": "AITプラザ", "order_number": 1, "lat": 35.198600, "lng": 137.093998},
        # {"name": "愛和食堂", "order_number": 2, "lat": 35.184473, "lng": 137.110925},
        # {"name": "キャリアセンター", "order_number": 3, "lat": 35.184473, "lng": 137.110925},
        # {"name": "14号館", "order_number": 4, "lat": 35.184473, "lng": 137.110925},
    ]

    # Spot に同じ名前のスポットがなければ追加（重複防止）
    # for s in spots:
    #     existing = Spot.query.filter_by(name=s['name']).first()
    #     if not existing:
    #         new_spot = Spot(
    #             name=s['name'],
    #             order_number=s['order_number'],
    #             lat=s['lat'],
    #             lng=s['lng'],
    #         )
    #         db.session.add(new_spot)
    # db.session.commit()

    # # order_number = 1 のスポットをDBから取得して返す
    # spot = Spot.query.filter_by(order_number=1).first()
    # if not spot:
    #     return jsonify({"error": "order_number=1 のスポットが見つかりません"}), 404

    # response = {
    #     "name": spot.name,
    #     "latitude": spot.lat,
    #     "longitude": spot.lng,
    #     "radius": 30  # 半径の設定はお好みで
    # }

    # return jsonify(response)
    return jsonify(spots)

@app.route('/spots2')
def get_spots2():
    spots = [
        # {"name": "アロハカフェ", "latitude": 35.183932, "longitude": 137.1115, "radius": 20},
        {"name": "14号館", "latitude": 35.184473, "longitude": 137.110925, "radius": 20},
        # {"name": "テスト用", "latitude": 35.198600, "longitude": 137.093998, "radius": 30}
    ]
    return jsonify(spots)

@app.route('/spots3')
def get_spots3():
    spots = [
        # {"name": "セブンイレブン", "latitude": 35.18421, "longitude": 137.11190, "radius": 20},
        {"name": "14号館", "latitude": 35.184473, "longitude": 137.110925, "radius": 20},
        # {"name": "テスト用", "latitude": 35.198600, "longitude": 137.093998, "radius": 30}
    ]
    return jsonify(spots)

@app.route('/spots4')
def get_spots4():
    spots = [
        # {"name": "愛和食堂", "latitude": 35.18422, "longitude": 137.1123, "radius": 20},
        {"name": "14号館", "latitude": 35.184473, "longitude": 137.110925, "radius": 20},
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
# ----------------------------------------↑スタンプラリーの座標↑----------------------------------------


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)