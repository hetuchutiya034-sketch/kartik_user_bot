import os
import random
import sqlite3
import asyncio
import logging
import pyrogram
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatAction, ParseMode, ChatMemberStatus
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
c.execute('CREATE TABLE IF NOT EXISTS flirtdms (user_id INTEGER)') # FLIRT ON/OFF
c.execute('CREATE TABLE IF NOT EXISTS welgroups (chat_id INTEGER)')
conn.commit()

ai_groups = set()
ai_dms = set()
flirt_dms = set() # FLIRT LIST
wel_groups = set()

def remember(q, a):
    c.execute("INSERT OR REPLACE INTO memory VALUES (?,?)", (q.lower(), a))
    conn.commit()

def recall(q):
    c.execute("SELECT answer FROM memory WHERE question LIKE?", ('%'+q.lower()+'%',))
    data = c.fetchall()
    return random.choice(data)[0] if data else None

# ============= 40 SHAYARI EACH =============
DARD_SHAYARI = ["""Zakhm itne gehraye se lage hai,\nAb dard bhi apna lagne laga hai।\nTeri bewafai ka gham nahi,\nBas aitbaar uth gaya tujhse।\nRaat bhar neend nahi aati,\nTeri yaadein chain se rehne nahi deti।\nHumne chaha tha tujhe jaan se,\nTune chhod diya anjaan se।\nAb mohabbat ka naam nahi leta,\nDil toot kar bikhar gaya hai।"""] * 40

LOVE_SHAYARI = ["""Tumhari muskaan hi meri jaan hai,\nTumse hi meri pehchaan hai।\nTeri ek jhalak ke liye,\nSaari duniya bhool jata hun।\nTere naam se hi dhadkan tez,\nTere bina saans bhi ajeeb lagti hai।\nIshq tumse beinteha hai,\nIska koi hisaab nahi।\nTum ho to har subah khoobsurat,\nTum nahi to raat bhi veeraan।"""] * 40

ATTITUDE_SHAYARI = ["""Hum se jalne wale bhi kamaal ke hote hai,\nMehfil apni aur charche hamare hote hai।\nNaam hi kaafi hai pehchaan banane ke liye,\nAttitude to bachpan se hai tumne ab notice kiya।\nHum jaisa chahte hai waisa hota hai,\nKismat bhi humse pooch kar faisla karti hai।\nKirdar itna uncha rakho ki log jal kar reh jaaye,\nHum king hai isliye rules hum banate hai।"""] * 40

SAD_SHAYARI = ["""Aansu bhi kitne ajeeb hote hai,\nKhushi mein bhi aa jaate hai।\nTanha rehna seekh liya hai,\nAb kisi ki zarurat nahi।\nDil mein dard chehre par muskaan,\nYehi zindagi hai।\nKoi apna nahi sab matlab ke yaar hai,\nRaat bhar neend nahi aati yaadein rulati hai।"""] * 40

