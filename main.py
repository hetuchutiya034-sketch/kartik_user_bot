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

app = Client(
    name="kartikuserbot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION
)
app.set_parse_mode(ParseMode.HTML) # FIXED
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

# ============= 40-40 SHAYARI =============
DARD_SHAYARI = [
"Zakhm itne mile zindagi mein, ab dard bhi mehmaan lagta hai।",
"Dil tod ke wo muskura rahe hai, hum unhe yaad karke ro rahe hai।",
"Teri bewafai ka gham nahi, bas aitbaar uth gaya tujhse।",
"Rone se koi laut kar nahi aata, par rula kar koi sukoon se bhi nahi sota।",
"Chaha tha jise jaan se zyada, usne hi dard diya sabse zyada।",
"Ab mohabbat karne ka dil nahi karta, kyunki bharosa toot chuka hai।",
"Kuch log aise milte hai, jo sabak dekar chale jate hai।",
"Tanhaai mein uski yaad aati hai, aur dil phir se toot jata hai।",
"Humne mohabbat ki thi, gunah nahi kiya tha।",
"Usne kaha tha saath nibhayenge, par beech raaste mein chhod gaya।",
"Dard chupane ki aadat ho gayi hai, isliye sab kehte hai khush rehta hai।",
"Kash kabhi usko bhi hamara dard mehsoos ho।",
"Pyar mein dhokha khana aam baat hai, par humne khaas se dhokha khaya।",
"Intezar karte karte thak gaye, wo laut kar nahi aaya।",
"Jisne apna kaha tha, wahi sabse bada gair nikla।",
"Ansu pochte pochte aankhe dukh gayi, par wo wapas nahi aaya।",
"Wo khush hai apni duniya mein, aur hum uski yaad mein।",
"Dard ki dawa nahi hoti, bas sehne ki aadat ho jati hai।",
"Tere bina jee to rahe hai, par jeena nahi kehte isko।",
"Kisi aur ki ho kar bhi wo meri duaon mein rehta hai।",
"Mohabbat adhuri reh gayi, kahaani khatam ho gayi।",
"Uski har baat yaad aati hai, bas wo yaad nahi aata।",
"Dil mein dard, labon par muskaan, yehi zindagi hai।",
"Tumne badal kar dekh liya, humne nibha kar dekh liya।",
"Zakhm gehrai se lage hai, isliye dard bhi gehrai se hota hai।",
"Wo bhool gaya hume, hum bhool nahi paaye usko।",
"Pyar mein sab kuch qurbani mangta hai, humne khud ko hi qurban kar diya।",
"Teri yaad ka mausam har pal rehta hai।",
"Koi samjha hi nahi dard mera, sabne majak samjha।",
"Rishta toot gaya, par ehsaas abhi bhi baaki hai।",
"Humne chaha tha usko, usne majboori bata di।",
"Dard se dosti ho gayi hai, ab dard nahi hota।",
"Tumhari khushi mein hi meri khushi thi, par tum hi khush nahi।",
"Ek jhootha rishta nibhate nibhate thak gaye।",
"Tum mil gaye the, par apne nahi ban paaye।",
"Yaad karna aadat ban gayi hai, bhoolna mumkin nahi।",
"Dil toota hai par awaaz nahi, yehi sabse bada dard hai।",
"Tere ishq ne barbaad kar diya, phir bhi shikayat nahi।",
"Kash tu laut aaye, ye umeed bhi khatam ho gayi।",
"Zindagi ne itna rulaya, ki ab rona bhi nahi aata।"
]

