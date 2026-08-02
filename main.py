import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, ChatPrivileges, ChatPermissions
from pyrogram.errors import FloodWait, UserAdminInvalid
from gtts import gTTS # TTS ke liye

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION = os.getenv("SESSION")

app = Client("KING_USERBOT", api_id=API_ID, api_hash=API_HASH, session_string=SESSION)

tagging = False

# /ping
@app.on_message(filters.me & filters.command("ping"))
async def ping(client, message: Message):
    await message.edit("🏓 Pong! Bot zinda hai 👑")

# /help - TTS ADD KIYA
@app.on_message(filters.me & filters.command("help"))
async def help(client, message: Message):
    text = """🔥 <b>KING Userbot Commands</b> 🔥

<b>Tag wale:</b>
<code>/tagall message</code> - Ek ek karke sabko tag
<code>/cancel</code> - Tagging rok de

<b>Admin wale:</b>
<code>/promote</code> - Reply karke admin bana
<code>/demote</code> - Reply karke admin hata  
<code>/ban</code> - Reply karke ban
<code>/unban</code> - Reply karke unban
<code>/mute</code> - Reply karke mute
<code>/unmute</code> - Reply karke unmute

<b>Info wale:</b>
<code>/id</code> - Chat aur User ID
<code>/info</code> - Reply karke user info
<code>/purge</code> - Reply se niche sab delete

<b>Broadcast wale:</b>
<code>/broadcast msg</code> - Sabko DM + Group
<code>/gcast msg</code> - Sirf Groups me
<code>/dcast msg</code> - Sirf DM me

<b>TTS wala:</b>
<code>/tts text</code> - Text ko voice me convert

<b>Made with 💜 by KING</b>"""
    await message.edit(text)

# /tts NEW COMMAND - SAFE
@app.on_message(filters.me & filters.command("tts"))
async def tts_cmd(client, message: Message):
    if len(message.command) < 2:
        return await message.edit("Use: <code>/tts hello kaise ho</code>")
    
    text = " ".join(message.command[1:])
    await message.edit("🎤 Voice bana raha hu...")
    
    file_name = "voice.ogg"
    try:
        tts = gTTS(text=text, lang='hi') # 'hi' = Hindi, 'en' = English
        tts.save(file_name)
        await client.send_voice(message.chat.id, file_name, caption=f"TTS: {text}")
        await message.delete()
    except Exception as e:
        await message.edit(f"Error: <code>{e}</code>")
    finally:
        if os.path.exists(file_name):
            os.remove(file_name) # pakka delete

# /tagall - ek karke - SAFE SPEED
@app.on_message(filters.me & filters.command("tagall"))
async def tagall(client, message: Message):
    global tagging
    if len(message.command) < 2:
        await message.edit("Use: <code>/tagall message</code>")
        return
    
    tagging = True
    msg = " ".join(message.command[1:])
    await message.delete()
    
    members = []
    async for member in client.get_chat_members(message.chat.id):
        if member.user and not member.user.is_bot and not member.user.is_deleted:
            members.append(member.user)
    
    count = 0
    for user in members:
        if not tagging: 
            await message.reply("Tagging Stopped ❌")
            break
            
        try:
            await client.send_message(
                message.chat.id, 
                f"[{user.first_name}](tg://user?id={user.id}) {msg}"
            )
            count += 1
            await asyncio.sleep(8) # 8 sec rakha ban se bachne ke liye
            
        except FloodWait as e:
            await asyncio.sleep(e.value + 5)
        except:
            pass
    
    if tagging:
        await message.reply(f"Tagging Complete ✅\nTotal: {count} members")
    tagging = False

# /cancel
@app.on_message(filters.me & filters.command("cancel"))
async def cancel_tag(client, message: Message):
    global tagging
    tagging = False
    await message.edit("Tagging Cancelled ❌")

# /promote
@app.on_message(filters.me & filters.command("promote"))
async def promote(client, message: Message):
    if not message.reply_to_message:
        return await message.edit("Reply karke use kar")
    try:
        await client.promote_chat_member(
            message.chat.id, message.reply_to_message.from_user.id,
            privileges=ChatPrivileges(can_manage_chat=True, can_delete_messages=True, can_manage_video_chats=True, can_restrict_members=True, can_promote_members=False, can_change_info=True, can_invite_users=True, can_pin_messages=True)
        )
        await message.edit("✅ Promote kar diya")
    except UserAdminInvalid:
        await message.edit("Tu admin nahi hai ya rights nahi hai")
    except Exception as e:
        await message.edit(f"Error: {e}")

# /demote
@app.on_message(filters.me & filters.command("demote"))
async def demote(client, message: Message):
    if not message.reply_to_message:
        return await message.edit("Reply karke use kar")
    try:
        await client.promote_chat_member(message.chat.id, message.reply_to_message.from_user.id, privileges=ChatPrivileges())
        await message.edit("✅ Demote kar diya")
    except Exception as e:
        await message.edit(f"Error: {e}")

# /ban /unban
@app.on_message(filters.me & filters.command("ban"))
async def ban(client, message: Message):
    if message.reply_to_message:
        try:
            await client.ban_chat_member(message.chat.id, message.reply_to_message.from_user.id)
            await message.edit("✅ Banned")
        except Exception as e:
            await message.edit(f"Error: {e}")
        
