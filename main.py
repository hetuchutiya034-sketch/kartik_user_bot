from pyrogram import Client, filters
from pyrogram.types import *
from pyrogram.errors import FloodWait
import asyncio, os, random

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION = os.getenv("SESSION")

app = Client("ishikauserbot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION)

# ===== GLOBAL BUTTONS =====
def buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🚀 Deploy", callback_data="deploy")],
        [InlineKeyboardButton("✅ Available", callback_data="available")],
        [InlineKeyboardButton("📢 Updates", url="https://t.me/")],
        [InlineKeyboardButton("💬 Owner", url="https://t.me/")]
    ])

# ===== CALLBACK =====
@app.on_callback_query()
async def cb(client, q):
    if q.data == "deploy":
        await q.answer("🚀 Bot already deployed!", show_alert=True)
    elif q.data == "available":
        await q.answer("✅ All systems working!", show_alert=True)

# ===== BASIC =====
@app.on_message(filters.me & filters.command("ping"))
async def ping(_, m):
    await m.edit("🏓 Pong!", reply_markup=buttons())

@app.on_message(filters.me & filters.command("help"))
async def help(_, m):
    await m.edit("""
🔥 KING USERBOT 🔥

.cat .rose .hacker .error .fuck .butterfly  
.yourmom .myson .love  

.clone .back  
.tagall .allban .stop  

.aanysnap = auto reply  
""", reply_markup=buttons())

# ===== KING COMMANDS =====
@app.on_message(filters.me & filters.command("cat"))
async def cat(_, m): await m.edit("🐱 Meow 😺", reply_markup=buttons())

@app.on_message(filters.me & filters.command("rose"))
async def rose(_, m): await m.edit("🌹 Rose ❤️", reply_markup=buttons())

@app.on_message(filters.me & filters.command("hacker"))
async def hacker(_, m): await m.edit("💻 Hacking...\nAccess Granted ✅", reply_markup=buttons())

@app.on_message(filters.me & filters.command("error"))
async def error(_, m): await m.edit("⚠️ System Crash!", reply_markup=buttons())

@app.on_message(filters.me & filters.command("fuck"))
async def fuck(_, m): await m.edit("🖕", reply_markup=buttons())

@app.on_message(filters.me & filters.command("butterfly"))
async def butterfly(_, m): await m.edit("🦋 Butterfly Mode", reply_markup=buttons())

@app.on_message(filters.me & filters.command("yourmom"))
async def yourmom(_, m): await m.edit("😂 Mom roast activated", reply_markup=buttons())

@app.on_message(filters.me & filters.command("myson"))
async def myson(_, m): await m.edit("👨‍👦 Me & My Son", reply_markup=buttons())

@app.on_message(filters.me & filters.command("love"))
async def love(_, m): await m.edit("❤️ Love 💫", reply_markup=buttons())

# ===== AUTO REPLY =====
auto_reply = False

@app.on_message(filters.me & filters.command("aanysnap"))
async def auto(_, m):
    global auto_reply
    auto_reply = not auto_reply
    await m.edit(f"Auto Reply {'ON' if auto_reply else 'OFF'}", reply_markup=buttons())

@app.on_message(filters.text & ~filters.me)
async def reply_all(client, m):
    if auto_reply:
        await m.reply("⚡ Auto Reply Active", reply_markup=buttons())

# ===== CLONE =====
backup = {}

@app.on_message(filters.me & filters.command("clone"))
async def clone(client, m):
    user = m.reply_to_message.from_user
    me = await client.get_me()
    backup["name"] = me.first_name
    await client.update_profile(first_name=user.first_name)
    await m.edit("👥 Cloned", reply_markup=buttons())

@app.on_message(filters.me & filters.command("back"))
async def back(client, m):
    if backup:
        await client.update_profile(first_name=backup["name"])
        await m.edit("🔄 Restored", reply_markup=buttons())

# ===== TAG ALL =====
running = True

@app.on_message(filters.me & filters.command("tagall"))
async def tagall(client, m):
    global running
    running = True
    await m.delete()

    async for u in client.get_chat_members(m.chat.id):
        if not running: break
        try:
            await client.send_message(m.chat.id, f"[{u.user.first_name}](tg://user?id={u.user.id}) hi")
            await asyncio.sleep(2)
        except:
            pass

@app.on_message(filters.me & filters.command("stop"))
async def stop(_, m):
    global running
    running = False
    await m.edit("🛑 Stopped", reply_markup=buttons())

# ===== ALL BAN (SAFE) =====
@app.on_message(filters.me & filters.command("allban"))
async def allban(client, m):
    await m.edit("🔨 Banning...")
    async for u in client.get_chat_members(m.chat.id):
        try:
            await client.ban_chat_member(m.chat.id, u.user.id)
            await asyncio.sleep(0.5)
        except:
            pass

print("🔥 USERBOT STARTED 🔥")
app.run()