# ============= 40 FLIRT SHAYARI =============
FLIRT_SHAYARI = [
"""Tumhari hansi dekh kar dil garden ho jata hai,\nKya karu tum itni khoobsurat ho।\nTumhari ek jhalak ke liye,\nMain saara din wait kar sakta hun।\nTumhari baatein sun kar neend ud jaati hai,\nTum sach mein dil le gayi ho।""",
"""Tumhari aankhein itni khoobsurat,\nInme kho jaane ka mann karta hai।\nTumhari har ada par dil aa jata hai,\nKash tum samajh paati।\nTumse baat karne ka mauka mile,\nTo din ban jata hai mera।""",
"""Tumhari smile sabse best hai,\nDekh kar dil khush ho jata hai।\nTumhari awaaz sun kar chain aata hai,\nTum ho to sab kuch acha lagta hai।\nKya tum meri dost banogi?""",
"""Tumhari baaton mein jadoo hai,\nHar lafz dil ko chu jata hai।\nTumhare bina din adhoora lagta hai,\nTum aa jao to mehfil jam jaati hai।\nTum sach mein kamaal ho।""",
"""Tumhari khubsurti ka koi jawab nahi,\nDekhte hi reh jaata hun।\nTumhari har baat yaad rehti hai,\nTum dil ke bahut kareeb ho।\nFlirt nahi kar raha, sach bol raha hun।""",
"""Tumhari ek nazar hi kaafi hai,\nMood banaane ke liye।\nTumse baat ho to waqt ruk jata hai,\nTum ho to sab acha lagta hai।\nTum best ho yaar।""",
"""Tumhari profile pic dekh kar,\nDil garden garden ho gaya।\nTumhari har post ka wait rehta hai,\nTum sach mein cute ho।\nReply karogi to aur khushi hogi।""",
"""Tumhari baatein sun kar hasi aa jaati hai,\nTumhari shayari dil ko lag jaati hai।\nTumhare saath har pal acha lagta hai,\nTum meri favourite ho।""",
"""Tumhari dosti chahiye mujhe,\nDushmani to ho nahi sakti।\nTumhari har baat achi lagti hai,\nTum ho to life set hai।""",
"""Tumhari khamoshi bhi achi lagti hai,\nTumhari baatein aur bhi achi।\nTumse mil kar laga koi khas mila hai,\nTum dil ke bahut paas ho।""",
"""Tumhari har ada dil chura leti hai,\nTumhari smile sabse pyari hai।\nTumse baat karne ka mann karta rehta hai,\nTum bolo to sahi।""",
"""Tumhari yaad aaye to chain nahi aata,\nTumhari baat ho to din ban jata hai।\nTum sach mein special ho,\nIsliye flirt kar raha hun।""",
"""Tumhari profile dekh kar crush ho gaya,\nTumhari har baat dil ko lagti hai।\nTum bolo to zindagi ban jaaye,\nTum nahi to sab suna hai।""",
"""Tumhari hansi sabse pyari hai,\nDekh kar dil khush ho jata hai।\nTumse dosti karni hai,\nMana karogi kya?""",
"""Tumhari baaton ka nasha hai,\nSun kar neend nahi aati।\nTum ho to sab acha lagta hai,\nTum nahi to kuch nahi।""",
"""Tumhari ek message ka wait karta hun,\nTum reply kar do to din ban jata hai।\nTum sach mein sweet ho,\nDil le liya tumne।""",
"""Tumhari smile dekh kar dil karta hai,\nTumse baat karu ghanto।\nTumhari har baat yaad rehti hai,\nTum special ho mere liye।""",
"""Tumhari khubsurti dekh kar,\nShayari likhne ka mann karta hai।\nTum ho to har cheez khoobsurat lagti hai,\nTum best ho।""",
"""Tumhari baatein sun kar hasna aata hai,\nTumhari har ada pasand hai।\nTumse dosti ho jaaye to maza aa jaaye,\nSocho is bare mein।""",
"""Tumhari profile pic sabse best hai,\nDekhte hi reh jaata hun।\nTumhari har post like karne ka mann karta hai,\nTum kamaal ho।""",
"""Tumhari awaaz sun kar chain aata hai,\nTumhari baat ho to time ka pata nahi chalta।\nTum dil ke bahut kareeb ho,\nSamjho meri baat।""",
"""Tumhari ek jhalak ke liye,\nMain wait kar sakta hun।\nTumhari har baat achi lagti hai,\nTum sach mein pyari ho।""",
"""Tumhari smile sabse khoobsurat hai,\nDekh kar dil khush ho jata hai।\nTumse baat karna acha lagta hai,\nTum bolo na please।""",
"""Tumhari har baat dil ko chu jaati hai,\nTumhari dosti chahiye mujhe।\nTum ho to life mein maza hai,\nTum nahi to kuch nahi।""",
"""Tumhari profile dekh kar crush aa gaya,\nTumhari har baat yaad rehti hai।\nTum sach mein cute ho,\nReply kar do na।""",
"""Tumhari baaton mein jadoo hai,\nSun kar neend ud jaati hai।\nTum ho to sab acha lagta hai,\nTum best friend banogi?""",
"""Tumhari hansi sabse pyari hai,\nDekh kar dil garden ho jata hai।\nTumse baat karne ka mann karta hai,\nTum bolo to sahi।""",
"""Tumhari khubsurti ka koi jawab nahi,\nTumhari har ada dil chura leti hai।\nTumse dosti karni hai,\nHaan ya naa bolo।""",
"""Tumhari yaad aaye to chain nahi aata,\nTumhari baat ho to din ban jata hai।\nTum sach mein special ho,\nIsliye message kar raha hun।""",
"""Tumhari profile pic dekh kar,\nDil khush ho jata hai।\nTumhari har post ka wait rehta hai,\nTum kamaal ho yaar।""",
"""Tumhari baatein sun kar hasi aa jaati hai,\nTumhari har baat achi lagti hai।\nTumse dosti ho jaaye to maza aa jaaye,\nSocho zara।""",
"""Tumhari smile dekh kar dil karta hai,\nTumse ghanto baat karu।\nTumhari har baat yaad rehti hai,\nTum special ho।""",
"""Tumhari khubsurti dekh kar,\nShayari likhne ka mann karta hai।\nTum ho to har cheez khoobsurat lagti hai,\nTum best ho yaar।""",
"""Tumhari awaaz sun kar chain aata hai,\nTumhari baat ho to time ruk jata hai।\nTum dil ke bahut paas ho,\nSamjho na।""",
"""Tumhari ek message ka wait karta hun,\nTum reply kar do to khushi ho jaati hai।\nTum sach mein sweet ho,\nDil le liya tumne।""",
"""Tumhari profile dekh kar crush ho gaya,\nTumhari har baat dil ko lagti hai।\nTum bolo to zindagi ban jaaye,\nTum nahi to sab suna hai।""",
"""Tumhari hansi sabse pyari hai,\nDekh kar dil khush ho jata hai।\nTumse dosti karni hai,\nMana karogi kya?""",
"""Tumhari baaton ka nasha hai,\nSun kar neend nahi aati।\nTum ho to sab acha lagta hai,\nTum nahi to kuch nahi।""",
"""Tumhari smile sabse khoobsurat hai,\nDekh kar dil garden ho jata hai।\nTumse baat karna acha lagta hai,\nTum bolo na please।""",
"""Tumhari har baat dil ko chu jaati hai,\nTumhari dosti chahiye mujhe।\nTum ho to life mein maza hai,\nTum nahi to kuch nahi।"""
]

