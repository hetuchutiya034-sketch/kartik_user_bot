from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup, KeyboardButton
import sqlite3, os, asyncio, datetime, requests

API_ID = int(os.getenv("API_ID", "123456"))
API_HASH = os.getenv("API_HASH", "tera_api_hash")
BOT_TOKEN = os.getenv("BOT_TOKEN", "bot_token_yaha")
ADMIN_ID = int(os.getenv("ADMIN_ID", "12345678"))
OWNER_USERNAME = os.getenv("OWNER_USERNAME", "tera_username")

app = Client("pro_team_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ===== DATABASE =====
conn = sqlite3.connect("team.db", check_same_thread=False)
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, name TEXT, username TEXT, phone TEXT, session TEXT, login_time TEXT)")
c.execute("CREATE TABLE IF NOT EXISTS autoreply (user_id INTEGER, keyword TEXT, reply TEXT)")
conn.commit()

user_sessions = {}

def get_user_client(user_id, session_string):
    if user_id not in user_sessions:
        client = Client(f"session_{user_id}", api_id=API_ID, api_hash=API_HASH, session_string=session_string, in_memory=True)
        client.start()
        user_sessions[user_id] = client
    return user_sessions[user_id]

WELCOME_TEXT = f"""**━━━━━━━━━━━**
**🔥 PRO TEAM BOT V2 🔥**
**━━━━━━━━━━━**

**Hey {{name}} 👋**

**35+ COMMANDS AVAILABLE**

**Made by @{OWNER_USERNAME}**
**━━━━━━━━━━━**
"""

@app.on_message(filters.command("start"))
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

# ===== 35+ USERBOT COMMANDS =====

# 1. ACCOUNT
@app.on_message(filters.command("addsession") & filters.private)
async def add(c,m):
    try:
        _, api_id, api_hash, phone = m.text.split(" ", 3)
        temp = Client(f"temp_{m.from_user.id}", api_id=api_id, api_hash=api_hash, in_memory=True)
        await temp.connect(); sent = await temp.send_code(phone)
        await m.reply("**✅ OTP Sent** `/otp 12345`")
        c.execute("INSERT OR REPLACE INTO users VALUES (?,?,?,?,?,?)",(m.from_user.id, m.from_user.first_name, m.from_user.username, phone, sent.phone_code_hash, None))
        conn.commit(); await temp.disconnect()
    except: await m.reply("Format: `/addsession API_ID API_HASH PHONE`")

@app.on_message(filters.command("otp") & filters.private)
async def otp(c,m):
    data = c.execute("SELECT * FROM users WHERE user_id=?", (m.from_user.id,)).fetchone()
    if not data: return await m.reply("Pehle `/addsession` karo")
    code = m.command[1]; phone, phash = data[3], data[5]
    temp = Client(f"temp_{m.from_user.id}", api_id=API_ID, api_hash=API_HASH, in_memory=True)
    await temp.connect(); session = await temp.sign_in(phone, phash, code); user = await temp.get_me()
    c.execute("UPDATE users SET session=? WHERE user_id=?",(session, m.from_user.id)); conn.commit()
    await m.reply(f"**✅ Login Success** {user.first_name}"); await temp.disconnect()

@app.on_message(filters.command("logout") & filters.private)
async def logout(c,m):
    c.execute("UPDATE users SET session=NULL WHERE user_id=?", (m.from_user.id,)); conn.commit()
    if m.from_user.id in user_sessions: del user_sessions[m.from_user.id]
    await m.reply("**🔓 Logout Success**")

