import os, asyncio, datetime
from dotenv import load_dotenv
load_dotenv()

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.raw.functions.account import UpdateProfile
from pyrogram.errors import FloodWait

from PIL import Image, ImageDraw, ImageFont

# --- FLASK KEEP ALIVE ---
from flask import Flask
from threading import Thread
web_app = Flask('')
@web_app.route('/')
def home(): return "LIVE DP USERBOT IS RUNNING!"
def run_web(): web_app.run(host='0.0.0.0', port=int(os.getenv("PORT", 10000)))
Thread(target=run_web, daemon=True).start()

# --- CONFIG - SIRF 3 CHEEZ ---
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")

# ============= GLOBAL SETTINGS =============
USER_NAME = "Mr. Kartik" # Yahan apna naam
AUTO_ON = True
ADMIN_ID = "me" # "me" ka matlab khud ka account
COLORS = [
    "#FFD700", "#1E90FF", "#FF4500", "#32CD32", "#8A2BE2",
    "#FF1493", "#00FFFF", "#FF0000", "#FF8C00", "#9400D3",
    "#00FF7F", "#DC143C", "#4682B4", "#FF69B4"
]

# ============= DP CREATOR - SS WALI STYLE =============
async def create_3d_dp(color):
    size = 512
    img = Image.new("RGB", (size, size), color)
    draw = ImageDraw.Draw(img)

    center = size // 2
    for i in range(center): # Radial Gradient
        shade = int(255 * (i / center))
        r = min(255, int(color[1:3], 16) + shade // 3)
        g = min(255, int(color[3:5], 16) + shade // 3)
        b = min(255, int(color[5:7], 16) + shade // 3)
        draw.ellipse((center-i, center-i, center+i, center+i), fill=f"#{r:02x}{g:02x}{b:02x}")

    try:
        font_k = ImageFont.truetype("arialbd.ttf", 380)
        font_time = ImageFont.truetype("arialbd.ttf", 80)
    except:
        font_k = ImageFont.load_default()
        font_time = ImageFont.load_default()

    # --- BADA 3D GOLDEN "K" ---
    letter = "K"
    bbox_k = draw.textbbox((0,0), letter, font=font_k)
    w_k, h_k = bbox_k[2] - bbox_k[0], bbox_k[3] - bbox_k[1]
    x_k = (size - w_k) / 2
    y_k = (size - h_k) / 2 - 10
    for i in range(8, 0, -1): draw.text((x_k+i, y_k+i), letter, font=font_k, fill="#B8860B")
    draw.text((x_k, y_k), letter, font=font_k, fill="#FFD700", stroke_width=4, stroke_fill="white")

    # --- BADA TIME ---
    ist_time = datetime.datetime.now() + datetime.timedelta(hours=5, minutes=30)
    time_str = ist_time.strftime('%I:%M %p')
    bbox_t = draw.textbbox((0,0), time_str, font=font_time)
    w_t, h_t = bbox_t[2] - bbox_t[0], bbox_t[3] - bbox_t[1]
    x_t = (size - w_t) / 2
    y_t = y_k + h_k + 20
    draw.text((x_t+4, y_t+4), time_str, font=font_time, fill="black")
    draw.text((x_t, y_t), time_str, font=font_time, fill="white")

    img.save("live_dp.jpg")
    return "live_dp.jpg", time_str

# ============= AUTO LOOP =============
async def run_automation(app):
    global AUTO_ON
    i = 0
    while True:
        if AUTO_ON:
            try:
                color = COLORS[i % len(COLORS)]
                dp_path, time_str = await create_3d_dp(color)
                await app.set_profile_photo(photo=dp_path)
                os.remove(dp_path)
                new_name = f"{USER_NAME} ⏰ {time_str} 🌕"
                await app.invoke(UpdateProfile(first_name=new_name))
                print(f"✅ UPDATED: {time_str} | Color={color}")
                i += 1
            except FloodWait as e: await asyncio.sleep(e.value)
            except Exception as e: print(f"❌ Error: {e}")
        await asyncio.sleep(60)

# ============= USERBOT COMMANDS =============
app = Client("user_session", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING, in_memory=True)

@app.on_message(filters.command("start") & filters.me)
async def start(_, message: Message):
    status = "✅ ON" if AUTO_ON else "❌ OFF"
    await message.edit_text(
        f"🔥 **KARTIK LIVE DP USERBOT** 🔥\n\n"
        f"**Status:** {status}\n"
        f"**User:** `{message.from_user.first_name}`\n\n"
        f"**Commands:**\n"
        f"`/on` - Auto DP On\n"
        f"`/off` - Auto DP Off\n"
        f"`/status` - Current Status\n"
        f"`/update` - Force 1 Update Now"
    )

@app.on_message(filters.command("on") & filters.me)
async def turn_on(_, message: Message):
    global AUTO_ON
    AUTO_ON = True
    await message.edit_text("✅ **Live DP ON ho gaya**")

@app.on_message(filters.command("off") & filters.me)
async def turn_off(_, message: Message):
    global AUTO_ON
    AUTO_ON = False
    await message.edit_text("❌ **Live DP OFF ho gaya**")

@app.on_message(filters.command("status") & filters.me)
async def status(_, message: Message):
    status = "✅ ON" if AUTO_ON else "❌ OFF"
    await message.edit_text(f"**Status:** {status}\n**User:** `{message.from_user.first_name}`")

@app.on_message(filters.command("update") & filters.me)
async def force_update(_, message: Message):
    msg = await message.edit_text("🔄 Updating...")
    color = COLORS[0]
    dp_path, time_str = await create_3d_dp(color)
    await app.set_profile_photo(photo=dp_path)
    os.remove(dp_path)
    await msg.edit_text(f"✅ **Force Updated**\nTime: `{time_str}`")

# ============= START =============
async def main():
    await app.start()
    me = await app.get_me()
    print(f"🔥 USERBOT LOGIN: {me.first_name} | @{me.username}")
    asyncio.create_task(run_automation(app))
    await asyncio.Event().wait()

asyncio.run(main())
