from flask import Flask, request, jsonify, g
import sqlite3
import requests
import jwt
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

JWT_SECRET = '123'  # JWT 密钥


def get_db():
    if 'db' not in g:
        print("Connecting to database...")
        g.db = sqlite3.connect('devices.db')
        g.db.row_factory = sqlite3.Row  # 使查询返回字典形式
        print("Connected to database.")
    return g.db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


# 鉴权装饰器
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # 从请求头中获取 Token
        if "Authorization" in request.headers:
            auth_header = request.headers["Authorization"]
            # 预期的格式是 'Bearer <token>'
            parts = auth_header.split()
            if len(parts) == 2 and parts[0] == "Bearer":
                token = parts[1]
        if not token:
            return jsonify({"status": "error", "message": "Token is missing!"}), 401
        try:
            # 解码 Token
            data = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            user_id = data["user_id"]
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            user = cursor.fetchone()
            cursor.close()
            if not user:
                return jsonify({"status": "error", "message": "User not found!"}), 401
            # 将用户信息保存到上下文中
            g.user = user
        except jwt.ExpiredSignatureError:
            return jsonify({"status": "error", "message": "Token has expired!"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"status": "error", "message": "Invalid token!"}), 401
        return f(*args, **kwargs)

    return decorated


# 用户注册
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"status": "error", "message": "Username and password are required."}), 400
    db = get_db()
    cursor = db.cursor()
    password_hash = generate_password_hash(password)
    try:
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, password_hash))
        db.commit()
        cursor.close()
        return jsonify({"status": "success", "message": "User registered successfully."}), 201
    except sqlite3.IntegrityError:
        cursor.close()
        return jsonify({"status": "error", "message": "Username already exists."}), 400


# 用户登录
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    cursor.close()
    if user and check_password_hash(user["password_hash"], password):
        # 生成 Token
        token = jwt.encode({
            "user_id": user["id"],
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }, JWT_SECRET, algorithm="HS256")
        return jsonify({"status": "success", "token": token})
    else:
        return jsonify({"status": "error", "message": "Invalid username or password."}), 401


# 绑定设备
@app.route("/bind", methods=["POST"])
@token_required
def bind_device():
    data = request.get_json()
    device_id = data.get("device_id")
    ip_address = data.get("ip_address")
    if not device_id or not ip_address:
        return jsonify({"status": "error", "message": "Device ID and IP address are required."}), 400
    user_id = g.user["id"]
    db = get_db()
    cursor = db.cursor()
    # 检查设备ID是否已存在
    cursor.execute("SELECT * FROM devices WHERE id = ? AND user_id = ?", (device_id, user_id))
    existing_device = cursor.fetchone()
    if existing_device:
        cursor.close()
        return jsonify({"status": "error", "message": "Device ID already exists."}), 400
    # 插入新设备
    cursor.execute("INSERT INTO devices (id, user_id, ip_address, login_status) VALUES (?, ?, ?, ?)",
                   (device_id, user_id, ip_address, 0))
    db.commit()
    cursor.close()
    return jsonify({"status": "success", "message": "Device bound successfully."}), 201


# 查看已绑定设备列表
@app.route("/devices", methods=["GET"])
@token_required
def list_devices():
    user_id = g.user["id"]
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, ip_address, login_status FROM devices WHERE user_id = ?", (user_id,))
    devices = cursor.fetchall()
    cursor.close()
    device_list = []
    for device in devices:
        device_list.append({
            "id": device["id"],
            "ip_address": device["ip_address"],
            "login_status": bool(device["login_status"])
        })
    return jsonify({"status": "success", "devices": device_list})


# 登录设备
@app.route("/devices/<int:device_id>/login", methods=["POST"])
@token_required
def login_device(device_id):
    user_id = g.user["id"]
    username = g.user["username"]
    data = request.get_json()
    ip_address = data.get("ip_address")  # 从请求体获取 IP 地址
    db = get_db()
    cursor = db.cursor()
    if not ip_address:
        # 如果未提供 IP 地址，从数据库中获取
        cursor.execute("SELECT ip_address FROM devices WHERE id = ? AND user_id = ?", (device_id, user_id))
        result = cursor.fetchone()
        if result:
            ip_address = result["ip_address"]
        else:
            cursor.close()
            return jsonify({"status": "error", "message": "Device not found."}), 404
    cursor.close()
    # 构造请求数据
    request_data = {
        # "username": username,
        "username": "rickon0929",  # 这里统一用申请到的用户名监听
        "ip": ip_address
    }
    try:
        # 调用校园网登录 API
        response = requests.post("https://yxms.byr.ink/api/login", json=request_data)
        if response.status_code == 200:
            resp_json = response.json()
            if resp_json.get("success"):
                # 更新登录状态
                cursor = db.cursor()
                cursor.execute("UPDATE devices SET login_status = ? WHERE id = ? AND user_id = ?",
                               (1, device_id, user_id))
                db.commit()
                cursor.close()
                return jsonify({"status": "success", "message": "Device logged in successfully."})
            else:
                return jsonify({"status": "error", "message": resp_json.get("message")}), 400
        else:
            return jsonify({"status": "error", "message": "Failed to connect to login API."}), 500
    except requests.exceptions.RequestException as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# 登出设备
@app.route("/devices/<int:device_id>/logout", methods=["POST"])
@token_required
def logout_device(device_id):
    user_id = g.user["id"]
    db = get_db()
    cursor = db.cursor()
    cursor.execute("UPDATE devices SET login_status = ? WHERE id = ? AND user_id = ?", (0, device_id, user_id))
    db.commit()
    cursor.close()
    return jsonify({"status": "success", "message": "Device logged out successfully."})


# 解绑设备
@app.route("/devices/<int:device_id>/unbind", methods=["POST"])
@token_required
def unbind_device(device_id):
    user_id = g.user["id"]
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM devices WHERE id = ? AND user_id = ?", (device_id, user_id))
    db.commit()
    cursor.close()
    return jsonify({"status": "success", "message": "Device unbound successfully."})


if __name__ == "__main__":
    print("starting server...")
    app.run(debug=True)
