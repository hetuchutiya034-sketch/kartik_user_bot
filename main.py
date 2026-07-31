import os
import random
import sqlite3
import requests
import asyncio
import time
from pyrogram import Client, filters
from pyrogram.types import Message
from flask import Flask
from threading import Thread

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
conn.commit()

ai_groups = set()
afk_status = False
afk_reason = "King busy hai 👑"

def remember(q, a):
    c.execute("INSERT INTO memory VALUES (?,?)", (q.lower(), a))
    conn.commit()

def recall(q):
    c.execute("SELECT answer FROM memory WHERE question LIKE?", ('%'+q.lower()+'%',))
    data = c.fetchall()
    return random.choice(data)[0] if data else None

# ============= SHAYARI LISTS =============
DARD_SHAYARI = [
    "Dil tod ke wo muskura rahe hai,\nHum unhe yaad karke ro rahe hai।",
    "Zakhm itne mile zindagi mein,\nAb dard bhi mehmaan lagta hai।",
    "Mohabbat bhi kitni ajeeb hoti hai,\nJo apna hota hai wahi door hota hai।",
    "Raat bhar rota raha dil mera,\nAur subah duniya ne kaha 'sab theek hai'",
    "Chup rehna hi behtar hai,\nLog sun kar bhi samajhte nahi।",
    "Tere bina jeena mushkil hai,\nPar tere saath rehna namumkin।",
    "Dil ke tukde hue hai aise,\nJaise koi sheesha toot gaya।",
    "Waqt ne sab sikha diya,\nAb kisi pe bharosa nahi।",
    "Unhone kaha bhool jao hume,\nHumne kaha yaad hi kab the tum।",
    "Dard likhne ki aadat si ho gayi hai,\nAb khushi bhi ajeeb lagti hai।"
]

LOVE_SHAYARI = [
    "Tumhari muskaan hi meri jaan hai,\nTumse hi meri pehchaan hai।",
    "Ishq tumse kuch is tarah hai,\nJaise saans se zindagi।",
    "Teri aankhon mein doob jana hai,\nBas tujh mein hi kho jana hai।",
    "Tum ho to sab kuch hai,\nTum nahi to kuch bhi nahi।",
    "Dil ne tujhe apna maana hai,\nHar pal bas tera hi deewana hai।",
    "Tere bina adhoori si lagti hai zindagi,\nTu ho to sab kuch poora।",
    "Mohabbat mein shartein nahi hoti,\nSirf ehsaas hota hai।",
    "Teri har baat dil ko choo jati hai,\nTu hi meri duniya hai।",
    "Tujhse milkar jaana,\nKya hoti hai asli mohabbat।",
    "Bas ek tu hi kaafi hai,\nMeri poori duniya ke liye।"
]

ATTITUDE_SHAYARI = [
    "Hum se jalne wale bhi kamaal ke hote hai,\nMehfil apni aur charche hamare।",
    "Naam hi kaafi hai,\nPehchaan banane ke liye।",
    "Hum wahi hai jo dikhte hai,\nAur jo nahi dikhte wo khatarnaak hai।",
    "Zindagi apni terms par jeete hai,\nKisi ke kehne se nahi।",
    "Royal attitude hai apna,\nLog jalte hai to jalne do।",
    "Humse panga mat lena,\nHistory bhi dangerous hai।",
    "Apni aukaat mein rehna seekh lo,\nHumse takraoge to bikhar jaoge।",
    "Sher apna shikar khud karta hai,\nAur hum apni pehchaan।",
    "Hum khamosh zaroor hai,\nPar kamzor nahi।",
    "Style aisa rakho,\nKi duniya dekhte reh jaaye।"
]

