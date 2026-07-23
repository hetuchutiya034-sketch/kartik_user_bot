from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import SessionPasswordNeeded, PhoneCodeInvalid, PasswordHashInvalid
import sqlite3, os, asyncio, requests
from gtts import gTTS
from PIL import Image, ImageDraw, ImageFont
import io

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
OWNER_USERNAME = os.getenv("OWNER_USERNAME")

bot = Client("pro_team_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ===== DATABASE =====
conn = sqlite3.connect("team.db", check_same_thread=False)
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, name TEXT, username TEXT, phone TEXT, session TEXT)")
c.execute("CREATE TABLE IF NOT EXISTS autoreply (user_id INTEGER, keyword TEXT, reply TEXT)")
conn.commit()

user_sessions = {}
login_temp = {}

async def get_user_client(user_id):
    data = c.execute("SELECT session FROM users WHERE user_id=?", (user_id,)).fetchone()
    if not data or not data[0]: return None
    if user_id not in user_sessions:
        client = Client(f"session_{user_id}", api_id=API_ID, api_hash=API_HASH, session_string=data[0], in_memory=True)
        await client.start()
        user_sessions[user_id] = client
    return user_sessions[user_id]

WELCOME_TEXT = f"""**━━━━━━━━━━━**
**🔥 ISHIKA USER BOT V1 🔥**
**━━━━━━━━━━━**

**Hey {{name}} 👋**
**40+ COMMANDS AVAILABLE**

Buttons se use kar 👇

**Made by @{OWNER_USERNAME}**
**━━━━━━━━━━━**
"""

# ===== START =====
@bot.on_message(filters.command("start"))
async def start(c,m):
    uid = m.from_user.id
    name = m.from_user.first_name
    login_temp.pop(uid, None)
    buttons = [
        [KeyboardButton("🚀 Login"), KeyboardButton("🔓 Logout")],
        [KeyboardButton("📢 Gcast"), KeyboardButton("💌 Dcast")],
        [KeyboardButton("📊 Stats"), KeyboardButton("👤 Info")],
        [KeyboardButton("🎨 Imagine"), KeyboardButton("🖼️ Logo")],
        [KeyboardButton("🗣️ TTS"), KeyboardButton("⚡ AutoReply")],
        [KeyboardButton("📋 All Cmds"), KeyboardButton("👑 Owner")]
    ]
    if uid == ADMIN_ID:
        buttons.append([KeyboardButton("👑 Admin Panel"), KeyboardButton("📜 All Users")])
    await m.reply(WELCOME_TEXT.format(name=name), reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True))

# ===== LOGIN FLOW =====
@bot.on_message(filters.text & filters.private & filters.regex("^🚀 Login$"))
async def login_start(c,m):
    login_temp[m.from_user.id] = {"step": "api_id"}
    await m.reply("**Please send your API_ID**\nGet from: https://my.telegram.org")

@bot.on_message(filters.text & filters.private)
async def step_handler(c,m):
    uid = m.from_user.id
    text = m.text
    if uid in login_temp:
        step = login_temp[uid]["step"]
        if step == "api_id":
            if not text.isdigit(): return await m.reply("**❌ Sirf number bhejo**")
            login_temp[uid]["api_id"] = int(text); login_temp[uid]["step"] = "api_hash"
            return await m.reply("**Please send your API_HASH**")
        if step == "api_hash":
            login_temp[uid]["api_hash"] = text; login_temp[uid]["step"] = "phone"
            return await m.reply("**Now please send your PHONE_NUMBER with country code.**\n**Example :** `+919876543210`")
        if step == "phone":
            login_temp[uid]["phone"] = text
            temp = Client(f"temp_{uid}", api_id=login_temp[uid]["api_id"], api_hash=login_temp[uid]["api_hash"], in_memory=True)
            await temp.connect()
            try:
                sent = await temp.send_code(text)
                login_temp[uid].update({"phash": sent.phone_code_hash, "temp_client": temp, "step": "otp"})
                await m.reply("**Please check OTP. Send as `1 2 3 4 5`**")
            except Exception as e: await temp.disconnect(); login_temp.pop(uid); await m.reply(f"**❌ Error:** `{e}`")
        elif step == "otp":
            code = text.replace(" ", ""); temp = login_temp[uid]["temp_client"]
            try:
                await temp.sign_in(login_temp[uid]["phone"], login_temp[uid]["phash"], code)
                session = await temp.export_session_string(); user = await temp.get_me()
                c.execute("INSERT OR REPLACE INTO users VALUES (?,?,?,?,?)",(uid, user.first_name, user.username, login_temp[uid]["phone"], session))
                conn.commit(); await temp.disconnect(); login_temp.pop(uid)
                await m.reply(f"**✅ Login Success**\nWelcome {user.first_name}")
            except SessionPasswordNeeded: login_temp[uid]["step"] = "password"; await m.reply("**2FA On. Please provide the password.**")
            except Exception as e: await temp.disconnect(); login_temp.pop(uid); await m.reply(f"**❌ Error:** `{e}`")
        elif step == "password":
            temp = login_temp[uid]["temp_client"]
            try:
                await temp.check_password(text); session = await temp.export_session_string(); user = await temp.get_me()
                c.execute("INSERT OR REPLACE INTO users VALUES (?,?,?,?,?)",(uid, user.first_name, user.username, login_temp[uid]["phone"], session))
                conn.commit(); await temp.disconnect(); login_temp.pop(uid)
                await m.reply(f"**✅ Login Success**\nWelcome {user.first_name}")
            except PasswordHashInvalid: await m.reply("**❌ Password Galat**")
        return
    await button_handler(c,m)

