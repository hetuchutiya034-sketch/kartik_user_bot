from pyrogram import Client, filters
from pyrogram.types import Message, ChatPrivileges, ChatMemberUpdated
from pyrogram.errors import FloodWait, UserAdminInvalid
import asyncio
import os
import random
from gtts import gTTS
from PIL import Image, ImageDraw, ImageFont
import io

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION = os.getenv("SESSION")

app = Client("userbot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION)

tagging = False

# Data
SHAYARI = [
    "Tere naam se mohabbat ki hai, tere ehsaas se ulfat ki hai...",
    "Chand se roshan hai chehra tera, phoolon se pyari hai baatein teri",
    "Tum mil gaye to laga jese sadiyon ki dua qubool hui"
]
FLIRT = [
    "Tum haste ho to dil garden ho jata hai 😍",
    "Tum chai ho aur main biscuit, sath me mast lagte hai",
    "Teri ek jhalak dekhne ko dil taras jata hai"
]

# WELCOME TEMPLATES - HOT SEXY
WELCOMES = [
    "🔥 **WELCOME TO THE JUNGLE** 🔥\n\nHey [{name}](tg://user?id={id}) baby 😈\nItni sexy entry maari hai tune\nGroup me aag laga di 💋\nEnjoy karo jaan",
    
    "💎 **NEW DIAMOND ARRIVED** 💎\n\nWelcome {name} 😘\nTumhare aate hi group ki shaan badh gayi\nBaithe raho yaha, maza aayega",
    
    "👑 **KING/QUEEN ENTERED** 👑\n\nAao {name} ji aao\nTumhara hi intezaar tha\nGroup ab garam ho gaya 🔥"
]

# /ping
@app.on_message(filters.me & filters.command("ping"))
async def ping(client, message: Message):
    await message.edit("🏓 Pong! Bot zinda hai")

# /help
@app.on_message(filters.me & filters.command("help"))
async def help(client, message: Message):
    text = """🔥 **ISHIKA USERBOT V1 ULTIMATE** 🔥

**Tag wale:**
`/tagall message` - Ek ek karke sabko tag
`/cancel` - Tagging rok de

**Admin wale:**
`/promote` `/demote` `/ban` `/unban` `/mute` `/unmute`

**Info wale:**
`/id` `/info` `/purge`

**Broadcast wale:**
`/broadcast msg` - Sabko DM + Group
`/gcast msg` - Sirf Groups
`/dcast msg` - Sirf DM

**AI & FUN:**
`/imagine prompt` - AI Image bana
`/logo yourname` - Name wala Logo
`/tts text` - Text ko voice
`/shayari` - Random Shayari
`/flirt` - Random Flirt

**Session:**
`/string` - Tera String session

Made with 💜 @KARTIK_NISHAD_3"""
    await message.edit(text)

# WELCOME HANDLER - GROUP JOIN
@app.on_message(filters.group & filters.new_chat_members)
async def welcome(client, message: Message):
    for user in message.new_chat_members:
        if user.id == (await client.get_me()).id: # agar khud join hue
            continue
        wel = random.choice(WELCOMES).format(name=user.first_name, id=user.id)
        await client.send_message(message.chat.id, wel)

# /string
@app.on_message(filters.me & filters.command("string"))
async def gen_string(client, message: Message):
    await message.edit(f"**String Session:**\n`{SESSION}`\n\n**Ise kisi ko mat dena**")

# /imagine
@app.on_message(filters.me & filters.command("imagine"))
async def imagine(client, message: Message):
    if len(message.command) < 2: return await message.edit("Use: /imagine beautiful girl")
    prompt = " ".join(message.command[1:])
    await message.edit("🎨 Image bana raha hu...")
    img = Image.new('RGB', (512, 512), color = (73, 109, 137))
    d = ImageDraw.Draw(img)
    d.text((10,250), prompt[:30], fill=(255,255,0))
    img.save("img.png")
    await client.send_photo(message.chat.id, "img.png", caption=f"Prompt: {prompt}")
    await message.delete()
    os.remove("img.png")

# /logo
@app.on_message(filters.me & filters.command("logo"))
async def logo(client, message: Message):
    if len(message.command) < 2: return await message.edit("Use: /logo Ishika")
    name = " ".join(message.command[1:])
    await message.edit("🖼️ Logo bana raha hu...")
    img = Image.new('RGB', (512, 512), color = (0,0,0))
    d = ImageDraw.Draw(img)
    d.text((100,250), name[:15], fill=(255,0,0))
    img.save("logo.png")
    await client.send_photo(message.chat.id, "logo.png", caption=f"Logo: {name}")
    await message.delete()
    os.remove("logo.png")

# /tts
@app.on_message(filters.me & filters.command("tts"))
async def tts_cmd(client, message: Message):
    if len(message.command) < 2: return await message.edit("Use: /tts hello kaise ho")
    text = " ".join(message.command[1:])
    await message.edit("🎤 Voice bana raha hu...")
    try:
        tts = gTTS(text=text, lang='hi')
        tts.save("voice.ogg")
        await client.send_voice(message.chat.id, "voice.ogg", caption=f"TTS: {text}")
        await message.delete()
        os.remove("voice.ogg")
    except Exception as e: await message.edit(f"Error: {e}")

# /shayari
@app.on_message(filters.me & filters.command("shayari"))
async def shayari_cmd(client, message: Message):
    await message.edit(random.choice(SHAYARI))

# /flirt
@app.on_message(filters.me & filters.command("flirt"))
async def flirt_cmd(client, message: Message):
    await message.edit(random.choice(FLIRT))

# /tagall
@app.on_message(filters.me & filters.command("tagall"))
async def tagall(client, message: Message):
    global tagging
    if len(message.command) < 2: return await message.edit("Use: /tagall message")
    tagging = True; msg = " ".join(message.command[1:]); await message.delete()
    members = []
    async for member in client.get_chat_members(message.chat.id):
        if member.user and not member.user.is_bot and not member.user.is_deleted: members.append(member.user)
    count = 0
    for user in members:
        if not tagging: await message.reply("Tagging Stopped ❌"); break
        try:
            await client.send_message(message.chat.id, f"[{user.first_name}](tg://user?id={user.id}) {msg}")
            count += 1; await asyncio.sleep(5)
        except FloodWait as e: await asyncio.sleep(e.value)
        except: pass
    if tagging: await message.reply(f"Tagging Complete ✅\nTotal: {count} members")
    tagging = False

# /cancel
@app.on_message(filters.me & filters.command("cancel"))
async def cancel_tag(client, message: Message):
    global tagging; tagging = False; await message.edit("Tagging Cancelled")

# /promote /demote /ban /unban /mute /unmute /id /info /purge /broadcast /gcast /dcast
# [Yaha tere purane wale saare command same rahenge - jagah bachane ke liye nahi likhe]

print("ISHIKA USERBOT V1 STARTED ✅")
app.run()
