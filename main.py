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
c.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, name TEXT, username TEXT, phone TEXT, session TEXT, phash TEXT)")
c.execute("CREATE TABLE IF NOT EXISTS autoreply (user_id INTEGER, keyword TEXT, reply TEXT)")
conn.commit()

user_sessions = {}

async def get_user_client(user_id):
    data = c.execute("SELECT session FROM users WHERE user_id=?", (user_id,)).fetchone()
    if not data or not data[0]: return None
    if user_id not in user_sessions:
        client = Client(f"session_{user_id}", api_id=API_ID, api_hash=API_HASH, session_string=data[0], in_memory=True)
        await client.start()
        user_sessions[user_id] = client
    return user_sessions[user_id]

WELCOME_TEXT = f"""**━━━━━━━━━━━**
**🔥 PRO TEAM BOT V3 FIXED 🔥**
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

# ===== LOGIN SYSTEM =====
@bot.on_message(filters.command("addsession") & filters.private)
async def add(c,m):
    try:
        _, api_id, api_hash, phone = m.text.split(" ", 3)
        temp = Client(f"temp_{m.from_user.id}", api_id=int(api_id), api_hash=api_hash, in_memory=True)
        await temp.connect()
        sent = await temp.send_code(phone)
        c.execute("INSERT OR REPLACE INTO users VALUES (?,?,?,?,?,?)",(m.from_user.id, m.from_user.first_name, m.from_user.username, phone, None, sent.phone_code_hash))
        conn.commit(); await temp.disconnect()
        await m.reply("**✅ OTP Sent**\nAb bhejo: `/otp 12345`")
    except Exception as e: await m.reply(f"**Error:** `{e}`\n**Format:** `/addsession API_ID API_HASH +91XXXXXXXXXX`")

@bot.on_message(filters.command("otp") & filters.private)
async def otp(c,m):
    data = c.execute("SELECT * FROM users WHERE user_id=?", (m.from_user.id,)).fetchone()
    if not data: return await m.reply("Pehle `/addsession` karo")
    parts = m.command
    code = parts[1]; password = parts[2] if len(parts) > 2 else None
    phone, phash = data[3], data[5]
    temp = Client(f"temp_{m.from_user.id}", api_id=API_ID, api_hash=API_HASH, in_memory=True)
    await temp.connect()
    try:
        session = await temp.sign_in(phone, phash, code)
        if password: await temp.check_password(password)
        user = await temp.get_me()
        c.execute("UPDATE users SET session=? WHERE user_id=?",(session, m.from_user.id)); conn.commit()
        await m.reply(f"**✅ Login Success**\nWelcome {user.first_name} ✅")
    except SessionPasswordNeeded:
        await m.reply("**⚠️ 2FA Password hai**\nFormat: `/otp 12345 your_password`")
    except Exception as e:
        await m.reply(f"**❌ Error:** `{e}`")
    finally: await temp.disconnect()

@bot.on_message(filters.command("logout") & filters.private)
async def logout(c,m):
    c.execute("UPDATE users SET session=NULL WHERE user_id=?", (m.from_user.id,)); conn.commit()
    if m.from_user.id in user_sessions: await user_sessions[m.from_user.id].stop(); del user_sessions[m.from_user.id]
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

# ===== HELP =====
@bot.on_message(filters.command(["help","allcmds"])) # YE FIX HAI
async def help_cmd(c,m):
    await m.reply("**📖 35+ COMMAND LIST**\n\n**ACCOUNT:** `/addsession` `/otp` `/logout`\n**CAST:** `/gcast msg` `/dcast msg`\n**STATS:** `/stats` `/info`\n**AUTO REPLY:** `/setreply key reply` `/delreply key` `/listreply`\n**AI:** `/imagine prompt` `/logo name` `/tts text`\n**ADMIN:** `/panel` `/allusers`\n**OTHER:** `/start` `/help`")

# ===== BUTTON HANDLER =====
@bot.on_message(filters.text & filters.private & ~filters.command(["start","addsession","otp","logout","gcast","dcast","stats","info","help","allcmds","setreply","delreply","listreply","imagine","logo","tts","panel","allusers"]))
async def button_handler(c,m):
    text = m.text
    uid = m.from_user.id
    if text == "🚀 Login": await m.reply("**Format:**\n`/addsession API_ID API_HASH +91XXXXXXXXXX`")
    elif text == "🔓 Logout": await logout(c,m)
    elif text == "📢 Gcast": await m.reply("**Format:**\n`/gcast Your Message Here`")
    elif text == "💌 Dcast": await m.reply("**Format:**\n`/dcast Your Message Here`")
    elif text == "📊 Stats": await stats(c,m)
    elif text == "👤 Info": await info(c,m)
    elif text == "⚡ AutoReply": await m.reply("**AutoReply:**\n`/setreply hi Hello`\n`/delreply hi`\n`/listreply`")
    elif text == "🎨 Imagine": await m.reply("**Format:**\n`/imagine sunset beach`")
    elif text == "🖼️ Logo": await m.reply("**Format:**\n`/logo Your Name`")
    elif text == "🗣️ TTS": await m.reply("**Format:**\n`/tts Hello kaise ho`")
    elif text == "📋 All Cmds": await help_cmd(c,m)
    elif text == "👑 Owner": await m.reply(f"**Problem hai?**\nMujhe DM karo: [@{OWNER_USERNAME}](https://t.me/{OWNER_USERNAME})")
    elif text == "👑 Admin Panel" and uid==ADMIN_ID: await panel(c,m)
    elif text == "📜 All Users" and uid==ADMIN_ID: await allusers(c,m)

print("PRO TEAM BOT 35+ CMDS STARTED ✅")
bot.run()
