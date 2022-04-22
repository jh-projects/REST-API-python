from flask import Flask
from flask import request, jsonify, make_response




def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def createApp(test_config=None):
	app = Flask(__name__, instance_relative_config=True)
	app.config.from_mapping(SECRET_KEY='dev', DATABASE="inventory.db", DEBUG=True)
	
	
	@app.route('/api/login', methods=['POST', 'OPTIONS'])
	def login():
		if request.method == "OPTIONS": # CORS preflight
			return _build_cors_preflight_response()
		elif request.method == "POST":
			data = request.json
			response = jsonify(data)
			response.headers.add('Access-Control-Allow-Origin', '*')
			print("here")
			print(response)
			return response
	
	def _build_cors_preflight_response():
		response = make_response()
		response.headers.add("Access-Control-Allow-Origin", "*")
		response.headers.add('Access-Control-Allow-Headers', "*")
		response.headers.add('Access-Control-Allow-Methods', "*")
		return response
	

	@app.route('/api/list/all', methods=['GET'])
	def api_all():
		conn = sqlite3.connect('inventory.db')
		conn.row_factory = dict_factory
		cur = conn.cursor()
		all_books = cur.execute('SELECT * FROM items;').fetchall()

		return jsonify(all_books)
		
	@app.route('/', methods=['GET'])
	def home():
		return "<h1>Distant Reading Archive</h1><p>This site is a prototype API for distant reading of science fiction novels.</p>"

	app.run()

createApp()