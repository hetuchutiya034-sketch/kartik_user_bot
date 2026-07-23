from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup, KeyboardButton
import sqlite3, os, asyncio, datetime, requests

# ===== CONFIG - RAILWAY VARIABLES ME DAALNA =====
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

# ===== FANCY WELCOME =====
WELCOME_TEXT = f"""**━━━━━━━━━━━━━━━━━━━**
**🔥 WELCOME TO PRO TEAM BOT 🔥**
**━━━━━━━━━━━**

**Hey {{name}} 👋**

Ye bot tumhare **Personal Telegram Account** se kaam karega.

**⚡ FEATURES ⚡**
- `📢 Gcast` - 1 Click me sab Group me msg
- `💌 Dcast` - 1 Click me sab DM me msg
- `⚡ Auto Reply` - Keyword pe auto reply
- `📊 Live Stats` - Groups + DM count
- `🎨 Imagine` - AI se image banao
- `🖼️ Logo Maker` - Apne naam ka logo

**📝 RULES**
1. Pehle `🚀 Login` button se account add karo
2. Spam mat karna warna Telegram ban karega
3. Koi problem ho to `👑 Owner` se contact karo

**━━━━━━━━━━━**
**Made with ❤️ by @{OWNER_USERNAME}**
**━━━━━━━━━━━━━━━━━━━**
"""

# ===== /START =====
@app.on_message(filters.command("start"))
async def start(c,m):
    uid = m.from_user.id
    name = m.from_user.first_name

    buttons = [
        [KeyboardButton("🚀 Login"), KeyboardButton("🔓 Logout")],
        [KeyboardButton("📢 My Gcast"), KeyboardButton("💌 My Dcast")],
        [KeyboardButton("📊 My Stats"), KeyboardButton("⚡ Auto Reply")],
        [KeyboardButton("🎨 Imagine"), KeyboardButton("🖼️ Logo")],
        [KeyboardButton("❓ Help"), KeyboardButton("👑 Owner Support")]
    ]
    if uid == ADMIN_ID:
        buttons.append([KeyboardButton("👑 Admin Panel"), KeyboardButton("📜 All Users"), KeyboardButton("📢 Broadcast")])

    await m.reply(WELCOME_TEXT.format(name=name), reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True))

# ===== BUTTON HANDLER =====
@app.on_message(filters.text & filters.private)
async def button_handler(c,m):
    text = m.text
    uid = m.from_user.id

    if text == "🚀 Login": await m.reply("**Format:**\n`/addsession API_ID API_HASH +91XXXXXXXXXX`")
    elif text == "🔓 Logout": await logout(c,m)
    elif text == "📢 My Gcast": await m.reply("**Format:**\n`/mygcast Your Message`")
    elif text == "💌 My Dcast": await m.reply("**Format:**\n`/mydcast Your Message`")
    elif text == "📊 My Stats": await mystats(c,m)
    elif text == "⚡ Auto Reply": await m.reply("`/setreply hi Hello`\n`/delreply hi`\n`/listreply`")
    elif text == "🎨 Imagine": await m.reply("**Format:**\n`/imagine sunset beach`")
    elif text == "🖼️ Logo": await m.reply("**Format:**\n`/logo Your Name`")
    elif text == "❓ Help": await help_cmd(c,m)
    elif text == "👑 Owner Support": await m.reply(f"**Problem hai?**\nMujhe DM karo: [@{OWNER_USERNAME}](https://t.me/{OWNER_USERNAME})", disable_web_page_preview=True)
    elif text == "👑 Admin Panel":
        if uid==ADMIN_ID: await panel(c,m)
    elif text == "📜 All Users":
        if uid==ADMIN_ID: await allusers(c,m)
    elif text == "📢 Broadcast":
        if uid==ADMIN_ID: await m.reply("**Format:**\n`/broadcast Your Message`")

