from flask import Flask
app = Flask('')

@app.route('/')
def home():
    return "Bot is Alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

from threading import Thread
def keep_alive():
    t = Thread(target=run)
    t.start()