LOVE_SHAYARI = [
"Tumhari muskaan hi meri jaan hai, tumse hi meri pehchaan hai।",
"Ishq tumse kuch is tarah hai, jaise saans se zindagi।",
"Teri ek jhalak ke liye, saari duniya bhool jata hun।",
"Tum mil gaye to laga, duaayein rang layi।",
"Tere naam se hi dhadkan tez ho jati hai।",
"Mohabbat ki inteha kar di, tumhe apna bana liya।",
"Tumhari baahon mein sukoon milta hai, duniya bhool jata hun।",
"Pyaar kiya hai tumse, isme koi shaq nahi।",
"Teri har baat dil ko chu jati hai।",
"Tum ho to har subah khoobsurat lagti hai।",
"Ishq mein teri galiyan, har raasta khoobsurat lagta hai।",
"Tumhari awaaz sunte hi din ban jata hai।",
"Mohabbat tumse hai, aur tumse hi rahegi।",
"Teri aankhon mein kho jane ka mann karta hai।",
"Tumhari khushboo se hi saanse chalti hai।",
"Pyar ka matlab tum ho, aur kuch nahi।",
"Tumse mil kar laga, zindagi mil gayi।",
"Tere liye har had paar kar jaunga।",
"Tumhari dosti hi meri taaqat hai।",
"Ishq mein tera naam japta hun, aur kuch nahi।",
"Tumhari ek baat ke liye, saara jahan thukra dunga।",
"Tum ho to sab kuch hai, tum nahi to kuch nahi।",
"Teri yaad mein hi har pal guzarta hai।",
"Mohabbat karna gunah nahi, tumse ki hai ye saboot hai।",
"Tumhari baatein neend uda deti hai।",
"Tumse pyar karke zindagi khoobsurat lagne lagi।",
"Tera saath ho to har mushkil aasan lagti hai।",
"Ishq tumse beinteha, iska koi hisaab nahi।",
"Tumhari ek muskaan ke liye, saari khushi luta dunga।",
"Tum mil gaye to manzil mil gayi।",
"Teri dhadkan mein meri dhadkan basi hai।",
"Pyar mein teri wafadari sabse upar hai।",
"Tumhari har ada par dil aa jata hai।",
"Mohabbat mein tumhari kasam, dhokha nahi dunga।",
"Tumhari yaad aaye to chain nahi aata।",
"Tumse milne ki khwahish har pal rehti hai।",
"Tera naam lete hi chehre par muskaan aa jati hai।",
"Ishq mein tumhari baatein hi nasha hai।",
"Tum ho to duniya haseen lagti hai।",
"Tere bina ek pal bhi guzarna mushkil hai।"
]

ATTITUDE_SHAYARI = [
"Hum se jalne wale bhi kamaal ke hote hai, mehfil apni aur charche hamare।",
"Naam hi kaafi hai, pehchaan banane ke liye।",
"Attitude to bachpan se hai, tumne ab notice kiya।",
"Hum jaisa chahte hai waisa hota hai, kismat bhi humse poochti hai।",
"Kirdar itna uncha rakho, ki log jal kar reh jaaye।",
"Hum king hai, isliye rules hum banate hai।",
"Taqat aur paisa dono hai, isliye attitude bhi hai।",
"Jalne walon ki kami nahi, aur hamari fan following bhi kam nahi।",
"Hum badshah hai, jhukna hamari fitrat mein nahi।",
"Style alag hai, attitude ekdum royal।",
"Log kehte hai ghamand hai, hum kehte hai confidence hai।",
"Humse takkar lene se pehle 100 baar sochna।",
"Apna time aayega nahi, apna time hum laate hai।",
"Sher akela hi aata hai, bhediyon ke jhund nahi banata।",
"Attitude ki baat mat karo, hum attitude ke baap hai।",
"Naam se hi kaam ho jata hai, pehchaan karane ki zarurat nahi।",
"Hum kisi se kam nahi, ye baat sab jaante hai।",
"Royal khoon hai, isliye attitude royal hai।",
"Jitna jaloge, utna chamkenge hum।",
"Hum king hai, rani khud dhoond legi।",
"Takkar barabari wale se, baaki sab extra hai।",
"Attitude se jeete hai, dikhawa nahi karte।",
"Log copy karte hai, hum trend banate hai।",
"Humari baat hi alag hai, samjhe to theek warna bhad mein jaao।",
"King kabhi jhukta nahi, chahe toofan hi kyun na aa jaaye।",
"Attitude dikhane ki zarurat nahi, khud hi dikh jata hai।",
"Hum apne dam par bane hai, kisi ke sahare nahi।",
"Royal attitude, royal life, royal thinking।",
"Jalne wale jalo, hum aise hi jiyenge।",
"Naam suna hoga, kaam dekhne ki zarurat nahi।",
"Attitude humara, tension tumhari।",
"Hum wo hai jo naam se hi pehchane jate hai।",
"King ki entry, baaki sab ki exit।",
"Attitude to hoga hi, kyunki hum unique hai।",
"Log sochte hai, hum karke dikhate hai।",
"Royal family se hai, isliye attitude royal।",
"Humara jawab, humara attitude bolta hai।",
"Kisi ke baap ka naukar nahi, isliye attitude hai।",
"Jitna izzat doge, utna attitude milega।",
"King hai hum, crown sar par aur attitude dil mein।"
]

