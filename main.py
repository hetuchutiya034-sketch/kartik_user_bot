import os
import asyncio
import random
from pyrogram import Client, filters
from pyrogram.types import Message, ChatPrivileges, ChatPermissions
from pyrogram.errors import FloodWait, UserAdminInvalid
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped
from gtts import gTTS

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION = os.getenv("SESSION")

app = Client("KING_USERBOT", api_id=API_ID, api_hash=API_HASH, session_string=SESSION)
pytgcalls = PyTgCalls(app)

tagging = False
ROASTING = False
CURRENT_CHAT = None

# ================= VC ROAST LINES =================
# Yaha 1000 line tak add kar de. {name} me naam aa jayega
ROAST_LINES = [
    "{name} bhai teri shakal dekh ke Google bhi 'No results found' dikhata hai",
    "{name} tu itna useless hai ki power bank bhi tujhe charge karne se mana kar de",
    "{name} teri baatein sun ke to airplane bhi flight mode on kar leta hai",
    "{name} beta tu wo software update hai jo aate hi phone hang kar deta hai",
    "{name} tujhe dekh ke Photoshop bhi bolta hai bhai tu khud ko theek kar",
    "{name} teri soch itni choti hai ki 2GB RAM bhi full ho jati hai",
    "{name} tu wo message hai jo 'This message was deleted' ho jata hai",
    "{name} bhai tu school ki wo assembly hai jisme sabko neend aati hai",
    "{name} teri personality dekh ke WiFi bolta hai network not found",
    "{name} tu itna boring hai ki Netflix bhi tujhe 'Are you still watching' pooche",
    # yaha aur 990 line add kar 
]

async def get_chat_id(client, chat_input):
    if chat_input.startswith("@"):
        chat = await client.get_chat(chat_input)
        return chat.id
    else:
        return int(chat_input)

# ================= VC WALE COMMAND =================

@app.on_message(filters.me & filters.command("raidvc"))
async def raid_voice(client, message: Message):
    if not message.reply_to_message or not message.reply_to_message.voice:
        return await message.edit("❌ Saved Messages ki kisi voice note ko reply karke /raidvc chatid ya @username de")

    if len(message.command) < 2:
        return await message.edit("Use: <code>/raidvc -10012345678</code>")

    await message.edit("🔊 Voice VC me baja raha hu...")
    try:
        chat_id = await get_chat_id(client, message.command[1])
        voice_file = "raid_voice.ogg"
        await client.download_media(message.reply_to_message, file_name=voice_file)
        await pytgcalls.join_group_call(chat_id, AudioPiped(voice_file))
        await asyncio.sleep(3)
        await pytgcalls.leave_group_call(chat_id)
        os.remove(voice_file)
        await message.edit("✅ Voice baja di")
    except Exception as e:
        await message.edit(f"Error: {e}")

@app.on_message(filters.me & filters.command("graidvc"))
async def graid_roast(client, message: Message):
    global ROASTING, CURRENT_CHAT
    if len(message.command) < 3:
        return await message.edit("Use: <code>/graidvc -10012345678 Name</code>\n ya \n<code>/graidvc @username Name</code>")

    chat_input = message.command[1]
    name = " ".join(message.command[2:])
    ROASTING = True
    try:
        CURRENT_CHAT = await get_chat_id(client, chat_input)
    except Exception as e:
        return await message.edit(f"Chat galat hai: {e}")

    await message.edit(f"🔥 {name} ki Graid Shuru... /stopgraid se rokna")
    try:
        await pytgcalls.join_group_call(CURRENT_CHAT, AudioPiped("silence.mp3"))
        for line in ROAST_LINES:
            if not ROASTING: break
            roast_text = line.format(name=name)
            tts_file = f"temp_{random.randint(1,99999)}.ogg"
            tts = gTTS(text=roast_text, lang='hi')
            tts.save(tts_file)
            await pytgcalls.change_stream(CURRENT_CHAT, AudioPiped(tts_file))
            await asyncio.sleep(4)
            os.remove(tts_file)
        await pytgcalls.leave_group_call(CURRENT_CHAT)
        await message.reply(f"✅ {name} ki Graid Complete")
        ROASTING = False
    except Exception as e:
        await message.edit(f"Error: {e}")
        ROASTING = False

@app.on_message(filters.me & filters.command("stopgraid"))
async def stop_graid(client, message: Message):
    global ROASTING
    ROASTING = False
    try: await pytgcalls.leave_group_call(CURRENT_CHAT)
    except: pass
    await message.edit("🛑 Graid Rok di")

# ================= PURANE USERBOT COMMAND =================

