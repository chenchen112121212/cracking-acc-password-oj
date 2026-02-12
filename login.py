from flask import Flask, request, jsonify
import requests
from flask_cors import CORS
# 安装python-dotenv库读取.env文件：pip install python-dotenv
from dotenv import load_dotenv
import os

# 加载.env配置文件
load_dotenv()

app = Flask(__name__)
# 强化跨域配置
CORS(
    app,
    origins="*",
    methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept"],
    supports_credentials=True
)

@app.route('/api/oj-login', methods=['POST', 'OPTIONS'])
def oj_login():
    # 处理OPTIONS预检请求
    if request.method == 'OPTIONS':
        return jsonify({'status': 200}), 200
    
    # 获取前端参数
    req_data = request.get_json(silent=True)
    if not req_data or 'username' not in req_data or 'password' not in req_data:
        return jsonify({'status': 400, 'msg': '缺少用户名或密码参数'}), 400

    # 从.env读取OJ登录接口地址
    oj_login_url = os.getenv('OJ_LOGIN_API')
    post_data = {
        'username': req_data['username'],
        'password': req_data['password']
    }

    try:
        session = requests.Session()
        response = session.post(oj_login_url, json=post_data, timeout=10)
        resp = jsonify(response.json())
        # 透传Cookie
        if 'Set-Cookie' in response.headers:
            resp.headers['Set-Cookie'] = response.headers['Set-Cookie']
        return resp, response.status_code
    except requests.exceptions.Timeout:
        return jsonify({'status': 504, 'msg': '请求OJ接口超时'}), 504
    except requests.exceptions.ConnectionError:
        return jsonify({'status': 503, 'msg': '无法连接到OJ服务器'}), 503
    except Exception as e:
        return jsonify({'status': 500, 'msg': f'服务器错误：{str(e)}'}), 500

if __name__ == '__main__':
    # 从.env读取本地后端地址（拆分host和port）
    local_backend = os.getenv('LOCAL_BACKEND_URL').split('://')[1].split(':')
    host = local_backend[0]
    port = int(local_backend[1].split('/')[0])
    app.run(host=host, port=port, debug=False, use_reloader=False)