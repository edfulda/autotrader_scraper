from app import app
from flask import jsonify

from app.scraper import Scraper

@app.route('/')
@app.route('/index')
def index():
    return "Hello, World!"

@app.route('/cars')
def cars():
    s = Scraper("BMW", "M5")
    return jsonify(s.get_full_info())
