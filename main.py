import os, asyncio, datetime
from dotenv import load_dotenv
load_dotenv()

from pyrogram import Client
from pyrogram.raw.functions.account import UpdateProfile
from pyrogram.errors import FloodWait

from PIL import Image, ImageDraw, ImageFont

# --- FLASK KEEP ALIVE FOR RAILWAY ---
from flask import Flask
from threading import Thread
web_app = Flask('')
@web_app.route('/')
def home(): return "LIVE DP AUTO BOT IS RUNNING!"
def run_web(): web_app.run(host='0.0.0.0', port=int(os.getenv("PORT", 10000)))
Thread(target=run_web, daemon=True).start()

# --- CONFIG - SIRF 3 VARIABLE ---
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")

# ============= SETTINGS =============
USER_NAME = "Mr. Kartik" # Yahan naam change kar lena
# 14 COLORS
COLORS = ["#FFD700", "#1E90FF", "#FF4500", "#32CD32", "#8A2BE2", "#FF1493", "#00FFFF", "#FF0000", "#FF8C00", "#9400D3", "#00FF7F", "#DC143C", "#4682B4", "#FF69B4"]

app = Client("user_session", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING, in_memory=True)

# ============= DP CREATOR - BADA 3D K + BADA TIME =============
async def create_3d_dp(color):
    size = 512
    img = Image.new("RGB", (size, size), color)
    draw = ImageDraw.Draw(img)

    # Radial Gradient BG
    center = size // 2
    for i in range(center):
        shade = int(200 * (i / center))
        r = min(255, int(color[1:3], 16) + shade)
        g = min(255, int(color[3:5], 16) + shade)
        b = min(255, int(color[5:7], 16) + shade)
        draw.ellipse((center-i, center-i, center+i, center+i), fill=f"#{r:02x}{g:02x}{b:02x}")

    try:
        font_k = ImageFont.truetype("arialbd.ttf", 380) # BAHUT BADA K
        font_time = ImageFont.truetype("arialbd.ttf", 80) # BADA TIME
    except:
        font_k = ImageFont.load_default()
        font_time = ImageFont.load_default()

    # --- BADA 3D GOLDEN "K" BEECH ME ---
    letter = "K"
    bbox_k = draw.textbbox((0,0), letter, font=font_k)
    w_k, h_k = bbox_k[2] - bbox_k[0], bbox_k[3] - bbox_k[1]
    x_k = (size - w_k) / 2
    y_k = (size - h_k) / 2 - 10
    for i in range(8, 0, -1): draw.text((x_k+i, y_k+i), letter, font=font_k, fill="#B8860B") # Shadow
    draw.text((x_k, y_k), letter, font=font_k, fill="#FFD700") # Golden K

    # --- BADA TIME NEECHE ---
    ist_time = datetime.datetime.now() + datetime.timedelta(hours=5, minutes=30)
    time_str = ist_time.strftime('%I:%M %p')
    bbox_t = draw.textbbox((0,0), time_str, font=font_time)
    w_t, h_t = bbox_t[2] - bbox_t[0], bbox_t[3] - bbox_t[1]
    x_t = (size - w_t) / 2
    y_t = y_k + h_k + 20
    draw.text((x_t+4, y_t+4), time_str, font=font_time, fill="black") # Shadow
    draw.text((x_t, y_t), time_str, font=font_time, fill="white") # White Time

    img.save("live_dp.jpg")
    return "live_dp.jpg", time_str

# ============= MAIN AUTO LOOP =============
async def main():
    await app.start()
    me = await app.get_me()
    print(f"🔥 AUTO LOGIN SUCCESS: {me.first_name} | @{me.username}")
    print("✅ AUTO DP STARTED. Har 60 sec me update hoga")

    i = 0
    await asyncio.sleep(15) # Login hone ka time
    while True:
        try:
            color = COLORS[i % len(COLORS)]
            dp_path, time_str = await create_3d_dp(color)
            await app.set_profile_photo(photo=dp_path)
            os.remove(dp_path)

            new_name = f"{USER_NAME} ⏰ {time_str} 🌕"
            await app.invoke(UpdateProfile(first_name=new_name))

            print(f"✅ UPDATED: {time_str} | Color={color}")
            i += 1

        except FloodWait as e:
            print(f"⏳ FloodWait: {e.value} sec wait")
            await asyncio.sleep(e.value)
        except Exception as e:
            print(f"❌ Error: {e}")

        await asyncio.sleep(60) # 1 min me 1 baar

asyncio.run(main())
