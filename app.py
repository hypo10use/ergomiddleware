from flask import Flask, render_template, request
import requests, json
from flask_cors import CORS, cross_origin

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/ergoscript', methods = ['POST'])
@cross_origin()
def compile_ergoscript():
    headers = {'content-type': 'application/json'}
    json_data = request.json
    script = json_data['script']
    r=requests.post("http://116.203.30.147:9053/script/p2sAddress", data=json.dumps({'source': script}), headers=headers)
    return r.text





if __name__ == '__main__': app.run(debug=True)