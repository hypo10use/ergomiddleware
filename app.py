from flask import Flask, render_template, request
import requests

app = Flask(__name__)


@app.route('/ergoscript', methods = ['GET'])
def compile_ergoscript():
    r=requests.post("http://116.203.30.147:9053/", data={'source': request.data})
    return r.text





if __name__ == '__main__': app.run(debug=True)