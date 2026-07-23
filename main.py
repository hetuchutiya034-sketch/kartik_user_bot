from pyrogram import Client, filters
from pyrogram.types import Message, ChatPrivileges
from pyrogram.errors import FloodWait, UserAdminInvalid
import asyncio
import os
from gtts import gTTS # TTS ke liye

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION = os.getenv("SESSION")

app = Client("userbot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION)

tagging = False

# /ping
@app.on_message(filters.me & filters.command("ping"))
async def ping(client, message: Message):
    await message.edit("🏓 Pong! Bot zinda hai")

# /help - TTS ADD KIYA
@app.on_message(filters.me & filters.command("help"))
async def help(client, message: Message):
    text = """**🔥 Ishika Userbot Commands 🔥**

**Tag wale:**
`/tagall message` - Ek ek karke sabko tag
`/cancel` - Tagging rok de

**Admin wale:**
`/promote` - Reply karke admin bana
`/demote` - Reply karke admin hata  
`/ban` - Reply karke ban
`/unban` - Reply karke unban
`/mute` - Reply karke mute
`/unmute` - Reply karke unmute

**Info wale:**
`/id` - Chat aur User ID
`/info` - Reply karke user info
`/purge` - Reply se niche sab delete

**Broadcast wale:**
`/broadcast msg` - Sabko DM + Group
`/gcast msg` - Sirf Groups me
`/dcast msg` - Sirf DM me

**TTS wala:**
`/tts text` - Text ko voice me convert

Made with 💜"""
    await message.edit(text)

# /tts NEW COMMAND
@app.on_message(filters.me & filters.command("tts"))
async def tts_cmd(client, message: Message):
    if len(message.command) < 2:
        return await message.edit("Use: `/tts hello kaise ho`")
    
    text = " ".join(message.command[1:])
    await message.edit("🎤 **Voice bana raha hu...**")
    
    try:
        tts = gTTS(text=text, lang='hi') # 'hi' = Hindi, 'en' = English
        tts.save("voice.ogg")
        
        await client.send_voice(message.chat.id, "voice.ogg", caption=f"**TTS:** {text}")
        await message.delete()
        os.remove("voice.ogg") # file delete
        
    except Exception as e:
        await message.edit(f"Error: `{e}`")

# /tagall - ek karke
@app.on_message(filters.me & filters.command("tagall"))
async def tagall(client, message: Message):
    global tagging
    if len(message.command) < 2:
        await message.edit("Use: `/tagall message`")
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
            await message.reply("**Tagging Stopped** ❌")
            break
            
        try:
            await client.send_message(
                message.chat.id, 
                f"[{user.first_name}](tg://user?id={user.id}) {msg}"
            )
            count += 1
            await asyncio.sleep(5)
            
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except:
            pass
    
    if tagging:
        await message.reply(f"**Tagging Complete** ✅\nTotal: `{count}` members")
    tagging = False

# /cancel
@app.on_message(filters.me & filters.command("cancel"))
async def cancel_tag(client, message: Message):
    global tagging
    tagging = False
    await message.edit("**Tagging Cancelled**")

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

# /demote
@app.on_message(filters.me & filters.command("demote"))
async def demote(client, message: Message):
    if not message.reply_to_message:
        return await message.edit("Reply karke use kar")
    try:
        await client.promote_chat_member(message.chat.id, message.reply_to_message.from_user.id, privileges=ChatPrivileges())
        await message.edit("✅ Demote kar diya")
    except:
        await message.edit("Error aa gaya")

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
    await message.edit(f"**Chat ID:** `{message.chat.id}`\n**Your ID:** `{message.from_user.id}`")

# /info
@app.on_message(filters.me & filters.command("info"))
async def userinfo(client, message: Message):
    if not message.reply_to_message:
        return await message.edit("Reply karke use kar")
    user = message.reply_to_message.from_user
    text = f"""**User Info:**
**Name:** {user.first_name} {user.last_name or ""}
**Username:** @{user.username or "None"}
**ID:** `{user.id}`
**Bio:** {user.bio or "None"}"""
    await message.edit(text)

# /purge
@app.on_message(filters.me & filters.command("purge"))
async def purge(client, message: Message):
    if not message.reply_to_message:
        return await message.edit("Reply karke use kar")
    chat_id = message.chat.id
    msg_id = message.reply_to_message.id
    await message.delete()
    for i in range(msg_id, message.id):
        try:
            await client.delete_messages(chat_id, i)
        except:
            pass
    await client.send_message(chat_id, "✅ Purged", disable_notification=True)

# /broadcast
@app.on_message(filters.me & filters.command("broadcast"))
async def broadcast(client, message: Message):
    if len(message.command) < 2:
        return await message.edit("Use: `/broadcast your message`")
    
    msg = " ".join(message.command[1:])
    await message.edit("📢 **Broadcast Starting...**")
    
    sent = 0
    failed = 0
    async for dialog in client.get_dialogs():
        if dialog.chat.type in ["private", "group", "supergroup"]:
            try:
                await client.send_message(dialog.chat.id, f"📢 **Broadcast**\n\n{msg}")
                sent += 1
                await asyncio.sleep(3)
            except FloodWait as e:
                await asyncio.sleep(e.value)
            except:
                failed += 1
    
    await message.reply(f"**Broadcast Complete** ✅\n**Sent:** `{sent}` chats\n**Failed:** `{failed}` chats")

# /gcast
@app.on_message(filters.me & filters.command("gcast"))
async def gcast(client, message: Message):
    if len(message.command) < 2:
        return await message.edit("Use: `/gcast your message`")
    
    msg = " ".join(message.command[1:])
    await message.edit("📢 **Group Broadcast Starting...**")
    
    sent = 0
    async for dialog in client.get_dialogs():
        if dialog.chat.type in ["group", "supergroup"]:
            try:
                await client.send_message(dialog.chat.id, f"📢 **Group Broadcast**\n\n{msg}")
                sent += 1
                await asyncio.sleep(3)
            except:
                pass
    
    await message.reply(f"**Group Broadcast Complete** ✅\n**Sent:** `{sent}` groups")

# /dcast
@app.on_message(filters.me & filters.command("dcast"))
async def dcast(client, message: Message):
    if len(message.command) < 2:
        return await message.edit("Use: `/dcast your message`")
    
    msg = " ".join(message.command[1:])
    await message.edit("📢 **DM Broadcast Starting...**")
    
    sent = 0
    async for dialog in client.get_dialogs():
        if dialog.chat.type == "private" and not dialog.chat.is_bot:
            try:
                await client.send_message(dialog.chat.id, f"📢 **Message**\n\n{msg}")
                sent += 1
                await asyncio.sleep(3)
            except:
                pass
    
    await message.reply(f"**DM Broadcast Complete** ✅\n**Sent:** `{sent}` users")

print("Userbot Started!")
app.run()
