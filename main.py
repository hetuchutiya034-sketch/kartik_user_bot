import os
import asyncio
import random
from dotenv import load_dotenv
load_dotenv()

from pyrogram import Client, filters
from pyrogram.types import Message
import google.generativeai as genai

# ================= CONFIG =================
API_ID = int(os.getenv("API_ID", 0))
API_HASH = os.getenv("API_HASH")
SESSION = os.getenv("SESSION")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# DEBUG
print("="*30)
print("DEBUG: API_ID =", API_ID)
print("DEBUG: API_HASH mil rahi hai =", "HAAN" if API_HASH else "NAHI")
print("DEBUG: SESSION mil rahi hai =", "HAAN" if SESSION else "NAHI")
print("DEBUG: GEMINI_KEY mil rahi hai =", "HAAN" if GEMINI_API_KEY else "NAHI")
print("="*30)

if not API_ID or not API_HASH or not SESSION:
    print("❌ ERROR: API_ID, API_HASH, ya SESSION missing hai")
    exit()

# Gemini Config
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    model = None
    print("⚠️ WARNING: GEMINI_API_KEY nahi hai. AI reply kaam nahi karega")

app = Client(
    name="ishikauserbot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION
)

# ================= GLOBAL =================
ai_groups = {}
ai_mode = "normal"
user_memory = {}

# ================= AI MODES =================
MODES = {
    "normal": "You are a helpful Hinglish assistant. Reply in 2 lines max. Use emoji.",
    "savage": "You are savage roasting Hinglish AI. Reply short and funny.",
    "gf": "You are a sweet romantic girlfriend. Reply lovingly in Hinglish.",
    "funny": "You are funny meme-style AI. Reply with jokes and emojis."
}

# ================= SHAYARI DATABASE =================
LOVE = ["""तेरी आँखों में जो बात है, वो किसी और में कहाँ... तेरे बिना ये दिल, अब लगता नहीं यहाँ... ❤️"""]*15
SAD = ["""दिल टूटा है मगर आवाज़ नहीं, कोई समझे ऐसा अंदाज़ नहीं... 💔"""]*15
ATTITUDE = ["""हम वो नहीं जो डर जाएं, हम वो हैं जो टकराएं... 😈"""]*10
GF = ["""तू मेरी जान है, तू ही मेरी पहचान है... ❤️"""]*10
ALL = LOVE + SAD + ATTITUDE + GF

# ================= COMMANDS =================

@app.on_message(filters.me & filters.command("help", [".","/"]))
async def help_cmd(_, m):
    help_text = """**🤖 ISHIKA AI USERBOT - HELP**

**AI Commands**
`.autoai on/off` - Group me AI auto reply ON/OFF
`.aimode normal/savage/gf/funny` - AI ka mood change
`.resetai` - AI ki memory clear

**Shayari Commands**
`.shayari` - Random shayari
`.shayarilove` - Love shayari
`.shayarisad` - Sad shayari
`.shayariattitude` - Attitude shayari
`.shayarigf` - GF wali shayari

**Utility**
`.ping` - Bot check
`.help` - Ye menu

**AI Use:** Reply karke `bot` likho ya PM karo 🔥
"""
    await m.edit(help_text)

@app.on_message(filters.me & filters.command("ping", [".","/"]))
async def ping(_, m): await m.edit("🏓 PONG")

@app.on_message(filters.me & filters.command("autoai", [".","/"]) & filters.group)
async def autoai(_, m):
    cid = m.chat.id
    if len(m.command)<2: return await m.edit("Use: `.autoai on` ya `.autoai off`")
    ai_groups[cid] = m.command[1]=="on"
    status = "ON ✅" if ai_groups[cid] else "OFF ❌"
    await m.edit(f"🤖 **AI AUTO REPLY {status}**")

@app.on_message(filters.me & filters.command("aimode", [".","/"]))
async def mode(_, m):
    global ai_mode
    if len(m.command)<2: return await m.edit("Use: `.aimode normal/savage/gf/funny`")
    if m.command[1] in MODES:
        ai_mode = m.command[1]
        await m.edit(f"Mode changed to: **{ai_mode}** 🔥")
    else:
        await m.edit("Galat mode. Use: normal/savage/gf/funny")

@app.on_message(filters.me & filters.command("resetai", [".","/"]))
async def reset(_, m):
    user_memory.clear()
    await m.edit("Memory cleared ✅")

# ================= AI GEMINI =================
async def ai_reply(uid, text):
    if not model: return "AI Key nahi lagi hai 😅"

    system_prompt = MODES[ai_mode]
    full_prompt = f"{system_prompt}\n\nUser: {text}\nBot:"

    try:
        res = model.generate_content(full_prompt)
        reply = res.text
        return reply[:4000] # telegram limit
    except Exception as e:
        return f"AI error: {str(e)[:100]} 😅"

@app.on_message(filters.group & ~filters.me)
async def group_ai(_, m: Message):
    if not ai_groups.get(m.chat.id): return
    if not m.text: return
    if m.reply_to_message and m.reply_to_message.from_user.is_self or "bot" in m.text.lower():
        reply = await ai_reply(m.from_user.id, m.text)
        await m.reply_text(reply)

@app.on_message(filters.private & ~filters.me)
async def private_ai(_, m: Message):
    if m.text:
        reply = await ai_reply(m.from_user.id, m.text)
        await m.reply_text(reply)

# ================= SHAYARI COMMANDS =================
@app.on_message(filters.me & filters.command("shayari", [".","/"]))
async def shayari(_, m): await m.edit(random.choice(ALL))
@app.on_message(filters.me & filters.command("shayarilove", [".","/"]))
async def love(_, m): await m.edit(random.choice(LOVE))
@app.on_message(filters.me & filters.command("shayarisad", [".","/"]))
async def sad(_, m): await m.edit(random.choice(SAD))
@app.on_message(filters.me & filters.command("shayariattitude", [".","/"]))
async def att(_, m): await m.edit(random.choice(ATTITUDE))
@app.on_message(filters.me & filters.command("shayarigf", [".","/"]))
async def gf(_, m): await m.edit(random.choice(GF))

# ================= START =================
print("🔥 FULL AI USERBOT STARTED WITH GEMINI 🔥")
app.run()