# ===== LOGIN / OTP / LOGOUT =====
@app.on_message(filters.command("addsession") & filters.private)
async def add(c,m):
    try:
        _, api_id, api_hash, phone = m.text.split(" ", 3)
        temp = Client(f"temp_{m.from_user.id}", api_id=api_id, api_hash=api_hash, in_memory=True)
        await temp.connect()
        sent = await temp.send_code(phone)
        await m.reply("**✅ OTP Sent**\nAb `/otp 12345` bhejo")
        c.execute("INSERT OR REPLACE INTO users (user_id, name, username, phone, session) VALUES (?,?,?,?,?)",
        (m.from_user.id, m.from_user.first_name, m.from_user.username, phone, sent.phone_code_hash))
        conn.commit()
        await temp.disconnect()
    except: await m.reply("**Format:** `/addsession API_ID API_HASH +91XXXXXXXXXX`")

@app.on_message(filters.command("otp") & filters.private)
async def otp(c,m):
    data = c.execute("SELECT * FROM users WHERE user_id=?", (m.from_user.id,)).fetchone()
    if not data: return await m.reply("Pehle `/addsession` karo")
    code = m.command[1]; phone, phash = data[3], data[5]
    temp = Client(f"temp_{m.from_user.id}", api_id=API_ID, api_hash=API_HASH, in_memory=True)
    await temp.connect()
    session = await temp.sign_in(phone, phash, code)
    user = await temp.get_me()
    login_time = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
    c.execute("UPDATE users SET session=?, name=?, username=?, login_time=? WHERE user_id=?",(session, user.first_name, user.username, login_time, m.from_user.id))
    conn.commit()
    await m.reply(f"**✅ Login Success**\n**Name:** {user.first_name}\nAb bot use karo")
    await temp.disconnect()

@app.on_message(filters.command("logout") & filters.private)
async def logout(c,m):
    c.execute("UPDATE users SET session=NULL WHERE user_id=?", (m.from_user.id,))
    conn.commit()
    if m.from_user.id in user_sessions: del user_sessions[m.from_user.id]
    await m.reply("**🔓 Logout Success**")

# ===== USERBOT GCAST / DCAST / STATS =====
@app.on_message(filters.command("mygcast") & filters.private)
async def mygcast(c,m):
    data = c.execute("SELECT session FROM users WHERE user_id=?", (m.from_user.id,)).fetchone()
    if not data or not data[0]: return await m.reply("Pehle `🚀 Login` karo")
    userbot = get_user_client(m.from_user.id, data[0])
    msg = m.text.split(" ",1)[1]; sent=0
    status = await m.reply("**Sending...**")
    async for d in userbot.get_dialogs():
        if d.chat.type in ["group","supergroup"]:
            try: await userbot.send_message(d.chat.id, msg); sent+=1; await asyncio.sleep(3)
            except: pass
    await status.edit(f"**📢 Gcast Done ✅**\nSent: `{sent}` Groups")

@app.on_message(filters.command("mydcast") & filters.private)
async def mydcast(c,m):
    data = c.execute("SELECT session FROM users WHERE user_id=?", (m.from_user.id,)).fetchone()
    if not data or not data[0]: return await m.reply("Pehle `🚀 Login` karo")
    userbot = get_user_client(m.from_user.id, data[0])
    msg = m.text.split(" ",1)[1]; sent=0
    status = await m.reply("**Sending...**")
    async for d in userbot.get_dialogs():
        if d.chat.type=="private" and not d.chat.is_bot:
            try: await userbot.send_message(d.chat.id, msg); sent+=1; await asyncio.sleep(3)
            except: pass
    await status.edit(f"**💌 Dcast Done ✅**\nSent: `{sent}` DMs")

@app.on_message(filters.command("mystats") & filters.private)
async def mystats(c,m):
    data = c.execute("SELECT session FROM users WHERE user_id=?", (m.from_user.id,)).fetchone()
    if not data or not data[0]: return await m.reply("Pehle `🚀 Login` karo")
    userbot = get_user_client(m.from_user.id, data[0])
    g=u=0
    async for d in userbot.get_dialogs():
        if d.chat.type in ["group","supergroup"]: g+=1
        elif d.chat.type=="private" and not d.chat.is_bot: u+=1
    await m.reply(f"**📊 YOUR STATS**\n\n**Groups:** `{g}`\n**DMs:** `{u}`\n**Total:** `{g+u}`")

