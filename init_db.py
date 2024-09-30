import sqlite3

# 连接到SQLite数据库
conn = sqlite3.connect('devices.db')

# 创建一个游标对象
cursor = conn.cursor()

# 创建用户表
cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password_hash TEXT
        )
    ''')
print("Created 'users' table.")
# 创建设备表
cursor.execute('''
        CREATE TABLE IF NOT EXISTS devices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            ip_address TEXT,
            login_status INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
print("Created 'devices' table.")
# 创建令牌表
cursor.execute('''
        CREATE TABLE IF NOT EXISTS tokens (
            token TEXT PRIMARY KEY,
            user_id INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
print("Created 'tokens' table.")
conn.commit()
print("Database initialized.")

# 关闭游标和连接
cursor.close()
conn.close()