from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup, KeyboardButton
from pyrogram.errors import SessionPasswordNeeded, PhoneCodeInvalid
import sqlite3, os, asyncio, requests

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
OWNER_USERNAME = os.getenv("OWNER_USERNAME")

bot = Client("pro_team_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ===== DATABASE =====
conn = sqlite3.connect("team.db", check_same_thread=False)
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, name TEXT, username TEXT, phone TEXT, session TEXT, phash TEXT, step TEXT, temp_api_id TEXT, temp_api_hash TEXT)")
c.execute("CREATE TABLE IF NOT EXISTS autoreply (user_id INTEGER, keyword TEXT, reply TEXT)")
conn.commit()

user_sessions = {}
login_temp = {} # step by step data store

async def get_user_client(user_id):
    data = c.execute("SELECT session FROM users WHERE user_id=?", (user_id,)).fetchone()
    if not data or not data[0]: return None
    if user_id not in user_sessions:
        client = Client(f"session_{user_id}", api_id=API_ID, api_hash=API_HASH, session_string=data[0], in_memory=True)
        await client.start()
        user_sessions[user_id] = client
    return user_sessions[user_id]

WELCOME_TEXT = f"""**━━━━━━━━━━━**
**🔥 PRO TEAM BOT V4 🔥**
**━━━━━━━━━━━**

**Hey {{name}} 👋**

**35+ COMMANDS AVAILABLE**
Buttons se use karlo 👇

**Made by @{OWNER_USERNAME}**
**━━━━━━━━━━━**
"""

# ===== START =====
@bot.on_message(filters.command("start"))
async def start(c,m):
    uid = m.from_user.id
    name = m.from_user.first_name
    login_temp.pop(uid, None) # reset login
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

# ===== STEP 1 LOGIN BUTTON =====
@bot.on_message(filters.text & filters.private & filters.regex("^🚀 Login$"))
async def login_start(c,m):
    uid = m.from_user.id
    login_temp[uid] = {"step": "api_id"}
    await m.reply("**Please send your API_ID**\n\nGet from: https://my.telegram.org")

# ===== STEP HANDLER =====
@bot.on_message(filters.text & filters.private & ~filters.command())
async def step_handler(c,m):
    uid = m.from_user.id
    text = m.text

    if uid not in login_temp:
        return await button_handler(c,m) # normal button

    step = login_temp[uid]["step"]

    # STEP 2: API_ID
    if step == "api_id":
        if not text.isdigit(): return await m.reply("**❌ Galat API_ID**\nSirf number bhejo")
        login_temp[uid]["api_id"] = text
        login_temp[uid]["step"] = "api_hash"
        return await m.reply("**Please send your API_HASH**")

    # STEP 3: API_HASH
    if step == "api_hash":
        login_temp[uid]["api_hash"] = text
        login_temp[uid]["step"] = "phone"
        return await m.reply("**Now please send your PHONE_NUMBER along with the country code.**\n**Example :** `+19876543210`")

    # STEP 4: PHONE
    if step == "phone":
        login_temp[uid]["phone"] = text
        api_id = int(login_temp[uid]["api_id"])
        api_hash = login_temp[uid]["api_hash"]
        phone = text

        temp = Client(f"temp_{uid}", api_id=api_id, api_hash=api_hash, in_memory=True)
        await temp.connect()
        try:
            sent = await temp.send_code(phone)
            login_temp[uid]["phash"] = sent.phone_code_hash
            login_temp[uid]["temp_client"] = temp
            login_temp[uid]["step"] = "otp"
            await m.reply("**Please check for an OTP in official telegram account. If you got it, send OTP here after reading the below format.**\n**If OTP is 12345, please send it as `1 2 3 4 5`.**")
        except Exception as e:
            await temp.disconnect()
            login_temp.pop(uid)
            await m.reply(f"**❌ Error:** `{e}`\nDobara `/start` karke try karo")

    # STEP 5: OTP
    elif step == "otp":
        code = text.replace(" ", "")
        temp = login_temp[uid]["temp_client"]
        phash = login_temp[uid]["phash"]
        phone = login_temp[uid]["phone"]
        try:
            session = await temp.sign_in(phone, phash, code)
            user = await temp.get_me()
            c.execute("INSERT OR REPLACE INTO users VALUES (?,?,?,?,?,?,?,?,?)",(uid, user.first_name, user.username, phone, session, None, None, None, None))
            conn.commit()
            await temp.disconnect()
            login_temp.pop(uid)
            await m.reply(f"**✅ Login Success**\nWelcome {user.first_name} ✅\nAb `/stats` try karo")
        except SessionPasswordNeeded:
            login_temp[uid]["step"] = "password"
            await m.reply("**Your account has enabled two-step verification. Please provide the password.**")
        except PhoneCodeInvalid:
            await m.reply("**❌ OTP Galat hai**\nFir se OTP bhejo")
        except Exception as e:
            await temp.disconnect()
            login_temp.pop(uid)
            await m.reply(f"**❌ Error:** `{e}`")

    # STEP 6: PASSWORD
    elif step == "password":
        temp = login_temp[uid]["temp_client"]
        try:
            await temp.check_password(text)
            session = await temp.export_session_string()
            user = await temp.get_me()
            phone = login_temp[uid]["phone"]
            c.execute("INSERT OR REPLACE INTO users VALUES (?,?,?,?,?,?,?,?,?)",(uid, user.first_name, user.username, phone, session, None, None, None, None))
            conn.commit()
            await temp.disconnect()
            login_temp.pop(uid)
            await m.reply(f"**✅ Login Success**\nWelcome {user.first_name} ✅\nAb `/stats` try karo")
        except Exception as e:
            await m.reply(f"**❌ Password Galat**\nFir se bhejo: `{e}`")

# ===== LOGOUT =====
@bot.on_message(filters.command("logout") & filters.private)
async def logout(c,m):
    c.execute("UPDATE users SET session=NULL WHERE user_id=?", (m.from_user.id,)); conn.commit()
    if m.from_user.id in user_sessions: await user_sessions[m.from_user.id].stop(); del user_sessions[m.from_user.id]
    login_temp.pop(m.from_user.id, None)
    await m.reply("**🔓 Logout Success**")

# ===== USERBOT COMMANDS =====
@bot.on_message(filters.command("gcast") & filters.private)
async def gcast(c,m):
    userbot = await get_user_client(m.from_user.id)
    if not userbot: return await m.reply("**Pehle 🚀 Login karo**")
    try: msg = m.text.split(" ",1)[1]
    except: return await m.reply("**Format:** `/gcast Your Message`")
    sent=0; status = await m.reply("**📢 Sending in Groups...**")
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
    sent=0; status = await m.reply("**💌 Sending in DMs...**")
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

# ===== BUTTON HANDLER =====
async def button_handler(c,m):
    text = m.text
    uid = m.from_user.id
    if text == "🔓 Logout": await logout(c,m)
    elif text == "📢 Gcast": await m.reply("**Format:**\n`/gcast Your Message Here`")
    elif text == "💌 Dcast": await m.reply("**Format:**\n`/dcast Your Message Here`")
    elif text == "📊 Stats": await stats(c,m)
    elif text == "👤 Info": await info(c,m)
    elif text == "📋 All Cmds": await m.reply("**Commands:** `/gcast` `/dcast` `/stats` `/info`")

print("PRO TEAM BOT V4 STARTED ✅")
bot.run()
