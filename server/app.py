from flask import request, jsonify, render_template, abort, redirect, url_for
from createApp import app
from loguru import logger
from waitress import serve
# import modéle


if __name__ == "__main__":
    app.run("0.0.0.0", debug=True)
    # serve(app, host='0.0.0.0', port=5000, threads=8) #WAITRESS!