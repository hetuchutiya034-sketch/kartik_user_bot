import os
import random
import sqlite3
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from flask import Flask
from threading import Thread
from pyrogram.enums import ChatAction

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION = os.environ.get("SESSION")
OWNER_ID = int(os.environ.get("OWNER_ID", 0))

app = Client(name="kartikuserbot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION)
app.set_parse_mode("html")
flask_app = Flask(__name__)

# ============= DATABASE =============
conn = sqlite3.connect('memory.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS memory (question TEXT, answer TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS groups (chat_id INTEGER)')
c.execute('CREATE TABLE IF NOT EXISTS dms (user_id INTEGER)')
conn.commit()

ai_groups = set()
ai_dms = set()
afk_status = False
afk_reason = "King busy hai 👑"

def remember(q, a):
    c.execute("INSERT INTO memory VALUES (?,?)", (q.lower(), a))
    conn.commit()

def recall(q):
    c.execute("SELECT answer FROM memory WHERE question LIKE?", ('%'+q.lower()+'%',))
    data = c.fetchall()
    return random.choice(data)[0] if data else None

# ============= SHAYARI LISTS FULL =============
DARD_SHAYARI = [
    "Dil tod ke wo muskura rahe hai,\nHum unhe yaad karke ro rahe hai।",
    "Zakhm itne mile zindagi mein,\nAb dard bhi mehmaan lagta hai।",
    "Mohabbat bhi kitni ajeeb hoti hai,\nJo apna hota hai wahi door hota hai।",
    "Teri kami mein ye dil rota hai,\nHar pal bas tujhe hi dhundhta hai।"
]
LOVE_SHAYARI = [
    "Tumhari muskaan hi meri jaan hai,\nTumse hi meri pehchaan hai।",
    "Ishq tumse kuch is tarah hai,\nJaise saans se zindagi।",
    "Teri aankhon mein doob jana hai,\nBas tujh mein hi kho jana hai।",
    "Tum mil gaye to laga,\nMujhe meri duniya mil gayi।"
]
ATTITUDE_SHAYARI = [
    "Hum se jalne wale bhi kamaal ke hote hai,\nMehfil apni aur charche hamare।",
    "Naam hi kaafi hai,\nPehchaan banane ke liye।",
    "Hum wahi hai jo dikhte hai,\nAur jo nahi dikhte wo khatarnaak hai।",
    "Taqat se nahi, aukaat se baat hoti hai,\nAur hamari aukaat tum soch bhi nahi sakte।"
]
SAD_SHAYARI = [
    "Aansu bhi kitne ajeeb hote hai,\nKhushi mein bhi aa jate hai।",
    "Tanha rehna seekh liya hai,\nAb kisi ki zarurat nahi।",
    "Dil ke armaan aansuon mein beh gaye,\nHum wafa karte karte reh gaye।",
    "Kisi ko apna bana ke dekho,\nFir use khone ka dard samjhoge।"
]

# ============= HUMAN AI =============
async def get_owner_mention():
    try:
        if OWNER_ID == 0: return "KING"
        user = await app.get_users(OWNER_ID)
        return f"@{user.username}" if user.username else f"<a href='tg://user?id={OWNER_ID}'>KING</a>"
    except:
        return "KING"

def human_reply(text, owner_mention):
    text = text.lower()
    if "owner" in text or "malik" in text or "bnaya kisne" in text:
        return f"मेरे KING 👑 ये रहे - {owner_mention}"
    learned = recall(text)
    if learned:
        return learned
    replies = ["hmm", "acha", "sahi hai", "fir?", "bol kya scene hai", "haan bol", "sun raha hu", "kya hua"]
    return random.choice(replies)

# ============= FLASK =============
@flask_app.route('/')
def home():
    return "KARTIK KING USERBOT IS ALIVE 👑"
def run_flask():
    flask_app.run(host='0.0.0.0', port=8080)

# ============= COMMANDS =============
@app.on_message(filters.me & filters.command("ping", "."))
async def ping(_, m: Message):
    await m.edit("Pong 🏓 KING KARTIK Zinda hai")

@app.on_message(filters.me & filters.command("help", "."))
async def help_menu(_, m: Message):
    menu = """👑 <b>KARTIK KING USERBOT MENU</b> 👑\n\n<b>1. BASIC</b>\n<code>.ping</code> - Bot check\n<code>.autoai</code> - Group me auto reply on/off\n<code>.dmai</code> - Sirf us DM me auto reply on/off\n\n<b>2. AI MEMORY</b>\n<code>.teach sawal | jawab</code> - Bot ko sikhana\n<b>3. UTILITY</b>\n<code>.afk reason</code> - AFK lagana\n<code>.tagall msg</code> - Sabko tag karna\n<b>4. SHAYARI</b> 💔\n<code>.dard</code> - Dard shayari\n<code>.love</code> - Love shayari\n<code>.attitude</code> - Attitude shayari\n<code>.sad</code> - Sad shayari\n<b>EXTRA</b>\nSticker bhejo → Bot bhi wahi sticker bhejega\n\nMade by KING KARTIK 👑"""
    await m.edit(menu)

@app.on_message(filters.me & filters.command("autoai", "."))
async def toggle_ai(_, m: Message):
    chat_id = m.chat.id
    if chat_id in ai_groups:
        ai_groups.remove(chat_id)
        c.execute("DELETE FROM groups WHERE chat_id=?", (chat_id,))
        await m.edit("GROUP AUTO REPLY OFF ❌")
    else:
        ai_groups.add(chat_id)
        c.execute("INSERT INTO groups VALUES (?)", (chat_id,))
        await m.edit("GROUP AUTO REPLY ON ✅")
    conn.commit()

@app.on_message(filters.me & filters.command("dmai", "."))
async def toggle_dm(_, m: Message):
    if not m.chat.id > 0:
        await m.edit("Ye command sirf DM me use karo")
        return
    user_id = m.chat.id
    if user_id in ai_dms:
        ai_dms.remove(user_id)
        c.execute("DELETE FROM dms WHERE user_id=?", (user_id,))
        await m.edit("DM AUTO REPLY OFF ❌ Ab is bande ko reply nahi jaayega")
    else:
        ai_dms.add(user_id)
        c.execute("INSERT INTO dms VALUES (?)", (user_id,))
        await m.edit("DM AUTO REPLY ON ✅ Ab sirf is bande ko reply jaayega")
    conn.commit()

@app.on_message(filters.me & filters.command("teach", "."))
async def teach(_, m: Message):
    try:
        q, a = m.text.split(".teach ", 1)[1].split("|", 1)
        remember(q.strip(), a.strip())
        await m.edit(f"Seekh liya KING ✅\nQ: {q}\nA: {a}")
    except:
        await m.edit("Use:.teach sawal | jawab")

@app.on_message(filters.me & filters.command("afk", "."))
async def afk(_, m: Message):
    global afk_status, afk_reason
    afk_status = True
    afk_reason = m.text.split(".afk ", 1)[1] if len(m.text.split()) > 1 else "King busy hai 👑"
    await m.edit(f"AFK ON 💤 Reason: {afk_reason}")

@app.on_message(filters.me & filters.command("tagall", "."))
async def tagall(_, m: Message):
    try: await m.delete()
    except: pass
    try:
        txt = m.text.split(".tagall ", 1)[1] if len(m.text.split()) > 1 else "Sab aa jao 👑"
        members = []
        async for member in app.get_chat_members(m.chat.id):
            if not member.user.is_bot:
                members.append(f"<a href='tg://user?id={member.user.id}'>ㅤ</a>")
        mention = ""; count = 0
        for i in members:
            mention += i; count += 1
            if count == 5:
                await app.send_message(m.chat.id, f"{txt}\n{mention}")
                mention = ""; count = 0; await asyncio.sleep(3)
        if mention:
            await app.send_message(m.chat.id, f"{txt}\n{mention}")
    except Exception as e:
        await m.reply(f"Tagall Error: {e}\nBot ko group me admin banao")

@app.on_message(filters.me & filters.command("dard", "."))
async def dard(_, m: Message):
    await m.edit(f"💔 DARD SHAYARI 💔\n\n{random.choice(DARD_SHAYARI)}")
@app.on_message(filters.me & filters.command("love", "."))
async def love(_, m: Message):
    await m.edit(f"❤️ LOVE SHAYARI ❤️\n\n{random.choice(LOVE_SHAYARI)}")
@app.on_message(filters.me & filters.command("attitude", "."))
async def attitude(_, m: Message):
    await m.edit(f"😈 ATTITUDE SHAYARI 😈\n\n{random.choice(ATTITUDE_SHAYARI)}")
@app.on_message(filters.me & filters.command("sad", "."))
async def sad(_, m: Message):
    await m.edit(f"😢 SAD SHAYARI 😢\n\n{random.choice(SAD_SHAYARI)}")

# ============= AUTO REPLY + STICKER ECHO =============
@app.on_message(filters.group & ~filters.me)
async def group_ai(_, m: Message):
    global afk_status
    try:
        owner_mention = await get_owner_mention()
        if afk_status and m.reply_to_message and m.reply_to_message.from_user.id == OWNER_ID:
            await m.reply(f"💤 KING AFK hai: {afk_reason}")
            return
        if m.chat.id not in ai_groups:
            return
        if m.sticker:
            await asyncio.sleep(1)
            await m.reply_sticker(m.sticker.file_id)
            return
        if not m.text:
            return
        await asyncio.sleep(random.uniform(1.5, 3.5))
        await app.send_chat_action(m.chat.id, ChatAction.TYPING)
        await asyncio.sleep(1)
        reply = human_reply(m.text, owner_mention)
        await m.reply_text(reply)
    except Exception as e:
        print(f"Group Error Ignore: {e}") # CRASH NAHI HOGA

@app.on_message(filters.private & ~filters.me)
async def pm_ai(_, m: Message):
    try:
        if m.from_user.id not in ai_dms:
            return
        owner_mention = await get_owner_mention()
        if m.sticker:
            await asyncio.sleep(1)
            await m.reply_sticker(m.sticker.file_id)
            return
        if not m.text:
            return
        await asyncio.sleep(random.uniform(1, 2.5))
        await app.send_chat_action(m.chat.id, ChatAction.TYPING)
        await asyncio.sleep(1)
        reply = human_reply(m.text, owner_mention)
        await m.reply_text(reply)
    except Exception as e:
        print(f"PM Error Ignore: {e}")

# ============= START =============
if __name__ == "__main__":
    for row in c.execute("SELECT chat_id FROM groups"):
        ai_groups.add(row[0])
    for row in c.execute("SELECT user_id FROM dms"):
        ai_dms.add(row[0])
    Thread(target=run_flask).start()
    print("👑 KARTIK KING USERBOT STARTED 👑")
    app.run()