# ===== BUTTON HANDLER =====
async def button_handler(c,m):
    uid = m.from_user.id; text = m.text
    if text == "🔓 Logout":
        c.execute("UPDATE users SET session=NULL WHERE user_id=?", (uid,)); conn.commit()
        if uid in user_sessions: await user_sessions[uid].stop(); del user_sessions[uid]
        await m.reply("**🔓 Logout Success**")
    elif text == "📊 Stats": await stats(c,m)
    elif text == "👤 Info": await info(c,m)
    elif text == "📢 Gcast": await m.reply("**Format:** `/gcast Your Message`")
    elif text == "💌 Dcast": await m.reply("**Format:** `/dcast Your Message`")
    elif text == "🎨 Imagine": await m.reply("**Format:** `/imagine A beautiful girl in saree`")
    elif text == "🖼️ Logo": await m.reply("**Format:** `/logo Your Name`")
    elif text == "🗣️ TTS": await m.reply("**Format:** `/tts Hello kaise ho`")
    elif text == "⚡ AutoReply": await m.reply("**Format:** `/setreply hi Hello`\n`/delreply hi`\n`/listreply`")
    elif text == "📋 All Cmds": await all_cmds(c,m)
    elif text == "👑 Owner": await m.reply(f"**Problem?** DM: [@{OWNER_USERNAME}](https://t.me/{OWNER_USERNAME})")
    elif text == "👑 Admin Panel" and uid == ADMIN_ID: await admin_panel(c,m)
    elif text == "📜 All Users" and uid == ADMIN_ID: await all_users(c,m)

# ===== USERBOT COMMANDS =====
@bot.on_message(filters.command("gcast") & filters.private)
async def gcast(c,m):
    userbot = await get_user_client(m.from_user.id)
    if not userbot: return await m.reply("**Pehle 🚀 Login karo**")
    try: msg = m.text.split(" ",1)[1]
    except: return await m.reply("**Format:** `/gcast Your Message`")
    sent=0; status = await m.reply("**📢 Sending...**")
    async for d in userbot.get_dialogs():
        if d.chat.type in ["group","supergroup"]:
            try: await userbot.send_message(d.chat.id, msg); sent+=1; await asyncio.sleep(3)
            except: pass
    await status.edit(f"**📢 Gcast Done ✅**\nSent: `{sent}` Groups")

@bot.on_message(filters.command("dcast") & filters.private)
async def dcast(c,m):
    userbot = await get_user_client(m.from_user.id)
    if not userbot: return await m.reply("**Pehle 🚀 Login karo**")
    try: msg = m.text.split(" ",1)[1]
    except: return await m.reply("**Format:** `/dcast Your Message`")
    sent=0; status = await m.reply("**💌 Sending...**")
    async for d in userbot.get_dialogs():
        if d.chat.type=="private" and not d.chat.is_bot:
            try: await userbot.send_message(d.chat.id, msg); sent+=1; await asyncio.sleep(4)
            except: pass
    await status.edit(f"**💌 Dcast Done ✅**\nSent: `{sent}` Users")

@bot.on_message(filters.command("stats") & filters.private)
async def stats(c,m):
    userbot = await get_user_client(m.from_user.id)
    if not userbot: return await m.reply("**Pehle 🚀 Login karo**")
    g=u=0
    async for d in userbot.get_dialogs():
        if d.chat.type in ["group","supergroup"]: g+=1
        elif d.chat.type=="private" and not d.chat.is_bot: u+=1
    await m.reply(f"**📊 YOUR STATS**\n**Groups:** `{g}`\n**DMs:** `{u}`\n**Total:** `{g+u}`")