# ============= HUMAN AI =============
async def get_owner_mention():
    try:
        if OWNER_ID == 0: return "KING"
        user = await app.get_users(OWNER_ID)
        return f"@{user.username}" if user.username else f"<a href='tg://user?id={OWNER_ID}'>KING</a>"
    except: return "KING"

async def human_reply(text, user_id):
    text = text.lower()
    reply = ""
    if "kya kar rahe" in text or "kya kar rhe": reply = random.choice(["bas baitha hu bhai", "kuch nahi, tu bol", "timepass kar raha"])
    elif "kaise ho" in text: reply = random.choice(["mast hu bhai tu bata", "badiya, tu suna", "ekdum jhakaas"])
    elif "owner" in text or "malik" in text: reply = f"मेरे KING 👑 - {await get_owner_mention()}"
    else: reply = recall(text) or random.choice(["hmm sahi hai", "acha fir?", "bol kya scene hai", "haan sun raha"])

    # FLIRT MODE CHECK
    if user_id in flirt_dms:
        flirt = random.choice(FLIRT_SHAYARI)
        reply = f"{reply}\n\n💘 <b>FLIRT:</b>\n{flirt}"
    return reply

async def safe_reply(chat_id, text, reply_to=None):
    try: await app.send_message(chat_id, text, reply_to_message_id=reply_to)
    except Exception as e: print(f"Reply Error: {e}")