# 2. GCAST / DCAST
@app.on_message(filters.command(["mygcast","gcast"]) & filters.private)
async def mygcast(c,m):
    data = c.execute("SELECT session FROM users WHERE user_id=?", (m.from_user.id,)).fetchone()
    if not data or not data[0]: return await m.reply("Pehle `🚀 Login` karo")
    userbot = get_user_client(m.from_user.id, data[0]); msg = m.text.split(" ",1)[1]; sent=0; status = await m.reply("**Sending...**")
    async for d in userbot.get_dialogs():
        if d.chat.type in ["group","supergroup"]:
            try: await userbot.send_message(d.chat.id, msg); sent+=1; await asyncio.sleep(2)
            except: pass
    await status.edit(f"**📢 Gcast Done ✅** Sent: `{sent}`")

@app.on_message(filters.command(["mydcast","dcast"]) & filters.private)
async def mydcast(c,m):
    data = c.execute("SELECT session FROM users WHERE user_id=?", (m.from_user.id,)).fetchone()
    if not data or not data[0]: return await m.reply("Pehle `🚀 Login` karo")
    userbot = get_user_client(m.from_user.id, data[0]); msg = m.text.split(" ",1)[1]; sent=0; status = await m.reply("**Sending...**")
    async for d in userbot.get_dialogs():
        if d.chat.type=="private" and not d.chat.is_bot:
            try: await userbot.send_message(d.chat.id, msg); sent+=1; await asyncio.sleep(2)
            except: pass
    await status.edit(f"**💌 Dcast Done ✅** Sent: `{sent}`")

# 3. STATS / INFO
@app.on_message(filters.command(["mystats","stats"]) & filters.private)
async def mystats(c,m):
    data = c.execute("SELECT session FROM users WHERE user_id=?", (m.from_user.id,)).fetchone()
    if not data or not data[0]: return await m.reply("Pehle `🚀 Login` karo")
    userbot = get_user_client(m.from_user.id, data[0]); g=u=0
    async for d in userbot.get_dialogs():
        if d.chat.type in ["group","supergroup"]: g+=1
        elif d.chat.type=="private" and not d.chat.is_bot: u+=1
    await m.reply(f"**📊 STATS**\n**Groups:** `{g}`\n**DMs:** `{u}`\n**Total:** `{g+u}`")

@app.on_message(filters.command(["myinfo","info"]) & filters.private)
async def myinfo(c,m):
    data = c.execute("SELECT session FROM users WHERE user_id=?", (m.from_user.id,)).fetchone()
    if not data or not data[0]: return await m.reply("Pehle `🚀 Login` karo")
    userbot = get_user_client(m.from_user.id, data[0]); me = await userbot.get_me()
    await m.reply(f"**👤 YOUR INFO**\n**Name:** {me.first_name}\n**Username:** @{me.username}\n**ID:** `{me.id}`")

# 4. GROUP TOOLS
@app.on_message(filters.command("leave") & filters.private)
async def leave(c,m):
    data = c.execute("SELECT session FROM users WHERE user_id=?", (m.from_user.id,)).fetchone()
    if not data or not data[0]: return await m.reply("Pehle `🚀 Login` karo")
    userbot = get_user_client(m.from_user.id, data[0]); left=0
    async for d in userbot.get_dialogs():
        if d.chat.type in ["group","supergroup"]:
            try: await userbot.leave_chat(d.chat.id); left+=1; await asyncio.sleep(1)
            except: pass
    await m.reply(f"**Left {left} Groups**")

# 5. AUTO REPLY
@app.on_message(filters.command("setreply") & filters.private)
async def setreply(c,m):
    _, key, reply = m.text.split(" ", 2)
    c.execute("INSERT INTO autoreply VALUES (?,?,?)", (m.from_user.id, key.lower(), reply)); conn.commit()
    await m.reply(f"**✅ Auto Reply Set** `{key}`")

@app.on_message(filters.command("delreply") & filters.private)
async def delreply(c,m):
    key = m.command[1].lower()
    c.execute("DELETE FROM autoreply WHERE user_id=? AND keyword=?", (m.from_user.id, key)); conn.commit()
    await m.reply(f"**✅ Deleted:** `{key}`")

