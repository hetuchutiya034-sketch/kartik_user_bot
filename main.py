from pyrogram import Client, filters
from pyrogram.types import Message, ChatPrivileges
from pyrogram.errors import FloodWait, UserAdminInvalid
import asyncio
import os
import random
from gtts import gTTS
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION = os.getenv("SESSION")

app = Client("userbot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION)

tagging = False
welcome_on = {} # har group ke liye alag welcome on/off

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

# HOT SEXY WELCOME
WELCOMES = [
    "🔥 **WELCOME TO THE JUNGLE** 🔥\n\nHey [{name}](tg://user?id={id}) baby 😈\nItni sexy entry maari hai tune\nGroup me aag laga di 💋",
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
    text = """🔥 **ISHIKA USERBOT V1.2 ULTIMATE** 🔥

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
`/anime name` - Anime BG par Name Logo
`/couple boy girl` - Couple Anime Logo
`/tts text` - Text ko voice
`/shayari` - Random Shayari
`/flirt` - Random Flirt

**Group:**
`/welcome on` - Welcome ON
`/welcome off` - Welcome OFF

**Session:**
`/string` - Tera String session

Made with 💜 @KARTIK_NISHAD_3"""
    await message.edit(text)

# /welcome on/off
@app.on_message(filters.me & filters.command("welcome") & filters.group)
async def welcome_toggle(client, message: Message):
    global welcome_on
    if len(message.command) < 2: return await message.edit("Use: `/welcome on` or `/welcome off`")
    chat_id = message.chat.id
    if message.command[1] == "on":
        welcome_on[chat_id] = True
        await message.edit("✅ Welcome ON kar diya is group me")
    elif message.command[1] == "off":
        welcome_on[chat_id] = False
        await message.edit("❌ Welcome OFF kar diya is group me")

# WELCOME HANDLER
@app.on_message(filters.group & filters.new_chat_members)
async def welcome(client, message: Message):
    chat_id = message.chat.id
    if not welcome_on.get(chat_id, True): return
    for user in message.new_chat_members:
        if user.is_self: continue
        wel = random.choice(WELCOMES).format(name=user.first_name, id=user.id)
        await client.send_message(chat_id, wel)

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

# /anime LOGO
@app.on_message(filters.me & filters.command("anime"))
async def anime_logo(client, message: Message):
    if len(message.command) < 2: return await message.edit("Use: /anime Ishika")
    name = " ".join(message.command[1:])
    await message.edit("🎨 Anime logo bana raha hu...")
    bg_url = "https://i.imgur.com/3Z3jW3Q.jpg"
    response = requests.get(bg_url)
    img = Image.open(BytesIO(response.content)).convert("RGBA")
    img = img.resize((512, 512))
    d = ImageDraw.Draw(img)
    try: font = ImageFont.truetype("arial.ttf", 50)
    except: font = ImageFont.load_default()
    d.text((256, 400), name[:12], fill=(255, 50, 150), font=font, anchor="mm", stroke_width=2, stroke_fill=(0,0,0))
    img.save("anime.png")
    await client.send_photo(message.chat.id, "anime.png", caption=f"**Anime Logo:** {name}")
    await message.delete()
    os.remove("anime.png")

# /couple LOGO
@app.on_message(filters.me & filters.command("couple"))
async def couple_logo(client, message: Message):
    if len(message.command) < 3: return await message.edit("Use: /couple boyname girlname")
    name1 = message.command[1]
    name2 = message.command[2]
    await message.edit("💑 Couple logo bana raha hu...")
    bg_url = "https://i.imgur.com/8QfZ3pL.jpg"
    response = requests.get(bg_url)
    img = Image.open(BytesIO(response.content)).convert("RGBA")
    img = img.resize((512, 512))
    d = ImageDraw.Draw(img)
    try: font = ImageFont.truetype("arial.ttf", 40)
    except: font = ImageFont.load_default()
    text = f"{name1} ❤️ {name2}"
    d.text((256, 420), text, fill=(255, 20, 147), font=font, anchor="mm", stroke_width=2, stroke_fill=(0,0,0))
    img.save("couple.png")
    await client.send_photo(message.chat.id, "couple.png", caption=f"**Couple:** {name1} + {name2} = Forever 💑")
    await message.delete()
    os.remove("couple.png")

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

# /promote
@app.on_message(filters.me & filters.command("promote"))
async def promote(client, message: Message):
    if not message.reply_to_message: return await message.edit("Reply karke use kar")
    try:
        await client.promote_chat_member(message.chat.id, message.reply_to_message.from_user.id, privileges=ChatPrivileges(can_manage_chat=True, can_delete_messages=True, can_manage_video_chats=True, can_restrict_members=True, can_promote_members=False, can_change_info=True, can_invite_users=True, can_pin_messages=True))
        await message.edit("✅ Promote kar diya")
    except: await message.edit("Tu admin nahi hai")

# /demote
@app.on_message(filters.me & filters.command("demote"))
async def demote(client, message: Message):
    if not message.reply_to_message: return await message.edit("Reply karke use kar")
    try:
        await client.promote_chat_member(message.chat.id, message.reply_to_message.from_user.id, privileges=ChatPrivileges())
        await message.edit("✅ Demote kar diya")
    except: await message.edit("Error aa gaya")

# /ban /unban /mute /unmute
@app.on_message(filters.me & filters.command("ban"))
async def ban(client, message: Message):
    if message.reply_to_message:
        await client.ban_chat_member(message.chat.id, message.reply_to_message.from_user.id)
        await message.edit("✅ Banned")

@app.on_message(filters.me & filters.command("unban"))
async def unban(client, message: Message):
    if message.reply_to_message:
        await client.unban_chat_member(message.chat.id, message.reply_to_message.from_user.id)
        await message.edit("✅ Unbanned")

@app.on_message(filters.me & filters.command("mute"))
async def mute(client, message: Message):
    if message.reply_to_message:
        await client.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id, permissions=message.chat.permissions)
        await message.edit("🔇 Muted")

@app.on_message(filters.me & filters.command("unmute"))
async def unmute(client, message: Message):
    if message.reply_to_message:
        await client.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id, permissions=message.chat.permissions)
        await message.edit("🔊 Unmuted")

