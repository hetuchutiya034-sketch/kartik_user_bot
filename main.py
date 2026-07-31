import os
import asyncio
import random
from dotenv import load_dotenv
load_dotenv()

from pyrogram import Client, filters
from pyrogram.types import Message
from openai import OpenAI

# ================= CONFIG =================
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION = os.getenv("SESSION")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

app = Client("ishikauserbot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION)
client_ai = OpenAI(api_key=OPENAI_API_KEY)

# ================= GLOBAL =================
ai_groups = {}
ai_mode = "normal"
user_memory = {}

# ================= AI MODES =================
MODES = {
    "normal": "You are a helpful Hinglish assistant.",
    "savage": "You are savage roasting Hinglish AI.",
    "gf": "You are a sweet romantic girlfriend.",
    "funny": "You are funny meme-style AI."
}

# ================= SHAYARI DATABASE =================

LOVE = [
"""तेरी आँखों में जो बात है,
वो किसी और में कहाँ...
तेरे बिना ये दिल,
अब लगता नहीं यहाँ...
तेरी मुस्कान मेरी जान है,
तेरी हर बात पहचान है...
बस तू ही मेरी दुनिया है ❤️""",
]*15

SAD = [
"""दिल टूटा है मगर आवाज़ नहीं,
कोई समझे ऐसा अंदाज़ नहीं...
रोते हैं अंदर ही अंदर हम,
पर बाहर कोई राज़ नहीं...
वो छोड़ गया हमें यूँ ही,
अब जीना भी सज़ा है 💔""",
]*15

ATTITUDE = [
"""हम वो नहीं जो डर जाएं,
हम वो हैं जो टकराएं...
दुनिया से क्या डरना हमें,
हम खुद आग बन जाएं...
जो जलते हैं हमसे,
उन्हें जलने दो 😈""",
]*10

GF = [
"""तू मेरी जान है,
तू ही मेरी पहचान है...
तेरे बिना ये दिल,
जैसे वीरान है...
तू हंसे तो दिन बन जाए,
तू रोए तो दिल टूट जाए ❤️""",
]*10

ALL = LOVE + SAD + ATTITUDE + GF

# ================= COMMANDS =================

@app.on_message(filters.me & filters.command("ping", [".","/"]))
async def ping(_, m): await m.edit("🏓 PONG")

@app.on_message(filters.me & filters.command("autoai", [".","/"]) & filters.group)
async def autoai(_, m):
    cid = m.chat.id
    if len(m.command)<2: return await m.edit("Use: .autoai on/off")
    ai_groups[cid] = m.command[1]=="on"
    await m.edit(f"AI {'ON' if ai_groups[cid] else 'OFF'}")

@app.on_message(filters.me & filters.command("aimode", [".","/"]))
async def mode(_, m):
    global ai_mode
    ai_mode = m.command[1]
    await m.edit(f"Mode: {ai_mode}")

@app.on_message(filters.me & filters.command("resetai", [".","/"]))
async def reset(_, m):
    user_memory.clear()
    await m.edit("Memory cleared")

# ================= AI =================

async def ai_reply(uid, text):
    hist = user_memory.get(uid, [])
    msgs = [{"role":"system","content":MODES[ai_mode]}] + hist[-5:]
    msgs.append({"role":"user","content":text})
    
    try:
        res = client_ai.chat.completions.create(
            model="gpt-4o-mini",
            messages=msgs
        )
        reply = res.choices[0].message.content
        hist += [{"role":"user","content":text},{"role":"assistant","content":reply}]
        user_memory[uid]=hist
        return reply
    except:
        return "AI error 😅"

@app.on_message(filters.group & ~filters.me)
async def group_ai(_, m):
    if not ai_groups.get(m.chat.id): return
    if not m.text: return
    if "bot" in m.text.lower() or m.reply_to_message:
        await m.reply_text(await ai_reply(m.from_user.id, m.text))

@app.on_message(filters.private & ~filters.me)
async def private_ai(_, m):
    if m.text:
        await m.reply_text(await ai_reply(m.from_user.id, m.text))

# ================= SHAYARI COMMANDS =================

@app.on_message(filters.me & filters.command("shayari", [".","/"]))
async def shayari(_, m):
    await m.edit(random.choice(ALL))

@app.on_message(filters.me & filters.command("shayarilove", [".","/"]))
async def love(_, m):
    await m.edit(random.choice(LOVE))

@app.on_message(filters.me & filters.command("shayarisad", [".","/"]))
async def sad(_, m):
    await m.edit(random.choice(SAD))

@app.on_message(filters.me & filters.command("shayariattitude", [".","/"]))
async def att(_, m):
    await m.edit(random.choice(ATTITUDE))

@app.on_message(filters.me & filters.command("shayarigf", [".","/"]))
async def gf(_, m):
    await m.edit(random.choice(GF))

# ================= START =================
print("🔥 FULL AI USERBOT STARTED 🔥")
app.run()