# ============= FLASK =============
@flask_app.route('/')
def home(): return "KARTIK KING USERBOT IS ALIVE 👑"
def run_flask(): flask_app.run(host='0.0.0.0', port=8080)

# ============= PREMIUM MENU =============
@app.on_message(filters.me & filters.command("help", "."))
async def help_menu(_, m: Message):
    menu = """┏━━━━━━━━━━━━━━━━━━━━━━┓
┃ 👑 <b>KARTIK KING USERBOT v4</b> 👑 ┃
┗━━━━━━━━━━━━━━┛

<b>⚡ AI CONTROL ⚡</b>
<code>.autoai</code> » Group auto reply
<code>.dmai</code> » DM auto reply
<code>.flirt</code> » DM me Flirt Mode on/off

<b>💾 MEMORY</b>
<code>.teach sawal | jawab</code> » Bot ko sikhana

<b>🎉 WELCOME SYSTEM</b>
<code>.welon</code> » Premium welcome on
<code>.weloff</code> » Welcome off

<b>📢 TAG SYSTEM</b>
<code>.tagall msg</code> » Sabko tag
<code>.tagsh</code> » Sabko shayari tag

<b>💔 SHAYARI</b>
<code>.dard</code> <code>.love</code> <code>.attitude</code> <code>.sad</code>

<b>🔧 OTHER</b>
<code>.ping</code> » Bot check

┗━ Made by KING KARTIK ━┛"""
    await m.edit(menu)

@app.on_message(filters.me & filters.command("flirt", "."))
async def flirt_toggle(_, m: Message):
    if not m.chat.id > 0: await m.edit("Ye sirf DM me kaam karega"); return
    user_id = m.chat.id
    if user_id in flirt_dms: flirt_dms.remove(user_id); c.execute("DELETE FROM flirtdms WHERE user_id=?", (user_id,)); await m.edit("💔 <b>FLIRT MODE OFF</b>")
    else: flirt_dms.add(user_id); c.execute("INSERT OR IGNORE INTO flirtdms VALUES (?)", (user_id,)); await m.edit("💘 <b>FLIRT MODE ON</b>\nAb har reply ke sath flirt shayari jayegi")
    conn.commit()

@app.on_message(filters.me & filters.command("welon", "."))
async def wel_on(_, m: Message):
    wel_groups.add(m.chat.id); c.execute("INSERT OR IGNORE INTO welgroups VALUES (?)", (m.chat.id,)); conn.commit()
    await m.edit("✅ <b>PREMIUM WELCOME ON</b>")

@app.on_message(filters.me & filters.command("weloff", "."))
async def wel_off(_, m: Message):
    wel_groups.discard(m.chat.id); c.execute("DELETE FROM welgroups WHERE chat_id=?", (m.chat.id,)); conn.commit()
    await m.edit("❌ <b>WELCOME OFF</b>")

@app.on_message(filters.me & filters.command("autoai", "."))
async def toggle_ai(_, m: Message):
    chat_id = m.chat.id
    if chat_id in ai_groups: ai_groups.remove(chat_id); c.execute("DELETE FROM groups WHERE chat_id=?", (chat_id,)); await m.edit("❌ <b>GROUP AI OFF</b>")
    else: ai_groups.add(chat_id); c.execute("INSERT OR IGNORE INTO groups VALUES (?)", (chat_id,)); await m.edit("✅ <b>GROUP AI ON</b>")
    conn.commit()

