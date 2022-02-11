from flask import Flask, render_template, request
import requests, json

app = Flask(__name__)


@app.route('/ergoscript', methods = ['POST'])
def compile_ergoscript():
    headers = {'content-type': 'application/json'}
    r=requests.post("http://116.203.30.147:9053/script/p2sAddress", data=json.dumps({'source': request.data}), headers=headers)
    return r.text





if __name__ == '__main__': app.run(debug=True)