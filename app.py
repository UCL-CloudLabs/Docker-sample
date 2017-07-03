from flask import Flask, render_template
import random

app = Flask(__name__)

# list of cat images
images = [
    "http://i.imgur.com/MljgJNN.gif",
    "http://i.imgur.com/s7Muc32.gif",
    "https://media0.giphy.com/media/CNf1SeN6fcBuo/giphy.gif",
    "https://media4.giphy.com/media/N5eUbQfWEzLqg/giphy.gif",
    "https://media0.giphy.com/media/DwtfcPtkcnCtq/giphy.gif"
]

@app.route('/')
def index():
    url = random.choice(images)
    return render_template('index.html', url=url)

if __name__ == "__main__":
    app.run(host="0.0.0.0")