# /id
@app.on_message(filters.me & filters.command("id"))
async def get_id(client, message: Message):
    await message.edit(f"Chat ID: `{message.chat.id}`\nYour ID: `{message.from_user.id}`")

# /info
@app.on_message(filters.me & filters.command("info"))
async def userinfo(client, message: Message):
    if not message.reply_to_message: return await message.edit("Reply karke use kar")
    user = message.reply_to_message.from_user
    text = f"""**User Info:**
Name: {user.first_name} {user.last_name or ""}
Username: @{user.username or "None"}
ID: `{user.id}`
Bio: {user.bio or "None"}"""
    await message.edit(text)

# /purge
@app.on_message(filters.me & filters.command("purge"))
async def purge(client, message: Message):
    if not message.reply_to_message: return await message.edit("Reply karke use kar")
    chat_id = message.chat.id; msg_id = message.reply_to_message.id
    await message.delete()
    for i in range(msg_id, message.id):
        try: await client.delete_messages(chat_id, i)
        except: pass
    await client.send_message(chat_id, "✅ Purged", disable_notification=True)

# /broadcast
@app.on_message(filters.me & filters.command("broadcast"))
async def broadcast(client, message: Message):
    if len(message.command) < 2: return await message.edit("Use: /broadcast your message")
    msg = " ".join(message.command[1:]); await message.edit("📢 Broadcast Starting...")
    sent = 0; failed = 0
    async for dialog in client.get_dialogs():
        if dialog.chat.type in ["private", "group", "supergroup"]:
            try: await client.send_message(dialog.chat.id, f"📢 Broadcast\n{msg}"); sent += 1; await asyncio.sleep(3)
            except FloodWait as e: await asyncio.sleep(e.value)
            except: failed += 1
    await message.reply(f"Broadcast Complete ✅\nSent: {sent} chats\nFailed: {failed} chats")

# /gcast
@app.on_message(filters.me & filters.command("gcast"))
async def gcast(client, message: Message):
    if len(message.command) < 2: return await message.edit("Use: /gcast your message")
    msg = " ".join(message.command[1:]); await message.edit("📢 Group Broadcast Starting...")
    sent = 0
    async for dialog in client.get_dialogs():
        if dialog.chat.type in ["group", "supergroup"]:
            try: await client.send_message(dialog.chat.id, f"📢 Group Broadcast\n{msg}"); sent += 1; await asyncio.sleep(3)
            except: pass
    await message.reply(f"Group Broadcast Complete ✅\nSent: {sent} groups")

# /dcast
@app.on_message(filters.me & filters.command("dcast"))
async def dcast(client, message: Message):
    if len(message.command) < 2: return await message.edit("Use: /dcast your message")
    msg = " ".join(message.command[1:]); await message.edit("📢 DM Broadcast Starting...")
    sent = 0
    async for dialog in client.get_dialogs():
        if dialog.chat.type == "private" and not dialog.chat.is_bot:
            try: await client.send_message(dialog.chat.id, f"📢 Message\n{msg}"); sent += 1; await asyncio.sleep(3)
            except: pass
    await message.reply(f"DM Broadcast Complete ✅\nSent: {sent} users")

print("ISHIKA USERBOT V1.2 STARTED ✅")
app.run()
