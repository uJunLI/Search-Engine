from flask import Flask, render_template, request, json, jsonify
from search.get_screenshot import get_screenshot
from search.history_proc import history
from search.search_logic import search
from search.user_attribute import saveuser_Attribute
from search.user_recommendation import get_recommendations
from login_users_historys.login_logic import login_check

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search_endpoint():
    query = request.form.get('query')
    username = request.form.get('username')
    results = search(query,username)
    return json.dumps(results)

@app.route('/getrecommendations',methods=['POST'])
def get_recommendation():
    username = request.form.get('username')
    results = get_recommendations(username)
    return json.dumps(results)

@app.route('/showhistory',methods=['POST'])
def show_history():
    username = request.form['username']  # 或者 request.json['username']
    results = history(username)
    return json.dumps(results)

@app.route('/showscreenshot',methods=['POST'])
def show_screenshot():
    url = request.form.get('screenshot')
    img_stream = get_screenshot(url)
    if img_stream == 0:
        print("NO SUCH URL")
        return jsonify({'error': 'No such URL'})
    else:
        return jsonify({'img_stream': img_stream})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if login_check(username, password):
        return jsonify(success=True)
    else:
        return jsonify(success=False)

@app.route('/saveuserattribute',methods=['POST'])
def saveuser_attribute():
    data = request.get_json()
    username = data.get('username')
    userattribute = data.get('userAttribute')
    print("属性名是: ",userattribute)
    is_saved_successfully = saveuser_Attribute(username,userattribute)
    # 使用 jsonify 将字典转为 JSON 格式的响应对象
    return jsonify(success=is_saved_successfully)

if __name__ == '__main__':
    app.run(debug=True)

