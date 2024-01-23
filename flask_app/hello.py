#!/usr/bin/python3

from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello this project is necessary for Pik&Go!'

if __name__ == "__main__":
    app.run(debug=True)