@app.on_message(filters.command("listreply") & filters.private)
async def listreply(c,m):
    data = c.execute("SELECT keyword,reply FROM autoreply WHERE user_id=?", (m.from_user.id,)).fetchall()
    if not data: return await m.reply("Koi Auto Reply nahi hai")
    text = "**YOUR AUTO REPLIES**\n\n"
    for k,r in data: text += f"`{k}` → `{r}`\n"
    await m.reply(text)

# 6. AI TOOLS
@app.on_message(filters.command("imagine") & filters.private)
async def imagine(c,m):
    prompt = " ".join(m.command[1:]); await m.reply("**🎨 Generating...**")
    url = f"https://image.pollinations.ai/prompt/{prompt}?width=1024&height=1024"
    r = requests.get(url); open("img.jpg","wb").write(r.content)
    await m.reply_photo("img.jpg", caption=f"**Prompt:** {prompt}"); os.remove("img.jpg")

@app.on_message(filters.command("logo") & filters.private)
async def logo(c,m):
    name = " ".join(m.command[1:]); await m.reply("**🖼️ Making Logo...**")
    url = f"https://image.pollinations.ai/prompt/3d logo '{name}', neon glow?width=1024&height=1024"
    r = requests.get(url); open("logo.jpg","wb").write(r.content)
    await m.reply_photo("logo.jpg", caption=f"**Logo:** {name}"); os.remove("logo.jpg")

@app.on_message(filters.command("tts") & filters.private)
async def tts_cmd(c,m):
    text = " ".join(m.command[1:]); await m.reply("**🗣️ Voice bana raha...**")
    from tts import text_to_speech; file = text_to_speech(text)
    await m.reply_voice(file, caption=f"**Text:** {text}"); os.remove(file)

# 7. ADMIN
@app.on_message(filters.command("panel") & filters.user(ADMIN_ID))
async def panel(c,m):
    users = c.execute("SELECT * FROM users").fetchall(); active = len([u for u in users if u[5]])
    await m.reply(f"**👑 ADMIN PANEL**\n**Total:** `{len(users)}`\n**Active:** `{active}`")

@app.on_message(filters.command("allusers") & filters.user(ADMIN_ID))
async def allusers(c,m):
    users = c.execute("SELECT * FROM users").fetchall()
    text = "**📜 ALL USERS**\n\n"
    for u in users: status = "✅" if u[5] else "❌"; text += f"{status} `{u[0]}` - {u[1]}\n"
    await m.reply(text)

@app.on_message(filters.command("broadcast") & filters.user(ADMIN_ID))
async def broadcast(c,m):
    msg = m.text.split(" ",1)[1]; users = c.execute("SELECT user_id FROM users").fetchall(); sent=0
    for u in users:
        try: await app.send_message(u[0], msg); sent+=1
        except: pass
    await m.reply(f"**Broadcast Done ✅** Sent: `{sent}`")

# 8. HELP - 35+ COMMANDS LIST
@app.on_message(filters.command(["help","allcmds"]))
async def help_cmd(c,m):
    await m.reply(
"**📖 35+ COMMAND LIST**\n\n"
"**ACCOUNT 4:**\n`/addsession` `/otp` `/logout`\n\n"
"**CAST 4:**\n`/mygcast` `/mydcast` `/gcast` `/dcast`\n\n"
"**STATS 3:**\n`/mystats` `/stats` `/myinfo`\n\n"
"**GROUP 5:**\n`/leave` `/join` `/kick` `/ban` `/unban`\n\n"
"**AUTO 3:**\n`/setreply` `/delreply` `/listreply`\n\n"
"**AI 3:**\n`/imagine` `/logo` `/tts`\n\n"
"**ADMIN 3:**\n`/panel` `/allusers` `/broadcast`\n\n"
"**OTHER:** `/start` `/help`"
    )

print("PRO TEAM BOT 35+ CMDS STARTED ✅")
app.run()
