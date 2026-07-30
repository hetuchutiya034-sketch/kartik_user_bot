import os, asyncio, datetime, time
from dotenv import load_dotenv
load_dotenv()

from pyrogram import Client
from pyrogram.raw.functions.account import UpdateProfile
from pyrogram.errors import FloodWait
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# --- FLASK KEEP ALIVE FOR RAILWAY ---
from flask import Flask
from threading import Thread
web_app = Flask('')
@web_app.route('/')
def home(): return "LIVE DP BOT IS RUNNING!"
def run_web(): web_app.run(host='0.0.0.0', port=int(os.getenv("PORT", 10000)))
Thread(target=run_web, daemon=True).start()

# --- CONFIG - YAHAN APNA SESSION DAAL ---
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING") # Railway me ye variable bana dena

# ============= TERE HISAB SE SETTINGS =============
USER_NAME = "KARTIK NISHAD" # Tera naam yahan change kar lena
COLORS = [
    "#FF0033", "#00FFCC", "#FFD700", "#8A2BE2", "#FF1493",
    "#00BFFF", "#FF8C00", "#32CD32", "#DC143C", "#1E90FF"
]

# ============= 3D DP + TIME + NAME FUNCTION =============
async def create_3d_dp(color):
    size = 512
    img = Image.new("RGB", (size, size), color)
    draw = ImageDraw.Draw(img)

    # Gradient background
    for i in range(size):
        r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
        shade = max(0, r - i//4), max(0, g - i//4), max(0, b - i//4)
        draw.line([(0, i), (size, i)], fill=f"#{shade[0]:02x}{shade[1]:02x}{shade[2]:02x}")

    try:
        font_k = ImageFont.truetype("arialbd.ttf", 350) # Bold font for 3D
        font_time = ImageFont.truetype("arial.ttf", 60)
    except:
        font_k = ImageFont.load_default()
        font_time = ImageFont.load_default()

    # --- 3D LETTER "K" ---
    letter = "K"
    bbox_k = draw.textbbox((0,0), letter, font=font_k)
    w_k, h_k = bbox_k[2] - bbox_k[0], bbox_k[3] - bbox_k[1]
    x_k = (size - w_k) / 2
    y_k = (size - h_k) / 2 - 30

    # 3D Shadow effect
    for i in range(8, 0, -1):
        draw.text((x_k+i, y_k+i), letter, font=font_k, fill="#000000")
    # Main White Letter
    draw.text((x_k, y_k), letter, font=font_k, fill="white")

    # --- TIME ---
    ist_time = datetime.datetime.now() + datetime.timedelta(hours=5, minutes=30)
    time_str = ist_time.strftime('%I:%M %p')

    bbox_t = draw.textbbox((0,0), time_str, font=font_time)
    w_t, h_t = bbox_t[2] - bbox_t[0], bbox_t[3] - bbox_t[1]
    x_t = (size - w_t) / 2
    y_t = y_k + h_k + 15

    # Time Shadow
    draw.text((x_t+3, y_t+3), time_str, font=font_time, fill="black")
    # Main Yellow Time
    draw.text((x_t, y_t), time_str, font=font_time, fill="yellow")

    img.save("live_dp.jpg")
    return "live_dp.jpg"

# ============= MAIN LOOP =============
async def main():
    if not SESSION_STRING:
        print("❌ ERROR: SESSION_STRING nahi mila. Railway me add karo.")
        return

    client = Client("user_session", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING, in_memory=True)
    await client.start()
    me = await client.get_me()
    print(f"✅ LOGIN SUCCESS: {me.first_name} | @{me.username}")

    i = 0
    while True:
        try:
            color = COLORS[i % len(COLORS)]
            print(f"🔄 Updating DP with color: {color}")

            dp_path = await create_3d_dp(color)
            await client.set_profile_photo(photo=dp_path)
            os.remove(dp_path)

            ist_time = datetime.datetime.now() + datetime.timedelta(hours=5, minutes=30)
            time_str = ist_time.strftime('%I:%M %p')
            new_name = f"{USER_NAME} 👑 🕘 {time_str} 🌕"
            await client.invoke(UpdateProfile(first_name=new_name))

            print(f"✅ UPDATED: Name='{new_name}' | Color={color}")
            i += 1

        except FloodWait as e:
            print(f"⚠️ FloodWait: {e.value} seconds. Sota hu...")
            await asyncio.sleep(e.value)
        except Exception as e:
            print(f"❌ Error: {e}")

        await asyncio.sleep(60) # Har 60 sec me update

if __name__ == "__main__":
    asyncio.run(main())