@app.on_message(filters.me & filters.command("ping"))
async def ping(client, message: Message):
    await message.edit("🏓 Pong! Bot zinda hai 👑")

@app.on_message(filters.me & filters.command("help"))
async def help(client, message: Message):
    text = """🔥 <b>KING USERBOT + VC RAID</b> 🔥

<b>VC Wale:</b>
<code>/raidvc chatid</code> - Reply voice ko VC me bajao
<code>/graidvc chatid Name</code> - Naam leke 100 roast
<code>/stopgraid</code> - Rok do

<b>Tag wale:</b>
<code>/tagall message</code> - Ek ek karke sabko tag
<code>/cancel</code> - Tagging rok de

<b>Admin wale:</b>
<code>/promote</code> <code>/demote</code> <code>/ban</code> <code>/unban</code> <code>/mute</code> <code>/unmute</code>

<b>Info wale:</b>
<code>/id</code> <code>/info</code> <code>/purge</code>

<b>Broadcast wale:</b>
<code>/broadcast msg</code> <code>/gcast msg</code> <code>/dcast msg</code>

<b>TTS wala:</b>
<code>/tts text</code> - Text ko voice me convert
"""
    await message.edit(text)

@app.on_message(filters.me & filters.command("tts"))
async def tts_cmd(client, message: Message):
    if len(message.command) < 2:
        return await message.edit("Use: <code>/tts hello kaise ho</code>")
    text = " ".join(message.command[1:])
    await message.edit("🎤 Voice bana raha hu...")
    file_name = "voice.ogg"
    try:
        tts = gTTS(text=text, lang='hi')
        tts.save(file_name)
        await client.send_voice(message.chat.id, file_name, caption=f"TTS: {text}")
        await message.delete()
    except Exception as e:
        await message.edit(f"Error: <code>{e}</code>")
    finally:
        if os.path.exists(file_name):
            os.remove(file_name)

@app.on_message(filters.me & filters.command("tagall"))
async def tagall(client, message: Message):
    global tagging
    if len(message.command) < 2:
        await message.edit("Use: <code>/tagall message</code>")
        return
    tagging = True
    msg = " ".join(message.command[1:])
    await message.delete()
    members = [m.user async for m in client.get_chat_members(message.chat.id) if m.user and not m.user.is_bot and not m.user.is_deleted]
    count = 0
    for user in members:
        if not tagging:
            await message.reply("Tagging Stopped ❌")
            break
        try:
            await client.send_message(message.chat.id, f"[{user.first_name}](tg://user?id={user.id}) {msg}")
            count += 1
            await asyncio.sleep(8)
        except FloodWait as e:
            await asyncio.sleep(e.value + 5)
        except:
            pass
    if tagging:
        await message.reply(f"Tagging Complete ✅\nTotal: {count} members")
    tagging = False

@app.on_message(filters.me & filters.command("cancel"))
async def cancel_tag(client, message: Message):
    global tagging; tagging = False; await message.edit("Tagging Cancelled ❌")

@app.on_message(filters.me & filters.command("promote"))
async def promote(client, message: Message):
    if not message.reply_to_message: return await message.edit("Reply karke use kar")
    try:
        await client.promote_chat_member(message.chat.id, message.reply_to_message.from_user.id, privileges=ChatPrivileges(can_manage_chat=True, can_delete_messages=True, can_manage_video_chats=True, can_restrict_members=True, can_promote_members=False, can_change_info=True, can_invite_users=True, can_pin_messages=True))
        await message.edit("✅ Promote kar diya")
    except UserAdminInvalid: await message.edit("Tu admin nahi hai ya rights nahi hai")
    except Exception as e: await message.edit(f"Error: {e}")

@app.on_message(filters.me & filters.command("demote"))
async def demote(client, message: Message):
    if not message.reply_to_message: return await message.edit("Reply karke use kar")
    try: await client.promote_chat_member(message.chat.id, message.reply_to_message.from_user.id, privileges=ChatPrivileges()); await message.edit("✅ Demote kar diya")
    except Exception as e: await message.edit(f"Error: {e}")

@app.on_message(filters.me & filters.command("ban"))
async def ban(client, message: Message):
    if message.reply_to_message:
        try: await client.ban_chat_member(message.chat.id, message.reply_to_message.from_user.id); await message.edit("✅ Banned")
        except Exception as e: await message.edit(f"Error: {e}")

@app.on_message(filters.me & filters.command("unban"))
async def unban(client, message: Message):
    if message.reply_to_message:
        try: await client.unban_chat_member(message.chat.id, message.reply_to_message.from_user.id); await message.edit("✅ Unbanned")
        except Exception as e: await message.edit(f"Error: {e}")

