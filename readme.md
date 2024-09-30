# 设备管理后端

## 简介

这是一个设备管理后端项目，基于 Flask 框架开发。该项目支持设备的状态管理和 API 功能，使用 `requests`, `pyjwt`, `Werkzeug` 和 `flask_cors` 等库。

## 环境设置

### 1. 创建虚拟环境

在开始之前，请确保你已经安装了 Python 3.x 版本。

1. 打开终端，进入你的项目文件夹：
   ```bash
   cd flaskProject
   ```

2. 创建一个虚拟环境：
   ```bash
   python3 -m venv byrenv
   ```

3. 激活虚拟环境：
   - macOS/Linux:
     ```bash
     source byrenv/bin/activate
     ```
   - Windows:
     ```bash
     .\byrenv\Scripts\activate
     ```

4. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

`requirements.txt` 包含以下库：
- `requests`
- `pyjwt`
- `Werkzeug`
- `flask_cors`

### 2. 初始化数据库

在运行后端应用程序之前，你需要先初始化数据库。请确保数据库已配置正确。

1. 运行数据库初始化脚本：
   ```bash
   python init_db.py
   ```

### 3. 启动后端服务

1. 启动 Flask 应用：
   ```bash
   python app.py
   ```

2. 成功启动后，你将看到如下信息：
   ```bash
   FLASK_APP = app.py
   FLASK_ENV = development
   FLASK_DEBUG = 0
   In folder /Users/zhangyukun/Desktop/CodeStudy/flaskProject
   /Users/zhangyukun/Desktop/CodeStudy/byr/byrenv/bin/python -m flask run
    * Serving Flask app 'app.py'
    * Debug mode: off
   WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
    * Running on http://127.0.0.1:5000
   Press CTRL+C to quit
   ```

3. 服务运行成功后，你可以通过 `http://127.0.0.1:5000` 访问后端 API。

### 4. 停止后端服务

- 使用 `Ctrl + C` 停止正在运行的 Flask 开发服务器。

## 注意事项

- **开发环境：** 此项目在开发环境下运行，请勿用于生产环境。
- **虚拟环境：** 每次工作时，请确保已激活虚拟环境。

# 设备管理前端

## 启动说明
前端页面是front.html文件

使用浏览器打开即可访问