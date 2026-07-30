import os
import asyncio
import datetime
from dotenv import load_dotenv
load_dotenv()

from pyrogram import Client
from pyrogram.raw.functions.account import UpdateProfile
from pyrogram.errors import FloodWait, RPCError

from PIL import Image, ImageDraw, ImageFont

# --- RAILWAY KEEP ALIVE ---
from flask import Flask
from threading import Thread
app_flask = Flask('')
@app_flask.route('/')
def home(): return "OK"
def run_flask(): app_flask.run(host='0.0.0.0', port=int(os.getenv("PORT", 8080)))
Thread(target=run_flask, daemon=True).start()

# --- CONFIG ---
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")

USER_NAME = "Kartik Nishad 👑" # Yaha naam daal de
COLORS = ["#FFD700", "#1E90FF", "#FF4500", "#32CD32", "#8A2BE2", "#FF1493", "#00FFFF", "#FF0000", "#FF8C00", "#9400D3"]

client = Client("kartik_session", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

def make_dp(color_hex):
    size = 512
    img = Image.new("RGB", (size, size), color_hex)
    draw = ImageDraw.Draw(img)

    # Gradient
    center = size // 2
    r0,g0,b0 = int(color_hex[1:3],16), int(color_hex[3:5],16), int(color_hex[5:7],16)
    for i in range(center, 0, -1):
        r = min(255, r0 + int(200 * (center-i)/center))
        g = min(255, g0 + int(200 * (center-i)/center))
        b = min(255, b0 + int(200 * (center-i)/center))
        draw.ellipse((i,i,size-i,size-i), fill=(r,g,b))

    try:
        font_k = ImageFont.truetype("arialbd.ttf", 360)
        font_t = ImageFont.truetype("arialbd.ttf", 70)
    except:
        font_k = ImageFont.load_default()
        font_t = ImageFont.load_default()

    # 3D K
    k = "K"
    bbox = draw.textbbox((0,0), k, font=font_k)
    wk, hk = bbox[2]-bbox[0], bbox[3]-bbox[1]
    xk, yk = (size-wk)/2, (size-hk)/2 - 20
    for i in range(6,0,-1): draw.text((xk+i, yk+i), k, font=font_k, fill="#8B6914")
    draw.text((xk, yk), k, font=font_k, fill="#FFD700")

    # TIME
    ist = datetime.datetime.utcnow() + datetime.timedelta(hours=5, minutes=30)
    t = ist.strftime("%I:%M %p")
    bbox2 = draw.textbbox((0,0), t, font=font_t)
    wt, ht = bbox2[2]-bbox2[0], bbox2[3]-bbox2[1]
    xt, yt = (size-wt)/2, yk+hk+15
    draw.text((xt+3, yt+3), t, font=font_t, fill="black")
    draw.text((xt, yt), t, font=font_t, fill="white")

    img.save("dp.jpg")
    return "dp.jpg", t

async def auto_loop():
    i = 0
    await asyncio.sleep(10)
    while True:
        try:
            color = COLORS[i % len(COLORS)]
            path, time_str = make_dp(color)
            await client.set_profile_photo(photo=path)
            os.remove(path)

            new_name = f"{USER_NAME} | {time_str}"
            await client.invoke(UpdateProfile(first_name=new_name))

            print(f"✅ Updated: {time_str}")
            i += 1
        except FloodWait as e:
            print(f"⏳ Sleeping {e.value}s")
            await asyncio.sleep(e.value)
        except RPCError as e:
            print(f"❌ Telegram Error: {e}")
        except Exception as e:
            print(f"❌ Error: {e}")
        await asyncio.sleep(60)

async def main():
    await client.start()
    me = await client.get_me()
    print(f"🔥 LOGIN: {me.first_name} @{me.username}")
    print("✅ AUTO STARTED")
    await auto_loop()

client.run(main())
