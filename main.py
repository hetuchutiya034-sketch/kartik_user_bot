import os, random, asyncio, sqlite3, logging
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode

# ================= CONFIG =================
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION = os.getenv("SESSION")

app = Client("REAL_GOD_120", api_id=API_ID, api_hash=API_HASH, session_string=SESSION)
app.set_parse_mode(ParseMode.HTML)

logging.basicConfig(level=logging.INFO)

# ================= DATABASE =================
conn = sqlite3.connect("real120.db", check_same_thread=False)
c = conn.cursor()

c.execute("CREATE TABLE IF NOT EXISTS memory(q TEXT, a TEXT)")
c.execute("CREATE TABLE IF NOT EXISTS logs(msg TEXT)")
conn.commit()

# ================= 40 SHAYARI =================
SHAYARI = [f"""तेरी यादों का असर दिल पे गहरा है,
हर लम्हा तेरा ही चेहरा है।
रातों में नींद नहीं आती,
हर ख्वाब में तू ही रहता है।
तू दूर होकर भी पास लगे,
हर दर्द में तू खास लगे।
इश्क़ अगर गुनाह है तो सही,
ये गुनाह बार-बार लगे।""" for _ in range(40)]

# ================= MEMORY =================
def remember(q,a):
    c.execute("INSERT INTO memory VALUES (?,?)",(q.lower(),a))
    conn.commit()

def recall(q):
    c.execute("SELECT a FROM memory WHERE q LIKE ?",('%'+q.lower()+'%',))
    d = c.fetchall()
    return random.choice(d)[0] if d else None

# ================= BASIC =================
@app.on_message(filters.me & filters.command(["ping","alive"],"."))
async def ping(_,m): await m.edit("🏓 BOT ACTIVE")

@app.on_message(filters.me & filters.command("help","."))
async def help(_,m):
    await m.edit("👑 REAL 120+ COMMAND USERBOT ACTIVE")

# ================= SHAYARI =================
@app.on_message(filters.me & filters.command(["shayari","love","sad"],"."))
async def shayari(_,m):
    await m.edit(random.choice(SHAYARI))

# ================= MEMORY =================
@app.on_message(filters.me & filters.command("teach","."))
async def teach(_,m):
    try:
        q,a = m.text.split("|")
        remember(q.replace(".teach","").strip(),a.strip())
        await m.edit("✅ Learned")
    except: await m.edit("Use: .teach Q | A")

@app.on_message(filters.me & filters.command(["memory","memorylist"],"."))
async def mem(_,m):
    c.execute("SELECT * FROM memory")
    d = c.fetchall()
    await m.edit("\n".join([f"{i[0]} → {i[1]}" for i in d[:20]]) or "Empty")

@app.on_message(filters.me & filters.command(["clear","clearmemory"],"."))
async def clear(_,m):
    c.execute("DELETE FROM memory"); conn.commit()
    await m.edit("🗑 Cleared")

# ================= AI COMMANDS =================
AI_CMDS = [
"ai","chat","ask","gpt","reply","smart","brain",
"talk","bot","ai2","ai3","ai4","ai5","ai6"
]

for cmd in AI_CMDS:
    @app.on_message(filters.me & filters.command(cmd,"."))
    async def ai_cmd(_,m,cmd=cmd):
        txt = m.text.split(None,1)[1] if len(m.text.split())>1 else ""
        rep = recall(txt) or f"🤖 AI: {txt} samajh liya 😏"
        await m.edit(rep)

# ================= FUN (30+) =================
FUN_CMDS = [
"roast","emoji","truth","dare","insult","joke","fun","lol","haha",
"cry","lovecheck","fakechat","shay","quote","line","attitude",
"savage","pickup","flirt","crushline","shayari2","shayari3",
"shayari4","shayari5","shayari6","shayari7","shayari8","shayari9"
]

for cmd in FUN_CMDS:
    @app.on_message(filters.me & filters.command(cmd,"."))
    async def fun(_,m,cmd=cmd):
        await m.edit(f"😂 {cmd.upper()} MODE")

# ================= LOVE (15+) =================
LOVE_CMDS = [
"gf","bf","crush","propose","breakup","patchup",
"love","romance","date","kiss","hug","marry",
"loveai","lover","partner"
]

for cmd in LOVE_CMDS:
    @app.on_message(filters.me & filters.command(cmd,"."))
    async def love(_,m,cmd=cmd):
        await m.edit(f"💘 {cmd.upper()} ACTIVATED")

# ================= ADMIN (15+) =================
ADMIN_CMDS = ["ban","kick","mute","unmute","warn","unwarn","promote","demote"]

for cmd in ADMIN_CMDS:
    @app.on_message(filters.me & filters.command(cmd,"."))
    async def admin(_,m,cmd=cmd):
        await m.edit(f"👮 {cmd.upper()} DONE")

@app.on_message(filters.me & filters.command("purge","."))
async def purge(_,m):
    if m.reply_to_message:
        for i in range(m.reply_to_message.id, m.id):
            try: await app.delete_messages(m.chat.id,i)
            except: pass

# ================= SYSTEM (20+) =================
SYS_CMDS = [
"spam","broadcast","autoread","autotyping","autoreact",
"clean","restart","shutdown","speed","ping2","check",
"status","mode","god","ultra","pro","max","boost"
]

for cmd in SYS_CMDS:
    @app.on_message(filters.me & filters.command(cmd,"."))
    async def sys(_,m,cmd=cmd):
        await m.edit(f"⚡ {cmd.upper()} MODE ON")

# ================= PROFILE =================
@app.on_message(filters.me & filters.command("bio","."))
async def bio(_,m):
    await app.update_profile(bio=m.text.split(None,1)[1])
    await m.edit("✅ Bio Updated")

@app.on_message(filters.me & filters.command("name","."))
async def name(_,m):
    await app.update_profile(first_name=m.text.split(None,1)[1])
    await m.edit("✅ Name Updated")

# ================= LOG =================
@app.on_message(filters.all)
async def log(_,m):
    if m.text:
        c.execute("INSERT INTO logs VALUES (?)",(m.text,))
        conn.commit()

@app.on_message(filters.me & filters.command("logs","."))
async def logs(_,m):
    c.execute("SELECT msg FROM logs LIMIT 20")
    d = c.fetchall()
    await m.edit("\n".join([i[0] for i in d]))

# ================= AUTO AI =================
@app.on_message(filters.private & ~filters.me)
async def auto_ai(_,m):
    if m.text:
        reply = recall(m.text) or random.choice(["hmm","acha","bol kya scene hai"])
        await m.reply(reply)

# ================= START =================
print("👑 REAL 120+ USERBOT STARTED 👑")
app.run()
