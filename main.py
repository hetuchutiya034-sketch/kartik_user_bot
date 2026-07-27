from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait
import os, asyncio, random

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION = os.getenv("SESSION")

app = Client("deviluserbot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION)

# ================== SETTINGS ==================
DEVIL_MODE = True
OWNER = "https://t.me/KARTIK_NISHAD_3"

def devil_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔥 Deploy", url="https://railway.app")],
        [InlineKeyboardButton("👑 Owner", url=OWNER)]
    ])

# ================== BASIC ==================
@app.on_message(filters.me & filters.command("ping"))
async def ping(client, message: Message):
    await message.edit("🏓 Pong! Bot Working 😈", reply_markup=devil_buttons())

@app.on_message(filters.me & filters.command("help"))
async def help_cmd(client, message: Message):
    txt = """🔥 ULTRA DEVIL USERBOT 🔥

⚡ BASIC
.ping - Check bot
.help - This menu
.devil - ON/OFF Devil Mode

😂 FUN
.shayari
.flirt
.joke

👥 GROUP
.tagall - Tag everyone
.cancel - Stop tagging

💣 SPAM
.spam [count] [text]"""
    await message.edit(txt, reply_markup=devil_buttons())

# ================== DEVIL MODE TOGGLE ==================
@app.on_message(filters.me & filters.command("devil"))
async def devil_toggle(client, message: Message):
    global DEVIL_MODE
    DEVIL_MODE = not DEVIL_MODE
    status = "ON 😈" if DEVIL_MODE else "OFF 🛑"
    await message.edit(f"DEVIL MODE {status}", reply_markup=devil_buttons())

# ================== AUTO DEVIL REPLY ================== FIXED
@app.on_message(filters.incoming & filters.text & ~filters.bot & ~filters.me)
async def auto_reply(client, message: Message):
    if DEVIL_MODE:
        try:
            replies = [
                f"😈 Devil: {message.text}",
                f"🔥 Bolo kya baat hai? {message.text}",
                f"😈 Haan? {message.text}"
            ]
            await message.reply(random.choice(replies), reply_markup=devil_buttons())
        except:
            pass

# ================== FUN ==================
SHAYARI = [
    "तुम हँसते हो तो दिल खुश हो जाता है ❤️",
    "मोहब्बत है तुमसे ❤️",
    "तुम बहुत खास हो 😍"
]
FLIRT = ["Tum cute ho 😍", "Tumse baat karke accha lagta hai ❤️"]
JOKES = ["Teacher: 2+2? Student: 5 😂", "Doctor: सो जाओ 😂"]

@app.on_message(filters.me & filters.command("shayari"))
async def shayari_cmd(client, message: Message):
    await message.edit(random.choice(SHAYARI), reply_markup=devil_buttons())

@app.on_message(filters.me & filters.command("flirt"))
async def flirt_cmd(client, message: Message):
    await message.edit(random.choice(FLIRT), reply_markup=devil_buttons())

@app.on_message(filters.me & filters.command("joke"))
async def joke_cmd(client, message: Message):
    await message.edit(random.choice(JOKES), reply_markup=devil_buttons())

# ================== TAG ALL ================== FIXED
tagging = False

@app.on_message(filters.me & filters.command("tagall"))
async def tagall(client, message: Message):
    global tagging
    tagging = True
    await message.delete()
    mentions = ""
    count = 0
    try:
        async for member in client.get_chat_members(message.chat.id):
            if not tagging: break
            if not member.user.is_bot:
                mentions += f"[{member.user.first_name}](tg://user?id={member.user.id}) "
                count += 1
                if count == 5:
                    await client.send_message(message.chat.id, mentions, reply_markup=devil_buttons())
                    mentions = ""
                    count = 0
                    await asyncio.sleep(2)
        if mentions:
            await client.send_message(message.chat.id, mentions, reply_markup=devil_buttons())
    except FloodWait as e:
        await asyncio.sleep(e.value)

@app.on_message(filters.me & filters.command("cancel"))
async def cancel(client, message: Message):
    global tagging
    tagging = False
    await message.edit("⛔ Tagging Stopped", reply_markup=devil_buttons())

# ================== SPAM ================== FIXED
@app.on_message(filters.me & filters.command("spam"))
async def spam(client, message: Message):
    if len(message.command) < 3:
        return await message.edit("Use:.spam 5 hello")
    try:
        count = int(message.command[1])
    except:
        return await message.edit("Count number me do")
    if count > 50:
        return await message.edit("⚠️ Max 50 hi kar sakte ho warna ban ho jaoge")
    text = " ".join(message.command[2:])
    await message.delete()
    for i in range(count):
        try:
            await client.send_message(message.chat.id, text)
            await asyncio.sleep(0.5) # safe delay
        except FloodWait as e:
            await asyncio.sleep(e.value)

# ================== START ==================
print("🔥 ULTRA DEVIL USERBOT STARTED 🔥")
app.run()
