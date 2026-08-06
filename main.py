import os
import asyncio
import random
from pyrogram import Client, filters
from pyrogram.types import Message, ChatPrivileges, ChatPermissions
from pyrogram.errors import FloodWait, UserAdminInvalid
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import AudioPiped
from gtts import gTTS

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION = os.getenv("SESSION")

app = Client("KING_USERBOT", api_id=API_ID, api_hash=API_HASH, session_string=SESSION)
pytgcalls = PyTgCalls(app)

tagging = False
ROASTING = False
CURRENT_CHAT = None

# ================= VC ROAST LINES - 50 ADDED =================
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
    "{name} tu wo calculator hai jisme 2+2 ka answer bhi galat aata hai",
    "{name} teri life me charger se zyada dikkat hai",
    "{name} bhai tu wo loading screen hai jo 99% pe atak jati hai",
    "{name} tu itna slow hai ki tortoise bhi tujhe race me hara de",
    "{name} teri awaaz sunke mic bhi khud ko mute kar leta hai",
    "{name} tu wo group hai jisme sirf 'Good morning' forward aate hain",
    "{name} teri soch dekh ke ChatGPT bhi 'I cannot answer that' bol deta hai",
    "{name} bhai tu wo auto-correct hai jo har baar galat word likh deta hai",
    "{name} tu itna fake hai ki AI bhi tujhe detect kar le",
    "{name} teri baaton me itna gyaan hai jitna kachre me sona",
    "{name} tu wo notification hai jisko sab swipe karke hata dete hain",
    "{name} bhai tera confidence dekh ke antivirus bhi dar jata hai",
    "{name} tu wo link hai jo '404 Error' dikhata hai",
    "{name} teri english sunke grammar bhi suicide kar lega",
    "{name} tu itna sasta hai ki free wala bhi tujhe na le",
    "{name} bhai tu wo meme hai jo 2012 me purana ho gaya tha",
    "{name} teri shakal dekh ke mirror bhi bolta hai bhai side ho ja",
    "{name} tu wo charger hai jo 1% pe hi tut jata hai",
    "{name} teri personality dekh ke Bluetooth bhi 'Device not found' bolta hai",
    "{name} tu itna bekar hai ki dustbin bhi tujhe return kar de",
    "{name} bhai tu wo typing... hai jo kabhi message send hi nahi hota",
    "{name} tu wo ad hai jisko sab 'Skip Ad' kar dete hain",
    "{name} teri baatein sunke radio bhi frequency change kar leta hai",
    "{name} tu itna ganda hai ki filter bhi tujhe saaf nahi kar sakta",
    "{name} bhai tu wo password hai jo har baar 'Incorrect' aata hai",
    "{name} teri life dekh ke motivational quotes bhi sharma jate hain",
    "{name} tu wo teacher hai jiski class me sab sote hain",
    "{name} teri soch dekh ke AI bhi bolta hai bhai main nahi kar sakta",
    "{name} tu itna boring hai ki book bhi tujhe dekh ke band ho jati hai",
    "{name} bhai tu wo signal hai jo call ke beech me chala jata hai",
    "{name} tu wo friend hai jo sirf exam ke time yaad aata hai",
    "{name} teri baaton me itna dam hai jitna paani me aag",
    "{name} tu itna chomu hai ki google bhi tujhe search nahi karta",
    "{name} bhai tu wo emoji hai jiska koi matlab hi nahi hota",
    "{name} teri shakal dekh ke camera bhi bolta hai focus nahi ho raha",
    "{name} tu wo reply hai jo 3 din baad aata hai",
    "{name} teri personality dekh ke Instagram bhi shadow ban kar deta hai",
    "{name} tu itna slow hai ki download 1kb/s pe chalta hai",
    "{name} bhai tu wo status hai jisko koi nahi dekhta",
    "{name} tu wo error hai jiska solution stackoverflow pe bhi nahi hai",
]

async def get_chat_id(client, chat_input):
    try:
        if chat_input.startswith("@"):
            chat = await client.get_chat(chat_input)
            return chat.id
        else:
            return int(chat_input)
    except:
        return None

