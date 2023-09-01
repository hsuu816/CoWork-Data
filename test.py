from flask import Flask, request, render_template, make_response


app = Flask(__name__)
	
@app.route('/')
def index():
	return 'welcome'


@app.route('/get_headers', methods=['POST'])
def get_headers():
    # 取得 POST 請求的 headers
    headers = request.headers
    # 輸出 headers 資訊
    return str(headers)




if __name__ == "__main__":
	app.run(debug=True, port=8000)
