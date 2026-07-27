from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import os, asyncio, random

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION = os.getenv("SESSION")

app = Client("deviluserbot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION)

# ================== SETTINGS ==================
DEVIL_MODE = True

SUPPORT_GROUP = "https://t.me/+AAB-iIMnebBmMWZl"
UPDATE_CHANNEL = "https://t.me/+AAB-iIMnebBmMWZl"
OWNER = "https://t.me/KARTIK_NISHAD_3"

# ================== BUTTON ==================
def devil_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔥 Deploy", url="https://railway.app")],
        [InlineKeyboardButton("⚡ Available", url="https://t.me")],
        [InlineKeyboardButton("👑 Owner", url=OWNER)]
    ])

# ================== BASIC ==================
@app.on_message(filters.me & filters.command("ping"))
async def ping(client, message: Message):
    await message.edit("🏓 Pong! Bot Working 😈", reply_markup=devil_buttons())

@app.on_message(filters.me & filters.command("help"))
async def help_cmd(client, message: Message):
    txt = """
🔥 ULTRA DEVIL USERBOT 🔥

⚡ BASIC
.ping
.help
.devil

😂 FUN
.shayari
.flirt
.joke

👥 ADMIN
.tagall
.cancel

💣 SPECIAL
.spam
"""
    await message.edit(txt, reply_markup=devil_buttons())

# ================== DEVIL MODE ==================
@app.on_message(filters.me & filters.command("devil"))
async def devil_toggle(client, message: Message):
    global DEVIL_MODE
    DEVIL_MODE = not DEVIL_MODE
    await message.edit(f"😈 DEVIL MODE {'ON' if DEVIL_MODE else 'OFF'}", reply_markup=devil_buttons())

# ================== AUTO DEVIL REPLY ==================
@app.on_message(filters.me & filters.text)
async def auto_reply(client, message: Message):
    if DEVIL_MODE:
        try:
            await message.reply(
                f"😈 DEVIL MODE ACTIVE\n\n{message.text}",
                reply_markup=devil_buttons()
            )
        except:
            pass

# ================== FUN ==================
SHAYARI = [
    "तुम हँसते हो तो दिल खुश हो जाता है ❤️",
    "मोहब्बत है तुमसे ❤️",
    "तुम बहुत खास हो 😍"
]

FLIRT = [
    "Tum cute ho 😍",
    "Tumse baat karke accha lagta hai ❤️"
]

JOKES = [
    "Teacher: 2+2? Student: 5 😂",
    "Doctor: सो जाओ 😂"
]

@app.on_message(filters.me & filters.command("shayari"))
async def shayari(client, message: Message):
    await message.edit(random.choice(SHAYARI), reply_markup=devil_buttons())

@app.on_message(filters.me & filters.command("flirt"))
async def flirt(client, message: Message):
    await message.edit(random.choice(FLIRT), reply_markup=devil_buttons())

@app.on_message(filters.me & filters.command("joke"))
async def joke(client, message: Message):
    await message.edit(random.choice(JOKES), reply_markup=devil_buttons())

# ================== TAG ALL ==================
tagging = False

@app.on_message(filters.me & filters.command("tagall"))
async def tagall(client, message: Message):
    global tagging
    tagging = True
    await message.delete()

    async for user in client.get_chat_members(message.chat.id):
        if not tagging:
            break
        try:
            await client.send_message(
                message.chat.id,
                f"[{user.user.first_name}](tg://user?id={user.user.id})",
                reply_markup=devil_buttons()
            )
            await asyncio.sleep(2)
        except:
            pass

@app.on_message(filters.me & filters.command("cancel"))
async def cancel(client, message: Message):
    global tagging
    tagging = False
    await message.edit("⛔ Tagging Stopped", reply_markup=devil_buttons())

# ================== SPAM ==================
@app.on_message(filters.me & filters.command("spam"))
async def spam(client, message: Message):
    if len(message.command) < 3:
        return await message.edit("Use: .spam 5 hello")

    count = int(message.command[1])
    text = " ".join(message.command[2:])

    await message.delete()

    for i in range(count):
        await client.send_message(message.chat.id, text)
        await asyncio.sleep(0.3)

# ================== START ==================
print("🔥 ULTRA DEVIL USERBOT STARTED 🔥")
app.run()