# ================= VC WALE COMMAND =================
@app.on_message(filters.me & filters.command("raidvc"))
async def raid_voice(client, message: Message):
    if not message.reply_to_message or not message.reply_to_message.voice:
        return await message.edit("❌ Saved Messages ki voice ko reply karke /raidvc chatid de")
    if len(message.command) < 2:
        return await message.edit("Use: <code>/raidvc -10012345678</code>")
    await message.edit("🔊 Voice VC me baja raha hu...")
    try:
        chat_id = await get_chat_id(client, message.command[1])
        if not chat_id: return await message.edit("❌ Chat ID galat hai")
        voice_file = "raid_voice.ogg"
        await client.download_media(message.reply_to_message, file_name=voice_file)
        await pytgcalls.join_group_call(chat_id, AudioPiped(voice_file))
        await asyncio.sleep(8)
        await pytgcalls.leave_group_call(chat_id)
        os.remove(voice_file)
        await message.edit("✅ Voice baja di")
    except Exception as e:
        await message.edit(f"Error: {e}")

@app.on_message(filters.me & filters.command("graidvc"))
async def graid_roast(client, message: Message):
    global ROASTING, CURRENT_CHAT
    if len(message.command) < 3:
        return await message.edit("Use: <code>/graidvc -10012345678 Name</code>")
    chat_input = message.command[1]
    name = " ".join(message.command[2:])
    ROASTING = True
    CURRENT_CHAT = await get_chat_id(client, chat_input)
    if not CURRENT_CHAT: return await message.edit("❌ Chat ID galat hai")
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
        try: await pytgcalls.leave_group_call(CURRENT_CHAT)
        except: pass

@app.on_message(filters.me & filters.command("stopgraid"))
async def stop_graid(client, message: Message):
    global ROASTING
    ROASTING = False
    try: await pytgcalls.leave_group_call(CURRENT_CHAT)
    except: pass
    await message.edit("🛑 Graid Rok di")

# ================= TAG WALE =================
@app.on_message(filters.me & filters.command("tagall"))
async def tagall(client, message: Message):
    global tagging
    if len(message.command) < 2: return await message.edit("Use: <code>/tagall msg</code>")
    tagging = True; msg = " ".join(message.command[1:]); await message.delete()
    members = [m.user async for m in client.get_chat_members(message.chat.id) if m.user and not m.user.is_bot and not m.user.is_deleted]
    count = 0
    for user in members:
        if not tagging: break
        try: await client.send_message(message.chat.id, f"[{user.first_name}](tg://user?id={user.id}) {msg}"); count += 1; await asyncio.sleep(6)
        except FloodWait as e: await asyncio.sleep(e.value + 5)
    tagging = False; await message.reply(f"Tagging Complete ✅\nTotal: {count}")

@app.on_message(filters.me & filters.command("cancel"))
async def cancel_tag(client, message: Message):
    global tagging; tagging = False; await message.edit("Tagging Cancelled ❌")

# ================= ADMIN WALE =================
@app.on_message(filters.me & filters.command("promote"))
async def promote(client, message: Message):
    if not message.reply_to_message: return await message.edit("Reply karke use kar")
    try: await client.promote_chat_member(message.chat.id, message.reply_to_message.from_user.id, privileges=ChatPrivileges(can_manage_chat=True, can_delete_messages=True, can_manage_video_chats=True, can_restrict_members=True, can_promote_members=False, can_change_info=True, can_invite_users=True, can_pin_messages=True)); await message.edit("✅ Promote kar diya 👑")
    except: await message.edit("❌ Rights nahi hai")

@app.on_message(filters.me & filters.command("demote"))
async def demote(client, message: Message):
    if not message.reply_to_message: return await message.edit("Reply karke use kar")
    try: await client.promote_chat_member(message.chat.id, message.reply_to_message.from_user.id, privileges=ChatPrivileges()); await message.edit("✅ Demote kar diya")
    except: await message.edit("❌ Error")

@app.on_message(filters.me & filters.command("ban"))
async def ban(client, message: Message):
    if message.reply_to_message: await client.ban_chat_member(message.chat.id, message.reply_to_message.from_user.id); await message.edit("✅ Banned 🔨")

@app.on_message(filters.me & filters.command("unban"))
async def unban(client, message: Message):
    if message.reply_to_message: await client.unban_chat_member(message.chat.id, message.reply_to_message.from_user.id); await message.edit("✅ Unbanned")

@app.on_message(filters.me & filters.command("mute"))
async def mute(client, message: Message):
    if message.reply_to_message: await client.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id, permissions=ChatPermissions()); await message.edit("🔇 Muted")