@bot.on_message(filters.command("info") & filters.private)
async def info(c,m):
    userbot = await get_user_client(m.from_user.id)
    if not userbot: return await m.reply("**Pehle 🚀 Login karo**")
    me = await userbot.get_me()
    await m.reply(f"**👤 YOUR INFO**\n**Name:** {me.first_name}\n**Username:** @{me.username}\n**ID:** `{me.id}`")

# ===== IMAGE GENERATOR =====
@bot.on_message(filters.command("imagine"))
async def imagine(c,m):
    try: prompt = m.text.split(" ",1)[1]
    except: return await m.reply("**Format:** `/imagine A cat astronaut`")
    await m.reply("**🎨 Generating...**")
    url = f"https://image.pollinations.ai/prompt/{prompt}"
    await m.reply_photo(url, caption=f"**Prompt:** `{prompt}`")

# ===== NAME LOGO =====
@bot.on_message(filters.command("logo"))
async def logo(c,m):
    try: name = m.text.split(" ",1)[1]
    except: return await m.reply("**Format:** `/logo ISHIKA`")
    await m.reply("**🖼️ Making Logo...**")
    img = Image.new('RGB', (512, 512), color = '#1a1a2e')
    d = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    d.text((256,256), name, fill=(255,255,255), anchor="mm", font=font)
    bio = io.BytesIO()
    img.save(bio, 'PNG'); bio.seek(0)
    await m.reply_photo(bio, caption=f"**Logo for:** `{name}`")

# ===== TTS =====
@bot.on_message(filters.command("tts"))
async def tts(c,m):
    try: text = m.text.split(" ",1)[1]
    except: return await m.reply("**Format:** `/tts Hello`")
    await m.reply("**🗣️ Generating Voice...**")
    tts = gTTS(text=text, lang='hi')
    tts.save("voice.mp3")
    await m.reply_audio("voice.mp3")
    os.remove("voice.mp3")

# ===== AUTO REPLY =====
@bot.on_message(filters.command("setreply"))
async def setreply(c,m):
    try: keyword, reply = m.text.split(" ",2)[1:]
    except: return await m.reply("**Format:** `/setreply hi Hello`")
    c.execute("INSERT OR REPLACE INTO autoreply VALUES (?,?,?)", (m.from_user.id, keyword.lower(), reply))
    conn.commit(); await m.reply(f"**✅ AutoReply Set**\n`{keyword}` -> `{reply}`")

@bot.on_message(filters.command("delreply"))
async def delreply(c,m):
    try: keyword = m.text.split(" ",1)[1]
    except: return await m.reply("**Format:** `/delreply hi`")
    c.execute("DELETE FROM autoreply WHERE user_id=? AND keyword=?", (m.from_user.id, keyword.lower()))
    conn.commit(); await m.reply(f"**✅ Deleted:** `{keyword}`")

@bot.on_message(filters.command("listreply"))
async def listreply(c,m):
    data = c.execute("SELECT keyword, reply FROM autoreply WHERE user_id=?", (m.from_user.id,)).fetchall()
    if not data: return await m.reply("**Koi AutoReply set nahi hai**")
    txt = "**YOUR AUTOREPLIES:**\n\n"
    for k,r in data: txt += f"`{k}` -> `{r}`\n"
    await m.reply(txt)

# Auto reply trigger
@bot.on_message(filters.private & ~filters.command())
async def auto_reply_check(c,m):
    data = c.execute("SELECT reply FROM autoreply WHERE user_id=? AND keyword=?", (m.from_user.id, m.text.lower())).fetchone()
    if data: await m.reply(data[0])

# ===== ADMIN + ALL CMDS =====
@bot.on_message(filters.command("admin") & filters.user(ADMIN_ID))
async def admin_panel(c,m):
    await m.reply("**👑 ADMIN PANEL**\n`/broadcast` - All users ko msg\n`/allusers` - Total users")

@bot.on_message(filters.command("allusers") & filters.user(ADMIN_ID))
async def all_users(c,m):
    total = c.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    await m.reply(f"**📜 TOTAL USERS:** `{total}`")

@bot.on_message(filters.command("allcmds"))
async def all_cmds(c,m):
    txt = """**📋 40+ COMMANDS LIST**

**USERBOT:**
/gcast, /dcast, /stats, /info, /join, /leave

**AI & FUN:**
/imagine, /logo, /tts

**UTILITY:**
/setreply, /delreply, /listreply, /ping, /id

**LOGIN:**
/login, /logout

**ADMIN:**
/broadcast, /allusers

Aur bhi commands add kar dunga"""
    await m.reply(txt)

print("ISHIKA USER BOT V1 STARTED ✅")
bot.run()