SAD_SHAYARI = [
    "Aansu bhi kitne ajeeb hote hai,\nKhushi mein bhi aa jate hai।",
    "Tanha rehna seekh liya hai,\nAb kisi ki zarurat nahi।",
    "Dil ke armaan aansuon mein beh gaye,\nHum wafa karte karte reh gaye।",
    "Kisi ko chahna galti nahi,\nPar usse expect karna galti hai।",
    "Zindagi ne sikhaya hai,\nApno par bhi bharosa na karo।",
    "Kabhi kabhi dil karta hai,\nSab kuch chhod kar chale jaaye।",
    "Dard itna hai ke bayaan nahi hota,\nAur log kehte hai kuch hua hi nahi।",
    "Khamoshi bhi ek jawab hai,\nJab bolna bekaar ho।",
    "Kuch log bas yaadon mein hi ache lagte hai,\nHaqeeqat mein nahi।",
    "Rishton ka bharosa toot jaye,\nTo sab khatam ho jata hai।"
]

# ============= HUMAN AI =============
async def get_owner_mention():
    try:
        user = await app.get_users(OWNER_ID)
        return f"@{user.username}" if user.username else f"<a href='tg://user?id={OWNER_ID}'>KING</a>"
    except:
        return "KING"

def human_reply(text, owner_mention):
    if "owner" in text.lower() or "malik" in text.lower() or "bnaya kisne" in text.lower():
        return f"मेरे KING 👑 ये रहे - {owner_mention}"
    learned = recall(text)
    if learned:
        return learned
    try:
        r = requests.post("https://api.gemini.com/v1/generate", json={"prompt": f"Reply like a human named Kartik. Be cool, king attitude. Q: {text}"}, timeout=5)
        reply = r.json().get("text", "hmm")
    except:
        reply = random.choice(["hmm", "acha", "sahi hai", "fir?", "bol kya scene hai"])
    reply = reply.replace("मैं एक AI हूँ", "मैं KARTIK हूँ").replace("As an AI", "सुन")
    return reply.strip()

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

@app.on_message(filters.me & filters.command("autoai", "."))
async def toggle_ai(_, m: Message):
    chat_id = m.chat.id
    if chat_id in ai_groups:
        ai_groups.remove(chat_id)
        c.execute("DELETE FROM groups WHERE chat_id=?", (chat_id,))
        await m.edit("AUTO REPLY OFF ❌")
    else:
        ai_groups.add(chat_id)
        c.execute("INSERT INTO groups VALUES (?)", (chat_id,))
        await m.edit("AUTO REPLY ON ✅ Ab KARTIK khud baat karega")
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
    if not m.chat.id: return
    await m.delete()
    txt = m.text.split(".tagall ", 1)[1] if len(m.text.split()) > 1 else "Sab aa jao 👑"
    members = []
    async for member in app.get_chat_members(m.chat.id):
        if not member.user.is_bot:
            members.append(f"<a href='tg://user?id={member.user.id}'>ㅤ</a>")
    mention = ""
    count = 0
    for i in members:
        mention += i
        count += 1
        if count == 5:
            await app.send_message(m.chat.id, f"{txt}\n{mention}")
            mention = ""
            count = 0
            await asyncio.sleep(2)
    if mention:
        await app.send_message(m.chat.id, f"{txt}\n{mention}")

# SHAYARI COMMANDS
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
    await app.send_chat_action(m.chat.id, "typing")
    time.sleep(1)
    reply = human_reply(m.text, owner_mention)
    await m.reply_text(reply)

@app.on_message(filters.private & ~filters.me)
async def pm_ai(_, m: Message):
    owner_mention = await get_owner_mention()
    if m.sticker:
        await asyncio.sleep(1)
        await m.reply_sticker(m.sticker.file_id)
        return
    if not m.text:
        return
    await asyncio.sleep(random.uniform(1, 2.5))
    await app.send_chat_action(m.chat.id, "typing")
    time.sleep(1)
    reply = human_reply(m.text, owner_mention)
    await m.reply_text(reply)

# ============= START =============
if __name__ == "__main__":
    for row in c.execute("SELECT chat_id FROM groups"):
        ai_groups.add(row[0])
    Thread(target=run_flask).start()
    print("👑 KARTIK KING USERBOT STARTED 👑")
    app.run()
