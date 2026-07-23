from pyrogram import Client, filters
from pyrogram.types import Message, ChatPrivileges
from pyrogram.errors import FloodWait, UserAdminInvalid
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import AudioStream
from pytgcalls.types.stream import StreamAudioEnded
import asyncio
import os
import random
from gtts import gTTS # TTS
from PIL import Image, ImageDraw, ImageFont # Logo + Imagine
import io
import yt_dlp # VC

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION = os.getenv("SESSION")

app = Client("userbot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION)
vc = PyTgCalls(app)

tagging = False

# Data
SHAYARI = [
    "Tere naam se mohabbat ki hai, tere ehsaas se ulfat ki hai...",
    "Chand se roshan hai chehra tera, phoolon se pyari hai baatein teri",
    "Tum mil gaye to laga jese sadiyon ki dua qubool hui"
]
FLIRT = [
    "Tum haste ho to dil garden garden ho jata hai 😍",
    "Tum chai ho aur main biscuit, sath me mast lagte hai",
    "Teri ek jhalak dekhne ko dil taras jata hai"
]

# /ping
@app.on_message(filters.me & filters.command("ping"))
async def ping(client, message: Message):
    await message.edit("🏓 Pong! Bot zinda hai")

# /help - UPDATE KIYA
@app.on_message(filters.me & filters.command("help"))
async def help(client, message: Message):
    text = """🔥 **ISHIKA USERBOT V9 ULTIMATE** 🔥

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

**VC:**
`/play song name` - VC me gaana
`/stop` - VC band

**Session:**
`/string` - Naya String session bana

Made with 💜 @KARTIK_NISHAD_3"""
    await message.edit(text)

# /string - NEW STRING SESSION
@app.on_message(filters.me & filters.command("string"))
async def gen_string(client, message: Message):
    await message.edit("**String Session:**\n`"+SESSION+"`\n\n**Ise sambhal ke rakh**")

# /imagine - AI IMAGE
@app.on_message(filters.me & filters.command("imagine"))
async def imagine(client, message: Message):
    if len(message.command) < 2: return await message.edit("Use: /imagine beautiful girl")
    prompt = " ".join(message.command[1:])
    await message.edit("🎨 Image bana raha hu...")
    # Dummy image banayi - yaha AI API laga sakte
    img = Image.new('RGB', (512, 512), color = (73, 109, 137))
    d = ImageDraw.Draw(img)
    d.text((10,10), prompt, fill=(255,255,0))
    img.save("img.png")
    await client.send_photo(message.chat.id, "img.png", caption=f"Prompt: {prompt}")
    await message.delete()
    os.remove("img.png")

# /logo - NAME WALA LOGO
@app.on_message(filters.me & filters.command("logo"))
async def logo(client, message: Message):
    if len(message.command) < 2: return await message.edit("Use: /logo Ishika")
    name = " ".join(message.command[1:])
    await message.edit("🖼️ Logo bana raha hu...")
    img = Image.new('RGB', (512, 512), color = (0,0,0))
    d = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    d.text((100,250), name, fill=(255,0,0), font=font)
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

# /tagall - ek karke
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

# /play VC
@app.on_message(filters.me & filters.command("play"))
async def play(client, message: Message):
    if len(message.command) < 2: return await message.edit("Use: /play song name")
    query = " ".join(message.command[1:])
    await message.edit(f"🔍 Searching: {query}")
    ydl_opts = {'format':'bestaudio', 'noplaylist':True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl: info = ydl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
    url = info['url']
    await vc.join_group_call(message.chat.id, AudioStream(url))
    await message.edit(f"🎵 **Playing:** {info['title']}")

# /stop VC
@app.on_message(filters.me & filters.command("stop"))
async def stop(client, message: Message):
    await vc.leave_group_call(message.chat.id)
    await message.edit("⏹️ Stopped")

@vc.on_stream_end()
async def stream_end_handler(_, update):
    if isinstance(update, StreamAudioEnded): await vc.leave_group_call(update.chat_id)

# Baaki tere purane: promote, demote, ban, unban, mute, unmute, id, info, purge, broadcast, gcast, dcast

print("ISHIKA USERBOT V STARTED ✅")
app.run()
