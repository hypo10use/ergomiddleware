from flask import Flask, render_template
import requests

app = Flask(__name__)


@app.route('/')
def index():
    r=requests.post("http://116.203.30.147:9053/", data={'key': 'value'})
    return render_template('index.html')





if __name__ == '__main__': app.run(debug=True)