SAD_SHAYARI = [
"Aansu bhi kitne ajeeb hote hai, khushi mein bhi aa jate hai।",
"Tanha rehna seekh liya hai, ab kisi ki zarurat nahi।",
"Dil mein dard, chehre par muskaan, yehi zindagi hai।",
"Koi apna nahi, sab matlab ke yaar hai।",
"Raat bhar neend nahi aati, yaadein rulati hai।",
"Apne hi begane ho gaye, zamana kya karega।",
"Khamosh rehne ki aadat ho gayi hai, shikayat karna chhod diya।",
"Dil toot kar bhi dhadakta hai, yehi mohabbat hai।",
"Har koi apna nahi hota, par har koi apna ban jata hai।",
"Zindagi se shikayat nahi, bas logon se umeed nahi।",
"Tanhai mein guzari har raat, uski yaad mein kat jaati hai।",
"Dil mein baat rakh kar jeena padta hai।",
"Koi samjhe na samjhe, hum toot chuke hai।",
"Waqt ke saath sab badal jata hai, rishta bhi।",
"Umeed toot gayi, ab koi intezar nahi।",
"Akelepan ki aadat ho gayi hai, ab bheed bhi akeli lagti hai।",
"Zakhm dil ke, dawa koi nahi।",
"Hansna bhool gaye, rona bhi nahi aata।",
"Jispe bharosa tha, usne hi dhokha diya।",
"Zindagi ek bojh lagti hai, bina uske।",
"Yaadein satati hai, neend nahi aati।",
"Apna koi nahi, par sabke apne ban gaye।",
"Dil mein chubhan, labon par khamoshi।",
"Mohabbat karna sabse badi galti thi।",
"Har pal uski kami mehsoos hoti hai।",
"Tod diya usne, jodna mushkil hai।",
"Zindagi mein sukoon nahi, bas dard hi dard hai।",
"Koi apna hota to haal poochta।",
"Rishta nibhate nibhate thak gaye।",
"Ab kisi se umeed nahi, na koi umeed hai।",
"Tanhai sabse achi dost ban gayi hai।",
"Dil mein dard ka toofan, bahar sannaata।",
"Jo apna tha wo paraya ho gaya।",
"Zindagi ne itna rulaya, ki ab hasi bhi nahi aati।",
"Har khushi mein uski kami lagti hai।",
"Waqt sab bhoola deta hai, par yaadein nahi।",
"Dil mein sawaal, jawab koi nahi।",
"Jeene ki wajah chali gayi, jeena reh gaya।",
"Koi apna ho to dard bataye bhi।",
"Raat ki tanhai, aur uski yaadein।"
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
    if learned: return learned
    return random.choice(["hmm", "acha", "sahi hai", "fir?", "bol kya scene hai", "haan bol bhai"])

async def safe_reply(chat_id, text, reply_to=None):
    try:
        await app.send_message(chat_id, text, reply_to_message_id=reply_to)
    except Exception as e:
        print(f"Reply Error Ignore: {e}")

# ============= FLASK =============
@flask_app.route('/')
def home(): return "KARTIK KING USERBOT IS ALIVE 👑"
def run_flask(): flask_app.run(host='0.0.0.0', port=8080)

# ============= COMMANDS =============
@app.on_message(filters.me & filters.command("ping", "."))
async def ping(_, m: Message): await m.edit("Pong 🏓 KING KARTIK Zinda hai")

@app.on_message(filters.me & filters.command("help", "."))
async def help_menu(_, m: Message):
    menu = """👑 <b>KARTIK KING USERBOT MENU</b> 👑\n\n<b>1. BASIC</b>\n<code>.ping</code> - Bot check\n<code>.autoai</code> - Group me auto reply on/off\n<code>.dmai</code> - Sirf us DM me auto reply on/off\n<b>2. AI MEMORY</b>\n<code>.teach sawal | jawab</code> - Bot ko sikhana\n<b>3. UTILITY</b>\n<code>.afk reason</code> - AFK lagana\n<code>.tagall msg</code> - Sabko tag karna\n<b>4. SHAYARI</b> 💔\n<code>.dard</code> <code>.love</code> <code>.attitude</code> <code>.sad</code>\n\nMade by KING KARTIK 👑"""
    await m.edit(menu)

@app.on_message(filters.me & filters.command("autoai", "."))
async def toggle_ai(_, m: Message):
    chat_id = m.chat.id
    if chat_id in ai_groups: ai_groups.remove(chat_id); c.execute("DELETE FROM groups WHERE chat_id=?", (chat_id,)); await m.edit("GROUP AUTO REPLY OFF ❌")
    else: ai_groups.add(chat_id); c.execute("INSERT INTO groups VALUES (?)", (chat_id,)); await m.edit("GROUP AUTO REPLY ON ✅")
    conn.commit()

@app.on_message(filters.me & filters.command("dmai", "."))
async def toggle_dm(_, m: Message):
    if not m.chat.id > 0: await m.edit("Ye command sirf DM me use karo"); return
    user_id = m.chat.id
    if user_id in ai_dms: ai_dms.remove(user_id); c.execute("DELETE FROM dms WHERE user_id=?", (user_id,)); await m.edit("DM AUTO REPLY OFF ❌")
    else: ai_dms.add(user_id); c.execute("INSERT INTO dms VALUES (?)", (user_id,)); await m.edit("DM AUTO REPLY ON ✅")
    conn.commit()

@app.on_message(filters.me & filters.command("teach", "."))
async def teach(_, m: Message):
    try: q, a = m.text.split(".teach ", 1)[1].split("|", 1); remember(q.strip(), a.strip()); await m.edit(f"Seekh liya KING ✅\nQ: {q}\nA: {a}")
    except: await m.edit("Use:.teach sawal | jawab")

@app.on_message(filters.me & filters.command("afk", "."))
async def afk(_, m: Message):
    global afk_status, afk_reason
    afk_status = True; afk_reason = m.text.split(".afk ", 1)[1] if len(m.text.split()) > 1 else "King busy hai 👑"
    await m.edit(f"AFK ON 💤 Reason: {afk_reason}")

@app.on_message(filters.me & filters.command("tagall", "."))
async def tagall(_, m: Message):
    try: await m.delete()
    except: pass
    try:
        txt = m.text.split(".tagall ", 1)[1] if len(m.text.split()) > 1 else "Sab aa jao 👑"
        members = []
        async for member in app.get_chat_members(m.chat.id):
            if not member.user.is_bot: members.append(f"<a href='tg://user?id={member.user.id}'>ㅤ</a>")
        mention = ""; count = 0
        for i in members:
            mention += i; count += 1
            if count == 5: await app.send_message(m.chat.id, f"{txt}\n{mention}"); mention = ""; count = 0; await asyncio.sleep(3)
        if mention: await app.send_message(m.chat.id, f"{txt}\n{mention}")
    except Exception as e: await m.reply(f"Tagall Error: {e}")

@app.on_message(filters.me & filters.command("dard", "."))
async def dard(_, m: Message): await m.edit(f"💔 DARD SHAYARI 💔\n\n{random.choice(DARD_SHAYARI)}")
@app.on_message(filters.me & filters.command("love", "."))
async def love(_, m: Message): await m.edit(f"❤️ LOVE SHAYARI ❤️\n\n{random.choice(LOVE_SHAYARI)}")
@app.on_message(filters.me & filters.command("attitude", "."))
async def attitude(_, m: Message): await m.edit(f"😈 ATTITUDE SHAYARI 😈\n\n{random.choice(ATTITUDE_SHAYARI)}")
@app.on_message(filters.me & filters.command("sad", "."))
async def sad(_, m: Message): await m.edit(f"😢 SAD SHAYARI 😢\n\n{random.choice(SAD_SHAYARI)}")

# ============= AUTO REPLY + STICKER ECHO =============
@app.on_message(filters.group & ~filters.me)
async def group_ai(_, m: Message):
    try:
        print(f"GROUP MSG: {m.chat.id}")
        if m.chat.id not in ai_groups: return
        if m.sticker: await asyncio.sleep(1); await m.reply_sticker(m.sticker.file_id); return
        if not m.text: return
        await asyncio.sleep(2)
        reply = human_reply(m.text, await get_owner_mention())
        await safe_reply(m.chat.id, reply, m.id)
    except Exception as e: print(f"Group Error: {e}")

@app.on_message(filters.private & ~filters.me)
async def pm_ai(_, m: Message):
    try:
        print(f"DM MILA: {m.from_user.id}")
        if m.from_user.id not in ai_dms: return
        if m.sticker: await asyncio.sleep(1); await m.reply_sticker(m.sticker.file_id); return
        if not m.text: return
        await asyncio.sleep(1.5)
        reply = human_reply(m.text, await get_owner_mention())
        await safe_reply(m.chat.id, reply, m.id)
    except Exception as e: print(f"PM Error: {e}")

# ============= START =============
if __name__ == "__main__":
    print("API_ID:", API_ID)
    print("OWNER_ID:", OWNER_ID)
    for row in c.execute("SELECT chat_id FROM groups"): ai_groups.add(row[0])
    for row in c.execute("SELECT user_id FROM dms"): ai_dms.add(row[0])
    Thread(target=run_flask).start()
    print("👑 KARTIK KING USERBOT STARTED 👑")
    app.run()
