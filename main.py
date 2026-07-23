from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup, KeyboardButton
from pyrogram.errors import SessionPasswordNeeded, PhoneCodeInvalid, PasswordHashInvalid
from pytgcalls import PyTgCalls
from pytgcalls.types import StreamType
from pytgcalls.types.input_stream import AudioPiped
import sqlite3, os, asyncio, datetime, random, yt_dlp
from gtts import gTTS
from PIL import Image, ImageDraw, ImageFont
import io

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
OWNER_USERNAME = os.getenv("OWNER_USERNAME")
LOG_GROUP = int(os.getenv("LOG_GROUP"))

bot = Client("pro_team_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
vc = PyTgCalls(bot) # VC ke liye

conn = sqlite3.connect("team.db", check_same_thread=False)
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, name TEXT, username TEXT, phone TEXT, session TEXT)")
c.execute("CREATE TABLE IF NOT EXISTS autoreply (user_id INTEGER, keyword TEXT, reply TEXT)")
c.execute("CREATE TABLE IF NOT EXISTS scraped (user_id INTEGER, chat_id INTEGER)") # Scrape ke liye
conn.commit()

user_sessions = {}
login_temp = {}
vc_chats = {} # VC me kya chal raha

async def get_user_client(user_id):
    data = c.execute("SELECT session FROM users WHERE user_id=?", (user_id,)).fetchone()
    if not data or not data[0]: return None
    if user_id not in user_sessions:
        client = Client(f"session_{user_id}", api_id=API_ID, api_hash=API_HASH, session_string=data[0], in_memory=True)
        await client.start()
        user_sessions[user_id] = client
    return user_sessions[user_id]

async def send_log(text):
    try: await bot.send_message(LOG_GROUP, text)
    except: pass

# Shayari + Flirt list
SHAYARI = ["Tere naam se mohabbat ki hai...", "Chand se roshan hai chehra tera..."]
FLIRT = ["Tum haste ho to dil garden ho jata hai", "Tum chai ho aur main biscuit"]

WELCOME_TEXT = """**━━━━━━━━━━━**
**🔥 ISHIKA USER BOT V1 ULTIMATE 🔥**
**━━━━━━━━━━━**
**Hey {name} 👋**
**50+ COMMANDS AVAILABLE**
Buttons se use kar 👇
**Made by @{owner}**
**━━━━━━━━━━━**
"""

@bot.on_message(filters.command("start"))
async def start(c,m):
    uid = m.from_user.id; name = m.from_user.first_name; username = f"@{m.from_user.username}" if m.from_user.username else "None"
    login_temp.pop(uid, None)
    time = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    await send_log(f"**🚀 NEW START**\n**Name:** {name}\n**ID:** `{uid}`\n**Time:** `{time}`")
    buttons = [[KeyboardButton("🚀 Login"), KeyboardButton("🔓 Logout")],[KeyboardButton("📢 Gcast"), KeyboardButton("💌 Dcast")],[KeyboardButton("📊 Stats"), KeyboardButton("👤 Info")],[KeyboardButton("🎨 Imagine"), KeyboardButton("🖼️ Logo")],[KeyboardButton("🗣️ TTS"), KeyboardButton("⚡ AutoReply")],[KeyboardButton("📋 All Cmds"), KeyboardButton("👑 Owner")]]
    if uid == ADMIN_ID: buttons.append([KeyboardButton("👑 Admin Panel"), KeyboardButton("📜 All Users")])
    await m.reply(WELCOME_TEXT.format(name=name, owner=OWNER_USERNAME), reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True))

@bot.on_message(filters.command("loginstring"))
async def login_string(c,m): # NAYA STRING SESSION
    await m.reply("**API_ID, API_HASH, PHONE bhejo format me:**\n`api_id api_hash +91xxxxxxxxxx`")

@bot.on_message(filters.command("broadcast") & filters.user(ADMIN_ID)) # NAYA BROADCAST
async def broadcast(c,m):
    msg = m.text.split(" ",1)[1]
    users = c.execute("SELECT user_id FROM users").fetchall()
    for u in users:
        try: await bot.send_message(u[0], f"**📢 BROADCAST**\n\n{msg}"); await asyncio.sleep(0.5)
        except: pass
    await m.reply("**✅ Broadcast Done**")

@bot.on_message(filters.command("scrape")) # NAYA SCRAPE
async def scrape(c,m):
    userbot = await get_user_client(m.from_user.id)
    if not userbot: return await m.reply("**Pehle Login**")
    chat = m.text.split(" ",1)[1]
    chat = await userbot.get_chat(chat)
    count=0
    async for member in userbot.get_chat_members(chat.id):
        c.execute("INSERT OR IGNORE INTO scraped VALUES (?,?)", (member.user.id, chat.id)); count+=1
    conn.commit(); await m.reply(f"**✅ {count} Members Scraped**")

@bot.on_message(filters.command("join")) # NAYA JOIN
async def join(c,m):
    userbot = await get_user_client(m.from_user.id)
    if not userbot: return await m.reply("**Pehle Login**")
    link = m.text.split(" ",1)[1]
    await userbot.join_chat(link); await m.reply("**✅ Joined**")

@bot.on_message(filters.command("tagall")) # NAYA TAGALL
async def tagall(c,m):
    userbot = await get_user_client(m.from_user.id)
    if not userbot: return await m.reply("**Pehle Login**")
    msg = m.text.split(" ",1)[1] if len(m.text.split())>1 else "Tagging..."
    txt=""; count=0
    async for member in userbot.get_chat_members(m.chat.id):
        txt += f"[{member.user.first_name}](tg://user?id={member.user.id}) "
        count+=1
        if count==5: await m.reply(txt+"\n"+msg); txt=""; count=0; await asyncio.sleep(2)
    if txt: await m.reply(txt+"\n"+msg)

@bot.on_message(filters.command("play")) # NAYA VC PLAY
async def play(c,m):
    userbot = await get_user_client(m.from_user.id)
    if not userbot: return await m.reply("**Pehle Login**")
    query = m.text.split(" ",1)[1]
    ydl_opts = {'format':'bestaudio', 'noplaylist':True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl: info = ydl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
    url = info['url']
    await vc.join_group_call(m.chat.id, AudioPiped(url), stream_type=StreamType().pulse_stream)
    await m.reply(f"**🎵 Playing:** {info['title']}")

@bot.on_message(filters.command("shayari")) # NAYA SHAYARI
async def shayari(c,m): await m.reply(random.choice(SHAYARI))

@bot.on_message(filters.command("flirt")) # NAYA FLIRT
async def flirt(c,m): await m.reply(random.choice(FLIRT))

# Baaki tere purane commands: gcast, dcast, stats, info, imagine, logo, tts, setreply, delreply, listreply, admin, allusers, allcmds

@bot.on_message(filters.command("allcmds"))
async def all_cmds(c,m):
    txt = """**📋 50+ COMMANDS LIST V8**

**USERBOT:**
`/gcast` `/dcast` `/stats` `/info` `/scrape` `/join` `/leave` `/tagall`

**VC:**
`/play song name` `/stop`

**AI & FUN:**
`/imagine` `/logo` `/tts` `/shayari` `/flirt`

**UTILITY:**
`/setreply` `/delreply` `/listreply` `/broadcast`

**LOGIN:**
Buttons: Login / Logout / `/loginstring`

**ADMIN:**
`/admin` `/allusers`"""
    await m.reply(txt)

@vc.on_stream_end()
async def stream_end_handler(_, update): await vc.leave_group_call(update.chat_id)

print("ISHIKA USER BOT V1 ULTIMATE STARTED ✅")
bot.run()
