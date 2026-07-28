import os
from dotenv import load_dotenv
load_dotenv()
import asyncio

# --- ASYNCIO LOOP FIX ---
try:
    loop = asyncio.get_running_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

from pyrogram import Client, filters
from pyrogram.errors import MessageNotModified
from pyrogram.enums import ParseMode

# --- FLASK KEEP ALIVE ---
from flask import Flask
from threading import Thread
web_app = Flask('')

@web_app.route('/')
def home():
    return "King Manager Bot is Running!"

def run_web():
    port = int(os.getenv("PORT", 10000))
    web_app.run(host='0.0.0.0', port=port)

Thread(target=run_web).start()

# --- BOT CONFIG ---
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Client("king_manager", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ====== 100+ ANIMATION DATABASE ======
ANIMATIONS = {
    # 1-10 Animals
    "cat": ["🐱","😺","😸","😹","😻","😽"],
    "dog": ["🐶","🐕","🦮","🐩","🐶"],
    "butterfly": ["🦋","🦋~","~🦋","🦋~~","~~🦋","🦋~~~"],
    "snake": ["🐍","🐍~","~🐍","🐍~~","~~🐍"],
    "ghost": ["👻","👻"," 👻 ","👻"],
    "lion": ["🦁","🦁","🦁"],
    "tiger": ["🐅","🐅","🐅"],
    "monkey": ["🐒","🙈","🙉","🙊"],
    "panda": ["🐼","🐼","🐼"],
    "fox": ["🦊","🦊","🦊"],

    # 11-20 Elements
    "fire": ["🔥","🔥","💥🔥💥","🔥"],
    "thunder": ["☁️","⛅","🌩️","⚡","💥"],
    "rain": ["🌤️","🌦️","🌧️","🌧️🌧️","☔"],
    "moon": ["🌑","🌒","🌓","🌔","🌕","🌖","🌗","🌘"],
    "sun": ["🌅","🌄","☀️","🌞"],
    "snow": ["❄️","🌨️","☃️","❄️"],
    "wind": ["🍃","🍃","💨","🍃"],
    "wave": ["🌊","🌊","🌊"],
    "cloud": ["☁️","☁️☁️","☁️☁️☁️"],
    "star": ["⭐","✨","🌟","⭐"],

    # 21-30 Love & Emotion
    "love": ["❤️","🧡","💛","💚","💙","💜","🖤","❤️"],
    "heartbreak": ["❤️","💔","💔","💔"],
    "cute": ["(｡♥‿♥｡)","So cute!"],
    "cry": ["(；´Д｀)","T_T","😭"],
    "laugh": ["😂","🤣","😆","😂"],
    "angry": ["😡","🤬","😠","😡"],
    "sad": ["😔","😞","😢","😔"],
    "happy": ["😊","😄","😁","😊"],
    "shy": ["😳","🙈","😊"],
    "cool": ["😎","🕶️","😎"],

    # 31-40 Tech
    "hacker": [f"Hacking [{'■'*i}{'□'*(10-i)}] {i*10}%" for i in range(11)],
    "error": ["Booting...0%","Booting...50%","ERROR!!! ⚠️","CRITICAL FAILURE","SYSTEM CRASH 💥"],
    "loading": ["[□]","[■□□]","[■■■□□□□□□]","[■■■■■□]","[■■■■■■■□]","[■■■■■■]"],
    "wifi": ["📶","📶📶","📶","📶📶📶📶"],
    "battery": ["🔋□","🔋■□","🔋■■□","🔋■■■"],
    "download": ["Downloading...0%","Downloading...50%","Downloading...100%","Done ✅"],
    "upload": ["Uploading...0%","Uploading...50%","Uploading...100%","Done ✅"],
    "search": ["🔍","🔍.","🔍..","🔍..."],
    "update": ["Updating...","Updating...","Update Complete ✅"],
    "restart": ["Restarting...","Restarting...","Restarted ✅"],

    # 41-50 Roast & Fun
    "fuck": [""". \n. \n. \n. \n.... \n...... \n**FUCK YOU!**"""],
    "myson": ["""(\\__/) \n(•ㅅ•) \n___ノ ヽ___ \nDon't talk to me or my son ever again."""],
    "tableflip": ["(╯°□°）╯︵ ┻━┻","TABLE FLIPPED!!!"],
    "shrug": ["¯\\_(ツ)_/¯","Idk man"],
    "pe": ["( ͡° ͜ʖ ͡°)","Pepe"],
    "facepalm": ["🤦","🤦‍♂️","🤦"],
    "clap": ["👏","👏","👏👏👏"],
    "thinking": ["🤔","🤔.","🤔..","🤔..."],
    "dance": ["💃","🕺","💃","🕺"],
    "sleep": ["😴","💤","😪","😴"],

    # 51-60 Items
    "rose": ["🌱","🌿","🥀","🌷","🌸","🌹"],
    "crown": ["👑","✨👑✨","KING 👑"],
    "diamond": ["💎","✨💎","💎✨💎"],
    "bike": ["🏍️","🏍️💨","💨🏍️💨"],
    "rocket": ["🚀","🚀","🚀💨","🌌🚀"],
    "pizza": ["🍕","🍕","🍕"],
    "burger": ["🍔","🍔","🍔"],
    "coffee": ["☕","☕","☕"],
    "cake": ["🎂","🎂","🎂"],
    "money": ["💰","💸","🤑","💰"],

    # 61-70 Festival
    "party": ["🎉","🎊","🥳","🎉"],
    "gift": ["🎁","🎁","🎁"],
    "balloon": ["🎈","🎈","🎈"],
    "christmas": ["🎄","🎄","🎄"],
    "diwali": ["🪔","✨🪔✨","🪔"],
    "holi": ["🌈","🎨","🌈"],
    "firework": ["🎆","🎇","✨","🎆"],
    "tada": ["🙌","🙌","🙌"],
    "confetti": ["🎊","🎊","🎊"],
    "celebrate": ["🥳","🎉","🥳"],

    # 71-80 Gaming
    "game": ["🎮","🎮","🎮"],
    "controller": ["🕹️","🕹️","🕹️"],
    "trophy": ["🏆","🏆","🏆"],
    "target": ["🎯","🎯","🎯"],
    "dice": ["🎲","🎲","🎲"],
    "chess": ["♟️","♟️","♟️"],
    "card": ["🃏","🃏","🃏"],
    "joystick": ["🕹️","🕹️","🕹️"],
    "esports": ["🏅","🏅","🏅"],
    "winner": ["🏅","🥇","🏆"],

    # 81-90 Transport
    "car": ["🚗","🚗💨","💨🚗"],
    "bus": ["🚌","🚌","🚌"],
    "train": ["🚆","🚆💨","💨🚆"],
    "plane": ["✈️","✈️💨","💨✈️"],
    "ship": ["🚢","🚢","🚢"],
    "truck": ["🚚","🚚💨","💨🚚"],
    "bicycle": ["🚲","🚲","🚲"],
    "taxi": ["🚕","🚕💨","💨🚕"],
    "ambulance": ["🚑","🚑","🚑"],
    "police": ["🚓","🚓💨","💨🚓"],

    # 91-100 Misc
    "magic": ["✨","🔮","✨"],
    "book": ["📖","📚","📖"],
    "music": ["🎵","🎶","🎵"],
    "camera": ["📷","📷","📷"],
    "phone": ["📱","📱","📱"],
    "laptop": ["💻","💻","💻"],
    "watch": ["⌚","⌚","⌚"],
    "glasses": ["👓","👓","👓"],
    "hat": ["🎩","🎩","🎩"],
    "ring": ["💍","💍","💍"],
}

# ====== AUTO HANDLER ======
async def animate(message, frames, delay=0.3):
    msg = await message.reply_text(frames[0])
    for frame in frames[1:]:
        await asyncio.sleep(delay)
        try: await msg.edit_text(frame)
        except MessageNotModified: pass
    await msg.edit_text(f"{frames[-1]} ✅")

for cmd, frames in ANIMATIONS.items():
    @app.on_message(filters.command(cmd) & filters.me)
    async def handler(_, m, f=frames):
        await animate(m, f)

print(f"ISHIKA Manager Bot Started ✅ {len(ANIMATIONS)} Commands Loaded")
app.run()
