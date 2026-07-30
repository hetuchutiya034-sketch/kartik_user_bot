import os, asyncio, random, datetime, sqlite3
from dotenv import load_dotenv
load_dotenv()

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.raw.functions.account import UpdateProfile
from pyrogram.errors import SessionPasswordNeeded
from PIL import Image, ImageDraw, ImageFont

# --- FLASK KEEP ALIVE ---
from flask import Flask
from threading import Thread
web_app = Flask('')
@web_app.route('/')
def home(): return "KARTIK NISHAD MULTI BOT IS RUNNING!"
def run_web(): web_app.run(host='0.0.0.0', port=int(os.getenv("PORT", 10000)))
Thread(target=run_web, daemon=True).start()

# --- CONFIG ---
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = [7967825682] 

bot = Client("manager_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- DATABASE FOR SESSIONS ---
conn = sqlite3.connect('sessions.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, session TEXT)''')
conn.commit()

USERBOTS = {}

# ============= TERA LIVE PROFILE SETTINGS =============
TG_AUTO = True
my_name = "KARTIK NISHAD"
COLORS = ["#FFD700", "#FF0000", "#00FF00", "#0000FF", "#FF00FF", "#00FFFF", "#FFA500", "#800080", "#FF1493", "#1E90FF", "#32CD32", "#DC143C"]

# ============= DP + NAME AUTO FUNCTIONS =============
async def create_color_dp(color):
    """Color + 3D K + Time wali DP banayega"""
    size = 512
    img = Image.new("RGB", (size, size), color)
    draw = ImageDraw.Draw(img)

    # Gradient effect
    for i in range(size):
        r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
        shade = max(0, r - i//4), max(0, g - i//4), max(0, b - i//4)
        draw.line([(0, i), (size, i)], fill=f"#{shade[0]:02x}{shade[1]:02x}{shade[2]:02x}")

    try:
        font_k = ImageFont.truetype("arial.ttf", 320)
        font_time = ImageFont.truetype("arial.ttf", 55)
    except:
        font_k = ImageFont.load_default()
        font_time = ImageFont.load_default()

    # 1. Bada 3D K
    letter = "K"
    bbox_k = draw.textbbox((0,0), letter, font=font_k)
    w_k, h_k = bbox_k[2] - bbox_k[0], bbox_k[3] - bbox_k[1]
    x_k = (size - w_k) / 2
    y_k = (size - h_k) / 2 - 20

    for i in range(5, 0, -1): # 3D shadow
        draw.text((x_k+i, y_k+i), letter, font=font_k, fill="black")
    draw.text((x_k, y_k), letter, font=font_k, fill="white")

    # 2. LIVE TIME
    ist_time = datetime.datetime.now() + datetime.timedelta(hours=5, minutes=30)
    time_str = ist_time.strftime('%I:%M %p')

    bbox_t = draw.textbbox((0,0), time_str, font=font_time)
    w_t, h_t = bbox_t[2] - bbox_t[0], bbox_t[3] - bbox_t[1]
    x_t = (size - w_t) / 2
    y_t = y_k + h_k + 10

    draw.text((x_t+2, y_t+2), time_str, font=font_time, fill="black")
    draw.text((x_t, y_t), time_str, font=font_time, fill="yellow")

    img.save("color_dp.jpg")
    return "color_dp.jpg"

async def run_automation(client, user_id):
    i = 0
    while True:
        if TG_AUTO and user_id in USERBOTS:
            try:
                # DP UPDATE
                color = COLORS[i % len(COLORS)]
                dp_path = await create_color_dp(color)
                await client.set_profile_photo(photo=dp_path)
                os.remove(dp_path)

                # NAME UPDATE
                ist_time = datetime.datetime.now() + datetime.timedelta(hours=5, minutes=30)
                time_str = ist_time.strftime('%I:%M %p')
                new_name = f"{my_name} 👑 🕘 {time_str} 🌕"
                await client.invoke(UpdateProfile(first_name=new_name))

                print(f"✅ {user_id} Updated: {color} | {time_str}")
                i += 1
            except Exception as e:
                print(f"❌ {user_id} Error: {e}")
        await asyncio.sleep(60)

# ============= LOAD ALL SESSIONS ON START =============
async def load_sessions():
    c.execute("SELECT user_id, session FROM users")
    for user_id, session_string in c.fetchall():
        try:
            client = Client(f"user_{user_id}", api_id=API_ID, api_hash=API_HASH, session_string=session_string, in_memory=True)
            await client.start()
            USERBOTS[user_id] = client
            asyncio.create_task(run_automation(client, user_id))
            print(f"✅ Loaded {user_id} - {client.me.first_name}")
        except Exception as e:
            print(f"❌ Failed to load {user_id}: {e}")

# ============= BOT COMMANDS =============

@bot.on_message(filters.command("start") & filters.user(ADMIN_ID))
async def start(_, message: Message):
    await message.reply_text(
        f"🔥 **KARTIK NISHAD MULTI MANAGER** 🔥\n\n"
        f"**Total Users:** {len(USERBOTS)}\n"
        f"**Live DP:** {'✅ ON' if TG_AUTO else '❌ OFF'}\n\n"
        f"**Commands:**\n"
        f"`/addsession` - Naya user add karo\n"
        f"`/del 123456` - User hatao\n"
        f"`/tgauto on/off` - Sab ki live DP band/chalu\n"
        f"`/users` - List dekho"
    )

@bot.on_message(filters.command("addsession") & filters.user(ADMIN_ID))
async def addsession(_, message: Message):
    await message.reply_text("**Phone number bhej:** `+91xxxxxxxxxx`")
    phone_msg = await bot.listen(message.chat.id, filters.user(ADMIN_ID), timeout=120)
    phone = phone_msg.text

    client = Client(f"temp_{phone}", api_id=API_ID, api_hash=API_HASH, in_memory=True)
    await client.connect()
    code = await client.send_code(phone)

    await message.reply_text("**OTP bhej:** `1 2 3 4 5` space ke sath")
    otp_msg = await bot.listen(message.chat.id, filters.user(ADMIN_ID), timeout=120)
    otp = otp_msg.text.replace(" ", "")

    try:
        await client.sign_in(phone, code.phone_code_hash, otp)
    except SessionPasswordNeeded:
        await message.reply_text("**2FA Password bhej:**")
        pwd_msg = await bot.listen(message.chat.id, filters.user(ADMIN_ID), timeout=60)
        await client.sign_in(password=pwd_msg.text)

    session_string = await client.export_session_string()
    user_id = client.me.id

    c.execute("INSERT OR REPLACE INTO users VALUES (?,?)", (user_id, session_string))
    conn.commit()

    USERBOTS[user_id] = client
    asyncio.create_task(run_automation(client, user_id))
    await message.reply_text(f"✅ **User Added:** `{user_id}`\n**Name:** {client.me.first_name}\n**Live DP/Name ON**")

@bot.on_message(filters.command("del") & filters.user(ADMIN_ID))
async def delete_user(_, message: Message):
    try:
        user_id = int(message.command[1])
        c.execute("DELETE FROM users WHERE user_id=?", (user_id,))
        conn.commit()
        if user_id in USERBOTS:
            await USERBOTS[user_id].stop()
            del USERBOTS[user_id]
        await message.reply_text(f"✅ User `{user_id}` deleted")
    except: await message.reply_text("**Use:** `/del 123456`")

@bot.on_message(filters.command("tgauto") & filters.user(ADMIN_ID))
async def tg_auto_toggle(_, message: Message):
    global TG_AUTO
    if len(message.command) < 2:
        return await message.reply_text(f"❌ **Use:** `/tgauto on` or `/tgauto off`\n**Current:** {'✅ ON' if TG_AUTO else '❌ OFF'}")

    TG_AUTO = message.command[1] == "on"
    await message.reply_text(f"✈️ **Sabki Live DP/Name:** {'✅ ON' if TG_AUTO else '❌ OFF'}\n`Total Users: {len(USERBOTS)}`")

@bot.on_message(filters.command("users") & filters.user(ADMIN_ID))
async def list_users(_, message: Message):
    if not USERBOTS: return await message.reply_text("Koi user add nahi hai")
    text = f"**Total Users: {len(USERBOTS)}**\n\n"
    for uid, client in USERBOTS.items():
        text += f"👤 `{uid}` - {client.me.first_name}\n"
    await message.reply_text(text)

# ============= START =============
async def main():
    await load_sessions()
    await bot.start()
    print(f"🔥 MANAGER BOT STARTED. {len(USERBOTS)} Users Loaded")
    await asyncio.Event().wait()

asyncio.run(main())