@app.on_message(filters.me & filters.command("dmai", "."))
async def toggle_dm(_, m: Message):
    if not m.chat.id > 0: await m.edit("Ye DM me use karo"); return
    user_id = m.chat.id
    if user_id in ai_dms: ai_dms.remove(user_id); c.execute("DELETE FROM dms WHERE user_id=?", (user_id,)); await m.edit("❌ <b>DM AI OFF</b>")
    else: ai_dms.add(user_id); c.execute("INSERT OR IGNORE INTO dms VALUES (?)", (user_id,)); await m.edit("✅ <b>DM AI ON</b>")
    conn.commit()

@app.on_message(filters.me & filters.command(["dard","love","attitude","sad"], "."))
async def shayari(_, m: Message):
    cmd = m.command[0]
    sh = random.choice(eval(cmd.upper()+"_SHAYARI"))
    await m.edit(f"💌 <b>{cmd.upper()} SHAYARI</b> 💌\n\n{sh}")

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

# ============= PREMIUM WELCOME WITH DP =============
@app.on_chat_member_updated()
async def welcome(_, update):
    if update.chat.id not in wel_groups: return
    if update.new_chat_member and update.new_chat_member.status == ChatMemberStatus.MEMBER:
        user = update.new_chat_member.user
        if not user.is_bot:
            sh = random.choice(LOVE_SHAYARI)
            tag = f"<a href='tg://user?id={user.id}'>{user.first_name}</a>"
            bio = ""
            try:
                full = await app.get_chat(user.id)
                bio = f"\n<b>Bio:</b> {full.bio}" if full.bio else ""
            except: pass

            wel_msg = f"""┏━━━━━━━━━━━━━━━━━━━┓
┃ 👑 <b>WELCOME TO THE GROUP</b> 👑 ┃
┗━━━━━━━━━━━┛

<b>Name:</b> {tag}
<b>Username:</b> @{user.username if user.username else 'N/A'}
<b>ID:</b> <code>{user.id}</code>{bio}

💌 <b>LOVE SHAYARI FOR YOU:</b>
{sh}

┗━ Enjoy your stay KING 👑 ━┛"""
            try:
                photos = [p async for p in app.get_chat_photos(user.id, limit=1)]
                if photos:
                    await app.send_photo(update.chat.id, photos[0].file_id, caption=wel_msg)
                else:
                    await app.send_message(update.chat.id, wel_msg)
            except:
                await app.send_message(update.chat.id, wel_msg)

# ============= AUTO REPLY =============
@app.on_message(filters.group & ~filters.me)
async def group_ai(_, m: Message):
    try:
        if m.chat.id not in ai_groups: return
        if m.sticker: await asyncio.sleep(1); await m.reply_sticker(m.sticker.file_id); return
        if not m.text: return
        await asyncio.sleep(random.uniform(1.5, 3))
        reply = await human_reply(m.text, m.from_user.id)
        await safe_reply(m.chat.id, reply, m.id)
    except Exception as e: print(f"Group Error: {e}")

@app.on_message(filters.private & ~filters.me)
async def pm_ai(_, m: Message):
    try:
        if m.from_user.id not in ai_dms: return
        if m.sticker: await asyncio.sleep(1); await m.reply_sticker(m.sticker.file_id); return
        if not m.text: return
        await asyncio.sleep(random.uniform(1, 2.5))
        reply = await human_reply(m.text, m.from_user.id)
        await safe_reply(m.chat.id, reply, m.id)
    except Exception as e: print(f"PM Error: {e}")

# ============= START =============
if __name__ == "__main__":
    for row in c.execute("SELECT chat_id FROM groups"): ai_groups.add(row[0])
    for row in c.execute("SELECT user_id FROM dms"): ai_dms.add(row[0])
    for row in c.execute("SELECT user_id FROM flirtdms"): flirt_dms.add(row[0])
    for row in c.execute("SELECT chat_id FROM welgroups"): wel_groups.add(row[0])
    Thread(target=run_flask).start()
    print("👑 KARTIK KING USERBOT STARTED 👑")
    app.run()
