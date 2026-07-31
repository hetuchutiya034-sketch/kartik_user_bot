import os
import asyncio
import random
from dotenv import load_dotenv
load_dotenv()

from pyrogram import Client, filters
from pyrogram.types import Message
from openai import OpenAI

# ================= CONFIG =================
API_ID = int(os.getenv("API_ID", 0))
API_HASH = os.getenv("API_HASH")
SESSION = os.getenv("SESSION")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Check karo key hai ya nahi
if not OPENAI_API_KEY:
    print("❌ ERROR: OPENAI_API_KEY nahi mili. Railway Variables me dalo")
    exit()

app = Client("ishikauserbot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION)
client_ai = OpenAI(api_key=OPENAI_API_KEY)

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
@app.on_message(filters.me & filters.command("ping", [".","/"]))
async def ping(_, m): await m.edit("🏓 PONG")

@app.on_message(filters.me & filters.command("autoai", [".","/"]) & filters.group)
async def autoai(_, m):
    cid = m.chat.id
    if len(m.command)<2: return await m.edit("Use:.autoai on/off")
    ai_groups[cid] = m.command[1]=="on"
    status = "ON ✅" if ai_groups[cid] else "OFF ❌"
    await m.edit(f"AI {status}")

@app.on_message(filters.me & filters.command("aimode", [".","/"]))
async def mode(_, m):
    global ai_mode
    if len(m.command)<2: return await m.edit("Use:.aimode normal/savage/gf/funny")
    if m.command[1] in MODES:
        ai_mode = m.command[1]
        await m.edit(f"Mode changed to: **{ai_mode}**")
    else:
        await m.edit("Mode nahi mila. Use: normal/savage/gf/funny")

@app.on_message(filters.me & filters.command("resetai", [".","/"]))
async def reset(_, m):
    user_memory.clear()
    await m.edit("Memory cleared ✅")

# ================= AI =================
async def ai_reply(uid, text):
    hist = user_memory.get(uid, [])
    msgs = [{"role":"system","content":MODES[ai_mode]}] + hist[-6:] # last 3 convo
    msgs.append({"role":"user","content":text})

    try:
        res = client_ai.chat.completions.create(
            model="gpt-4o-mini", # sasta wala model
            messages=msgs,
            max_tokens=150
        )
        reply = res.choices[0].message.content
        hist += [{"role":"user","content":text},{"role":"assistant","content":reply}]
        user_memory[uid]=hist[-10:] # memory ko zyada bada mat karo
        return reply
    except Exception as e:
        return f"AI error: {e} 😅"

@app.on_message(filters.group & ~filters.me)
async def group_ai(_, m):
    if not ai_groups.get(m.chat.id): return
    if not m.text: return
    # Sirf reply pe ya naam lene pe reply kare
    if m.reply_to_message or "bot" in m.text.lower():
        await m.reply_text(await ai_reply(m.from_user.id, m.text))

@app.on_message(filters.private & ~filters.me)
async def private_ai(_, m):
    if m.text:
        await m.reply_text(await ai_reply(m.from_user.id, m.text))

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
print("🔥 FULL AI USERBOT STARTED 🔥")
app.run()