@app.on_message(filters.me & filters.command("mute"))
async def mute(client, message: Message):
    if message.reply_to_message:
        try: await client.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id, permissions=ChatPermissions()); await message.edit("🔇 Muted")
        except Exception as e: await message.edit(f"Error: {e}")

@app.on_message(filters.me & filters.command("unmute"))
async def unmute(client, message: Message):
    if message.reply_to_message:
        try: await client.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id, permissions=ChatPermissions(can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True, can_add_web_page_previews=True)); await message.edit("🔊 Unmuted")
        except Exception as e: await message.edit(f"Error: {e}")

@app.on_message(filters.me & filters.command("id"))
async def get_id(client, message: Message):
    await message.edit(f"<b>Chat ID:</b> <code>{message.chat.id}</code>\n<b>Your ID:</b> <code>{message.from_user.id}</code>")

@app.on_message(filters.me & filters.command("info"))
async def userinfo(client, message: Message):
    if not message.reply_to_message: return await message.edit("Reply karke use kar")
    user = message.reply_to_message.from_user
    text = f"""<b>User Info:</b>\n<b>Name:</b> {user.first_name} {user.last_name or ""}\n<b>Username:</b> @{user.username or "None"}\n<b>ID:</b> <code>{user.id}</code>\n<b>Bio:</b> {user.bio or "None"}"""
    await message.edit(text)

@app.on_message(filters.me & filters.command("purge"))
async def purge(client, message: Message):
    if not message.reply_to_message: return await message.edit("Reply karke use kar")
    chat_id = message.chat.id; msg_id = message.reply_to_message.id; await message.delete()
    try: await client.delete_messages(chat_id, list(range(msg_id, message.id + 1))); await client.send_message(chat_id, "✅ Purged", disable_notification=True)
    except Exception as e: await client.send_message(chat_id, f"Error: {e}")

@app.on_message(filters.me & filters.command("broadcast"))
async def broadcast(client, message: Message):
    if len(message.command) < 2: return await message.edit("Use: <code>/broadcast your message</code>")
    msg = " ".join(message.command[1:]); status = await message.edit("📢 Broadcast Starting...")
    sent = 0; failed = 0; total = 0
    async for dialog in client.get_dialogs():
        total += 1
        if total % 10 == 0: await status.edit(f"📢 Scanning... {total} chats checked\nSent: {sent}")
        if dialog.chat.type in ["private", "group", "supergroup"]:
            try: await client.send_message(dialog.chat.id, f"📢 <b>KARTIK KI TARAF SE</b> 🌹❤️\n\n{msg}"); sent += 1; await asyncio.sleep(12)
            except FloodWait as e: await asyncio.sleep(e.value + 15)
            except: failed += 1
    await status.edit(f"Broadcast Complete ✅\n<b>Total Scanned:</b> {total}\n<b>Sent:</b> {sent}\n<b>Failed:</b> {failed}")

@app.on_message(filters.me & filters.command("gcast"))
async def gcast(client, message: Message):
    if len(message.command) < 2: return await message.edit("Use: <code>/gcast your message</code>")
    msg = " ".join(message.command[1:]); status = await message.edit("📢 Group Broadcast Starting...")
    sent = 0
    async for dialog in client.get_dialogs():
        if dialog.chat.type in ["group", "supergroup"]:
            try: await client.send_message(dialog.chat.id, f"📢 <b>Group Broadcast</b>\n\n{msg}"); sent += 1; await asyncio.sleep(8)
            except FloodWait as e: await asyncio.sleep(e.value + 10)
            except: pass
    await status.edit(f"Group Broadcast Complete ✅\n<b>Sent:</b> {sent} groups")

@app.on_message(filters.me & filters.command("dcast"))
async def dcast(client, message: Message):
    if len(message.command) < 2: return await message.edit("Use: <code>/dcast your message</code>")
    msg = " ".join(message.command[1:]); status = await message.edit("📢 DM Broadcast Starting...")
    sent = 0
    async for dialog in client.get_dialogs():
        if dialog.chat.type == "private" and not dialog.chat.is_bot:
            try: await client.send_message(dialog.chat.id, f"📢 <b>Message</b>\n\n{msg}"); sent += 1; await asyncio.sleep(8)
            except FloodWait as e: await asyncio.sleep(e.value + 10)
            except: pass
    await status.edit(f"DM Broadcast Complete ✅\n<b>Sent:</b> {sent} users")

print("👑 KING USERBOT STARTED 👑")
asyncio.run(pytgcalls.start())
app.run()