@app.on_message(filters.me & filters.command("unban"))
async def unban(client, message: Message):
    if message.reply_to_message:
        try:
            await client.unban_chat_member(message.chat.id, message.reply_to_message.from_user.id)
            await message.edit("✅ Unbanned")
        except Exception as e:
            await message.edit(f"Error: {e}")

# /mute /unmute - FIXED
@app.on_message(filters.me & filters.command("mute"))
async def mute(client, message: Message):
    if message.reply_to_message:
        try:
            await client.restrict_chat_member(
                message.chat.id, 
                message.reply_to_message.from_user.id,
                permissions=ChatPermissions() # sab band
            )
            await message.edit("🔇 Muted")
        except Exception as e:
            await message.edit(f"Error: {e}")

@app.on_message(filters.me & filters.command("unmute"))
async def unmute(client, message: Message):
    if message.reply_to_message:
        try:
            await client.restrict_chat_member(
                message.chat.id, 
                message.reply_to_message.from_user.id,
                permissions=ChatPermissions(
                    can_send_messages=True,
                    can_send_media_messages=True,
                    can_send_other_messages=True,
                    can_add_web_page_previews=True
                )
            )
            await message.edit("🔊 Unmuted")
        except Exception as e:
            await message.edit(f"Error: {e}")

# /id
@app.on_message(filters.me & filters.command("id"))
async def get_id(client, message: Message):
    await message.edit(f"<b>Chat ID:</b> <code>{message.chat.id}</code>\n<b>Your ID:</b> <code>{message.from_user.id}</code>")

# /info
@app.on_message(filters.me & filters.command("info"))
async def userinfo(client, message: Message):
    if not message.reply_to_message:
        return await message.edit("Reply karke use kar")
    user = message.reply_to_message.from_user
    text = f"""<b>User Info:</b>
<b>Name:</b> {user.first_name} {user.last_name or ""}
<b>Username:</b> @{user.username or "None"}
<b>ID:</b> <code>{user.id}</code>
<b>Bio:</b> {user.bio or "None"}"""
    await message.edit(text)

# /purge - FIXED
@app.on_message(filters.me & filters.command("purge"))
async def purge(client, message: Message):
    if not message.reply_to_message:
        return await message.edit("Reply karke use kar")
    chat_id = message.chat.id
    msg_id = message.reply_to_message.id
    await message.delete()
    try:
        await client.delete_messages(chat_id, list(range(msg_id, message.id + 1)))
        await client.send_message(chat_id, "✅ Purged", disable_notification=True)
    except Exception as e:
        await client.send_message(chat_id, f"Error: {e}")

# /broadcast - FIXED VERSION
@app.on_message(filters.me & filters.command("broadcast"))
async def broadcast(client, message: Message):
    if len(message.command) < 2:
        return await message.edit("Use: <code>/broadcast your message</code>")
    
    msg = " ".join(message.command[1:])
    status = await message.edit("📢 Broadcast Starting... 0 chats scanned")
    
    sent = 0
    failed = 0
    total = 0
    
    async for dialog in client.get_dialogs():
        total += 1
        if total % 10 == 0: # har 10 chat baad update
            await status.edit(f"📢 Scanning... {total} chats checked\nSent: {sent}")
            
        if dialog.chat.type in ["private", "group", "supergroup"]:
            try:
                await client.send_message(dialog.chat.id, f"📢 <b>KARTIK KI TARAF SE</b> 🌹❤️\n\n{msg}")
                sent += 1
                await asyncio.sleep(12) # 12 sec kar diya safety ke liye
            except FloodWait as e:
                await asyncio.sleep(e.value + 15)
            except:
                failed += 1
    
    await status.edit(f"Broadcast Complete ✅\n<b>Total Scanned:</b> {total}\n<b>Sent:</b> {sent}\n<b>Failed:</b> {failed}")

# /gcast - SAFE
@app.on_message(filters.me & filters.command("gcast"))
async def gcast(client, message: Message):
    if len(message.command) < 2:
        return await message.edit("Use: <code>/gcast your message</code>")
    
    msg = " ".join(message.command[1:])
    status = await message.edit("📢 Group Broadcast Starting...")
    
    sent = 0
    async for dialog in client.get_dialogs():
        if dialog.chat.type in ["group", "supergroup"]:
            try:
                await client.send_message(dialog.chat.id, f"📢 <b>Group Broadcast</b>\n\n{msg}")
                sent += 1
                await asyncio.sleep(8)
            except FloodWait as e:
                await asyncio.sleep(e.value + 10)
            except:
                pass
    
    await status.edit(f"Group Broadcast Complete ✅\n<b>Sent:</b> {sent} groups")

# /dcast - SAFE
@app.on_message(filters.me & filters.command("dcast"))
async def dcast(client, message: Message):
    if len(message.command) < 2:
        return await message.edit("Use: <code>/dcast your message</code>")
    
    msg = " ".join(message.command[1:])
    status = await message.edit("📢 DM Broadcast Starting...")
    
    sent = 0
    async for dialog in client.get_dialogs():
        if dialog.chat.type == "private" and not dialog.chat.is_bot:
            try:
                await client.send_message(dialog.chat.id, f"📢 <b>Message</b>\n\n{msg}")
                sent += 1
                await asyncio.sleep(8)
            except FloodWait as e:
                await asyncio.sleep(e.value + 10)
            except:
                pass
    
    await status.edit(f"DM Broadcast Complete ✅\n<b>Sent:</b> {sent} users")

print("👑 KING USERBOT STARTED 👑")
app.run()