# ===== AUTO REPLY =====
@app.on_message(filters.command("setreply") & filters.private)
async def setreply(c,m):
    try:
        _, key, reply = m.text.split(" ", 2)
        c.execute("INSERT INTO autoreply VALUES (?,?,?)", (m.from_user.id, key.lower(), reply))
        conn.commit()
        await m.reply(f"**✅ Auto Reply Set**\nKeyword: `{key}`")
    except: await m.reply("Format: `/setreply hi Hello`")

@app.on_message(filters.command("delreply") & filters.private)
async def delreply(c,m):
    key = m.command[1].lower()
    c.execute("DELETE FROM autoreply WHERE user_id=? AND keyword=?", (m.from_user.id, key))
    conn.commit()
    await m.reply(f"**✅ Deleted:** `{key}`")

@app.on_message(filters.command("listreply") & filters.private)
async def listreply(c,m):
    data = c.execute("SELECT keyword,reply FROM autoreply WHERE user_id=?", (m.from_user.id,)).fetchall()
    if not data: return await m.reply("Koi Auto Reply nahi hai")
    text = "**YOUR AUTO REPLIES**\n\n"
    for k,r in data: text += f"`{k}` → `{r}`\n"
    await m.reply(text)

# ===== IMAGE + LOGO =====
@app.on_message(filters.command("imagine") & filters.private)
async def imagine(c,m):
    if len(m.command) < 2: return await m.reply("**Format:** `/imagine ai robot`")
    prompt = " ".join(m.command[1:])
    await m.reply("**🎨 Generating... 10 sec wait**")
    try:
        url = f"https://image.pollinations.ai/prompt/{prompt}?width=1024&height=1024"
        r = requests.get(url)
        with open("img.jpg", "wb") as f: f.write(r.content)
        await m.reply_photo("img.jpg", caption=f"**Prompt:** {prompt}")
        os.remove("img.jpg")
    except: await m.reply("Error generating image")

@app.on_message(filters.command("logo") & filters.private)
async def logo(c,m):
    if len(m.command) < 2: return await m.reply("**Format:** `/logo PRO KING`")
    name = " ".join(m.command[1:])
    await m.reply("**🖼️ Making Logo...**")
    try:
        url = f"https://image.pollinations.ai/prompt/3d glossy logo text '{name}', neon glow, black background, professional logo design?width=1024&height=1024"
        r = requests.get(url)
        with open("logo.jpg", "wb") as f: f.write(r.content)
        await m.reply_photo("logo.jpg", caption=f"**Logo for:** {name}")
        os.remove("logo.jpg")
    except: await m.reply("Error generating logo")

# ===== ADMIN =====
@app.on_message(filters.command("panel") & filters.user(ADMIN_ID))
async def panel(c,m):
    users = c.execute("SELECT * FROM users").fetchall()
    active = len([u for u in users if u[5]])
    await m.reply(f"**👑 ADMIN PANEL**\n\n**Total Users:** `{len(users)}`\n**Active:** `{active}`")

@app.on_message(filters.command("allusers") & filters.user(ADMIN_ID))
async def allusers(c,m):
    users = c.execute("SELECT * FROM users").fetchall()
    text = "**📜 ALL USERS**\n\n"
    for u in users:
        status = "✅" if u[5] else "❌"
        text += f"{status} `{u[0]}` - {u[1]}\n"
    await m.reply(text)

@app.on_message(filters.command("broadcast") & filters.user(ADMIN_ID))
async def broadcast(c,m):
    msg = m.text.split(" ",1)[1]
    users = c.execute("SELECT user_id FROM users").fetchall()
    sent=0
    for u in users:
        try: await app.send_message(u[0], msg); sent+=1
        except: pass
    await m.reply(f"**Broadcast Done ✅**\nSent: `{sent}`")

@app.on_message(filters.command("help"))
async def help_cmd(c,m):
    await m.reply(
"**📖 FULL COMMAND LIST**\n\n"
"**ACCOUNT:**\n`/addsession API_ID API_HASH PHONE`\n`/otp CODE`\n`/logout`\n\n"
"**FEATURES:**\n`/mygcast msg`\n`/mydcast msg`\n`/mystats`\n\n"
"**AUTO REPLY:**\n`/setreply key reply`\n`/delreply key`\n`/listreply`\n\n"
"**AI:**\n`/imagine prompt`\n`/logo name`"
    )

print("PRO TEAM BOT STARTED ✅")
app.run()
