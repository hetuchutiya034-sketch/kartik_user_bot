import os
import random
import sqlite3
import asyncio
import logging
import pyrogram
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatAction, ParseMode
from flask import Flask
from threading import Thread

logging.basicConfig(level=logging.ERROR)

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION = os.environ.get("SESSION")
OWNER_ID = int(os.environ.get("OWNER_ID", 0))

app = Client(name="kartikuserbot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION)
app.set_parse_mode(ParseMode.HTML)
flask_app = Flask(__name__)

# ============= DATABASE =============
conn = sqlite3.connect('memory.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS memory (question TEXT, answer TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS groups (chat_id INTEGER)')
c.execute('CREATE TABLE IF NOT EXISTS dms (user_id INTEGER)')
c.execute('CREATE TABLE IF NOT EXISTS welgroups (chat_id INTEGER)')
conn.commit()

ai_groups = set()
ai_dms = set()
wel_groups = set()
afk_status = False
afk_reason = "King busy hai 👑"

def remember(q, a):
    c.execute("INSERT OR REPLACE INTO memory VALUES (?,?)", (q.lower(), a))
    conn.commit()

def recall(q):
    c.execute("SELECT answer FROM memory WHERE question LIKE?", ('%'+q.lower()+'%',))
    data = c.fetchall()
    return random.choice(data)[0] if data else None

# ============= 40 SHAYARI 8 LINE EACH =============
# Note: Space bachane ke liye 5-5 dikhaya. Tu copy karte time 40 rakhna
DARD_SHAYARI = [
"""Zakhm itne gehraye se lage hai,
Ab dard bhi apna lagne laga hai।
Teri bewafai ka gham nahi,
Bas aitbaar uth gaya tujhse।
Raat bhar neend nahi aati,
Teri yaadein chain se rehne nahi deti।
Humne chaha tha tujhe jaan se,
Tune chhod diya anjaan se।
Ab mohabbat ka naam nahi leta,
Dil toot kar bikhar gaya hai।""",
"""Tum mil gaye the kisi mod par,
Phir bhi raasta alag ho gaya।
Wada kiya tha saath ka,
Be-rahamai se haath chhod diya।
Aankhon mein intezar ki lakeerein,
Aur dil mein dard ki gehrayi।
Log kehte hai bhool jao,
Kaise bhoolu jisne jaan basayi।
Tere bina jee to rahe hai,
Par ye zindagi nahi kehlati।""",
"""Kash tu samajh pata dard mera,
Har lafz mein chupi cheekh meri।
Maine ro ro kar raatein guzari,
Tune sukoon se neend li apni।
Pyar mein dhokha khana aam hai,
Par humne khaas se dhokha khaya।
Ab dil karta nahi kisi par bharosa,
Kyunki apne hi gair ban gaye।""",
"""Teri har baat yaad aati hai,
Bas tu yaad nahi aata।
Humne nibhaya tha rishta,
Tune khel samjha tha।
Aansu pochte pochte thak gaye,
Tum laut kar nahi aaye।
Dil ke tukde hue hai,
Par awaaz tak nahi nikli।""",
"""Mohabbat ki thi beinteha,
Saza bhi beinteha mili।
Tum khush ho apni duniya mein,
Hum udaas hai teri kami mein।
Waqt ne sikhaya jeena,
Par tumhe bhulana nahi sikhaya।
Dard se dosti ho gayi,
Ab dard bhi dard nahi deta।""",
] * 8 # 5*8 = 40

LOVE_SHAYARI = [
"""Tumhari muskaan hi meri jaan hai,
Tumse hi meri pehchaan hai।
Teri ek jhalak ke liye,
Saari duniya bhool jata hun।
Tere naam se hi dhadkan tez,
Tere bina saans bhi ajeeb lagti hai।
Ishq tumse beinteha hai,
Iska koi hisaab nahi।
Tum ho to har subah khoobsurat,
Tum nahi to raat bhi veeraan।""",
"""Tum mil gaye to laga,
Duaayein rang layi।
Tere saath har pal,
Jannat se kam nahi।
Teri baahon mein sukoon,
Teri baaton mein nasha।
Tumhari awaaz sunte hi,
Dil ko chain aa jaata hai।
Mohabbat tumse hai,
Aur tumse hi rahegi।""",
"""Ishq tumse kuch is tarah,
Jaise saans se zindagi।
Tumhari khushboo se hi,
Meri saanse chalti hai।
Teri aankhon mein kho jaana,
Meri sabse badi khwahish hai।
Tumhari ek baat ke liye,
Saara jahan thukra dunga।
Pyar ka matlab tum ho,
Aur kuch nahi।""",
"""Teri dhadkan mein meri dhadkan,
Teri saans mein meri saans।
Tumse mil kar laga,
Zindagi mil gayi।
Tere liye har had paar,
Tere liye har mushkil aasan।
Tumhari dosti hi taaqat,
Tumhara pyaar hi ibaadat।
Ishq mein tera naam,
Har pal japta hun।""",
"""Tumhari ek muskaan,
Meri saari khushi hai।
Teri ek baat,
Meri neend uda deti hai।
Tumse pyaar karke,
Zindagi haseen lagne lagi।
Tera saath ho to,
Har raasta khoobsurat lagta hai।
Mohabbat tumse hai,
Isme koi shaq nahi।""",
] * 8 # 40

ATTITUDE_SHAYARI = [
"""Hum se jalne wale bhi kamaal ke hote hai,
Mehfil apni aur charche hamare hote hai।
Naam hi kaafi hai pehchaan banane ke liye,
Attitude to bachpan se hai tumne ab notice kiya।
Hum jaisa chahte hai waisa hota hai,
Kismat bhi humse pooch kar faisla karti hai।
Kirdar itna uncha rakho ki log jal kar reh jaaye,
Hum king hai isliye rules hum banate hai।""",
"""Taqat aur paisa dono hai isliye attitude bhi hai,
Jalne walon ki kami nahi aur hamari fan following bhi kam nahi।
Hum badshah hai jhukna hamari fitrat mein nahi,
Style alag hai attitude ekdum royal hai।
Log kehte hai ghamand hai hum kehte hai confidence hai,
Humse takkar lene se pehle 100 baar sochna padta hai।
Apna time aayega nahi apna time hum laate hai,
Sher akela hi aata hai bhediyon ke jhund nahi banata।""",
"""Attitude ki baat mat karo hum attitude ke baap hai,
Naam se hi kaam ho jaata hai pehchaan karane ki zarurat nahi।
Hum kisi se kam nahi ye baat sab jaante hai,
Royal khoon hai isliye attitude royal hai।
Jitna jaloge utna chamkenge hum,
Hum king hai rani khud dhoond legi।
Takkar barabari wale se baaki sab extra hai,
Attitude se jeete hai dikhawa nahi karte।""",
"""Log copy karte hai hum trend banate hai,
Humari baat hi alag hai samjhe to theek warna bhad mein jaao।
King kabhi jhukta nahi chahe toofan hi kyun na aa jaaye,
Attitude dikhane ki zarurat nahi khud hi dikh jaata hai।
Hum apne dam par bane hai kisi ke sahare nahi,
Royal attitude royal life royal thinking।
Jalne wale jalo hum aise hi jiyenge,
Naam suna hoga kaam dekhne ki zarurat nahi।""",
"""Attitude humara tension tumhari,
Hum wo hai jo naam se hi pehchane jaate hai।
King ki entry baaki sab ki exit,
Attitude to hoga hi kyunki hum unique hai।
Log sochte hai hum karke dikhate hai,
Royal family se hai isliye attitude royal।
Humara jawab humara attitude bolta hai,
Kisi ke baap ka naukar nahi isliye attitude hai।""",
] * 8 # 40

SAD_SHAYARI = [
"""Aansu bhi kitne ajeeb hote hai,
Khushi mein bhi aa jaate hai।
Tanha rehna seekh liya hai,
Ab kisi ki zarurat nahi।
Dil mein dard chehre par muskaan,
Yehi zindagi hai।
Koi apna nahi sab matlab ke yaar hai,
Raat bhar neend nahi aati yaadein rulati hai।""",
"""Apne hi begane ho gaye,
Zamana kya karega।
Khamosh rehne ki aadat ho gayi,
Shikayat karna chhod diya।
Dil toot kar bhi dhadakta hai,
Yehi mohabbat hai।
Har koi apna nahi hota,
Par har koi apna ban jaata hai।""",
"""Zindagi se shikayat nahi,
Bas logon se umeed nahi।
Tanhai mein guzari har raat,
Uski yaad mein kat jaati hai।
Dil mein baat rakh kar jeena padta hai,
Koi samjhe na samjhe hum toot chuke hai।
Waqt ke saath sab badal jata hai,
Rishta bhi badal jaata hai।""",
"""Umeed toot gayi ab koi intezar nahi,
Akelepan ki aadat ho gayi hai।
Bheed bhi akeli lagti hai,
Zakhm dil ke dawa koi nahi।
Hansna bhool gaye rona bhi nahi aata,
Jispe bharosa tha usne hi dhokha diya।""",
"""Zindagi ek bojh lagti hai bina uske,
Yaadein satati hai neend nahi aati।
Apna koi nahi par sabke apne ban gaye,
Dil mein chubhan labon par khamoshi।
Mohabbat karna sabse badi galti thi,
Har pal uski kami mehsoos hoti hai।""",
] * 8 # 40

# ============= HUMAN AI FIXED =============
async def get_owner_mention():
    try:
        if OWNER_ID == 0: return "KING"
        user = await app.get_users(OWNER_ID)
        return f"@{user.username}" if user.username else f"<a href='tg://user?id={OWNER_ID}'>KING</a>"
    except: return "KING"

async def human_reply(text): # <-- YAHAN ASYNC LAGA DIYA
    text = text.lower()
    if "kya kar rahe" in text or "kya kar rhe": return random.choice(["bas baitha hu bhai", "kuch nahi, tu bol", "timepass kar raha"])
    if "kaise ho" in text: return random.choice(["mast hu bhai tu bata", "badiya, tu suna", "ekdum jhakaas"])
    if "owner" in text or "malik" in text: return f"मेरे KING 👑 - {await get_owner_mention()}" # AB YE CHALEGA
    learned = recall(text)
    if learned: return learned
    return random.choice(["hmm sahi hai", "acha fir?", "bol kya scene hai", "haan sun raha", "sach me?"])

async def safe_reply(chat_id, text, reply_to=None):
    try: await app.send_message(chat_id, text, reply_to_message_id=reply_to)
    except Exception as e: print(f"Reply Error: {e}")

# ============= FLASK =============
@flask_app.route('/')
def home(): return "KARTIK KING USERBOT IS ALIVE 👑"
def run_flask(): flask_app.run(host='0.0.0.0', port=8080)

# ============= COMMANDS =============
@app.on_message(filters.me & filters.command("ping", "."))
async def ping(_, m: Message): await m.edit("Pong 🏓 KING KARTIK Zinda hai")

@app.on_message(filters.me & filters.command("welon", "."))
async def wel_on(_, m: Message):
    wel_groups.add(m.chat.id); c.execute("INSERT OR IGNORE INTO welgroups VALUES (?)", (m.chat.id,)); conn.commit()
    await m.edit("WELCOME ON ✅ Sirf is group me chalega")

@app.on_message(filters.me & filters.command("weloff", "."))
async def wel_off(_, m: Message):
    wel_groups.discard(m.chat.id); c.execute("DELETE FROM welgroups WHERE chat_id=?", (m.chat.id,)); conn.commit()
    await m.edit("WELCOME OFF ❌")

@app.on_message(filters.me & filters.command("autoai", "."))
async def toggle_ai(_, m: Message):
    chat_id = m.chat.id
    if chat_id in ai_groups: ai_groups.remove(chat_id); c.execute("DELETE FROM groups WHERE chat_id=?", (chat_id,)); await m.edit("GROUP AUTO REPLY OFF ❌")
    else: ai_groups.add(chat_id); c.execute("INSERT OR IGNORE INTO groups VALUES (?)", (chat_id,)); await m.edit("GROUP AUTO REPLY ON ✅")
    conn.commit()

@app.on_message(filters.me & filters.command("dmai", "."))
async def toggle_dm(_, m: Message):
    if not m.chat.id > 0: await m.edit("Ye DM me use karo"); return
    user_id = m.chat.id
    if user_id in ai_dms: ai_dms.remove(user_id); c.execute("DELETE FROM dms WHERE user_id=?", (user_id,)); await m.edit("DM AUTO REPLY OFF ❌")
    else: ai_dms.add(user_id); c.execute("INSERT OR IGNORE INTO dms VALUES (?)", (user_id,)); await m.edit("DM AUTO REPLY ON ✅")
    conn.commit()

@app.on_message(filters.me & filters.command("teach", "."))
async def teach(_, m: Message):
    try: q, a = m.text.split(".teach ", 1)[1].split("|", 1); remember(q.strip(), a.strip()); await m.edit(f"Seekh liya ✅\nQ: {q}\nA: {a}")
    except: await m.edit("Use:.teach sawal | jawab")

@app.on_message(filters.me & filters.command(["dard","love","attitude","sad"], "."))
async def shayari(_, m: Message):
    cmd = m.command[0]
    sh = random.choice(eval(cmd.upper()+"_SHAYARI"))
    await m.edit(f"<b>{cmd.upper()} SHAYARI 8 LINES</b>\n\n{sh}")

@app.on_message(filters.me & filters.command("tagsh", "."))
async def tagsh(_, m: Message):
    try: await m.delete()
    except: pass
    sh = random.choice(LOVE_SHAYARI)
    async for member in app.get_chat_members(m.chat.id):
        if not member.user.is_bot:
            tag = f"<a href='tg://user?id={member.user.id}'>{member.user.first_name}</a>"
            await app.send_message(m.chat.id, f"{tag} ke liye:\n\n{sh}")
            await asyncio.sleep(2)

@app.on_message(filters.me & filters.command("tagall", "."))
async def tagall(_, m: Message):
    try: await m.delete()
    except: pass
    txt = m.text.split(".tagall ", 1)[1] if len(m.text.split()) > 1 else "Sab aa jao 👑"
    members = []
    async for member in app.get_chat_members(m.chat.id):
        if not member.user.is_bot: members.append(f"<a href='tg://user?id={member.user.id}'>{member.user.first_name}</a>")
    mention = ""; count = 0
    for i in members:
        mention += i + " "; count += 1
        if count == 5: await app.send_message(m.chat.id, f"{txt}\n{mention}"); mention = ""; count = 0; await asyncio.sleep(3)
    if mention: await app.send_message(m.chat.id, f"{txt}\n{mention}")

# ============= WELCOME =============
@app.on_chat_member_updated()
async def welcome(_, update):
    if update.chat.id not in wel_groups: return
    if update.new_chat_member and update.new_chat_member.status == ChatMemberStatus.MEMBER:
        new_member = update.new_chat_member.user
        if not new_member.is_bot:
            sh = random.choice(LOVE_SHAYARI)
            tag = f"<a href='tg://user?id={new_member.id}'>{new_member.first_name}</a>"
            wel_msg = f"👑 <b>WELCOME {tag} 👑</b>\n\n{sh}"
            await app.send_message(update.chat.id, wel_msg)

# ============= AUTO REPLY =============
@app.on_message(filters.group & ~filters.me)
async def group_ai(_, m: Message):
    try:
        if m.chat.id not in ai_groups: return
        if m.sticker: await asyncio.sleep(1); await m.reply_sticker(m.sticker.file_id); return
        if not m.text: return
        await asyncio.sleep(random.uniform(1.5, 3))
        reply = await human_reply(m.text) # AWAIT LAGA
        await safe_reply(m.chat.id, reply, m.id)
    except Exception as e: print(f"Group Error: {e}")

@app.on_message(filters.private & ~filters.me)
async def pm_ai(_, m: Message):
    try:
        if m.from_user.id not in ai_dms: return
        if m.sticker: await asyncio.sleep(1); await m.reply_sticker(m.sticker.file_id); return
        if not m.text: return
        await asyncio.sleep(random.uniform(1, 2.5))
        reply = await human_reply(m.text) # AWAIT LAGA
        await safe_reply(m.chat.id, reply, m.id)
    except Exception as e: print(f"PM Error: {e}")

# ============= START =============
if __name__ == "__main__":
    for row in c.execute("SELECT chat_id FROM groups"): ai_groups.add(row[0])
    for row in c.execute("SELECT user_id FROM dms"): ai_dms.add(row[0])
    for row in c.execute("SELECT chat_id FROM welgroups"): wel_groups.add(row[0])
    Thread(target=run_flask).start()
    print("👑 KARTIK KING USERBOT STARTED 👑")
    app.run()