@app.on_message(filters.me & filters.command("unmute"))
async def unmute(client, message: Message):
    if message.reply_to_message: await client.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id, permissions=ChatPermissions(can_send_messages=True, can_send_media_messages=True)); await message.edit("🔊 Unmuted")

# ================= INFO + UTILITY =================
@app.on_message(filters.me & filters.command("id"))
async def get_id(client, message: Message):
    await message.edit(f"<b>Chat ID:</b> <code>{message.chat.id}</code>\n<b>Your ID:</b> <code>{message.from_user.id}</code>")

@app.on_message(filters.me & filters.command("info"))
async def userinfo(client, message: Message):
    if not message.reply_to_message: return await message.edit("Reply karke use kar")
    user = message.reply_to_message.from_user
    await message.edit(f"<b>Name:</b> {user.first_name}\n<b>Username:</b> @{user.username or 'None'}\n<b>ID:</b> <code>{user.id}</code>")

@app.on_message(filters.me & filters.command("purge"))
async def purge(client, message: Message):
    if not message.reply_to_message: return await message.edit("Reply karke use kar")
    await client.delete_messages(message.chat.id, list(range(message.reply_to_message.id, message.id + 1))); await message.reply("✅ Purged")

# ================= BROADCAST WALE =================
@app.on_message(filters.me & filters.command("broadcast"))
async def broadcast(client, message: Message):
    if len(message.command) < 2: return await message.edit("Use: <code>/broadcast msg</code>")
    msg = " ".join(message.command[1:]); sent = 0
    async for dialog in client.get_dialogs():
        if dialog.chat.type in ["private", "group", "supergroup"]:
            try: await client.send_message(dialog.chat.id, f"📢 <b>KARTIK KI TARAF SE</b>\n\n{msg}"); sent += 1; await asyncio.sleep(12)
            except: pass
    await message.edit(f"Broadcast Complete ✅\nSent: {sent}")

@app.on_message(filters.me & filters.command("gcast"))
async def gcast(client, message: Message):
    if len(message.command) < 2: return await message.edit("Use: <code>/gcast msg</code>")
    msg = " ".join(message.command[1:]); sent = 0
    async for dialog in client.get_dialogs():
        if dialog.chat.type in ["group", "supergroup"]:
            try: await client.send_message(dialog.chat.id, f"📢 <b>Group Broadcast</b>\n\n{msg}"); sent += 1; await asyncio.sleep(8)
            except: pass
    await message.edit(f"Gcast Complete ✅\nSent: {sent} groups")

@app.on_message(filters.me & filters.command("dcast"))
async def dcast(client, message: Message):
    if len(message.command) < 2: return await message.edit("Use: <code>/dcast msg</code>")
    msg = " ".join(message.command[1:]); sent = 0
    async for dialog in client.get_dialogs():
        if dialog.chat.type == "private" and not dialog.chat.is_bot:
            try: await client.send_message(dialog.chat.id, f"📢 <b>Message</b>\n\n{msg}"); sent += 1; await asyncio.sleep(8)
            except: pass
    await message.edit(f"Dcast Complete ✅\nSent: {sent} users")

# ================= TTS + OTHER =================
@app.on_message(filters.me & filters.command("tts"))
async def tts_cmd(client, message: Message):
    if len(message.command) < 2: return await message.edit("Use: <code>/tts text</code>")
    text = " ".join(message.command[1:]); tts = gTTS(text=text, lang='hi'); tts.save("voice.ogg")
    await client.send_voice(message.chat.id, "voice.ogg"); os.remove("voice.ogg"); await message.delete()

@app.on_message(filters.me & filters.command("ping"))
async def ping(client, message: Message):
    await message.edit("🏓 Pong! Bot zinda hai 👑")

@app.on_message(filters.me & filters.command("help"))
async def help(client, message: Message):
    text = """🔥 <b>KING USERBOT + VC RAID</b> 🔥
<b>VC:</b> /raidvc /graidvc /stopgraid
<b>Tag:</b> /tagall /cancel
<b>Admin:</b> /promote /demote /ban /unban /mute /unmute
<b>Info:</b> /id /info /purge
<b>Broadcast:</b> /broadcast /gcast /dcast
<b>Other:</b> /tts /ping /help"""
    await message.edit(text)

async def main():
    await pytgcalls.start()
    await app.start()
    print("👑 KING USERBOT STARTED 👑")
    await app.idle()

if __name__ == "__main__":
    app.run(main())
