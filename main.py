import os
import sys
import random
import time
import threading
import asyncio
import aiohttp
from dotenv import load_dotenv
load_dotenv()

from pyrogram import Client, filters
from pyrogram.types import Message
from groq import Groq

# ================= CONFIG =================
API_ID = int(os.getenv("API_ID", 0))
API_HASH = os.getenv("API_HASH")
SESSION = os.getenv("SESSION")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OWNER_ID = int(os.getenv("OWNER_ID", 0))

print("="*30)
print("DEBUG: GROQ_KEY =", "MIL GAYI" if GROQ_API_KEY else "NAHI HAI")
print("="*30)

if not API_ID or not API_HASH or not SESSION:
    exit("❌ ERROR: API_ID, API_HASH, ya SESSION missing hai")

client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
app = Client(name="ishikauserbot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION)

# ================= DATA ANDAR HI HAI =================
DATA = {
  "shayari": {
    "all": [
      "Tere naam se mohabbat ki hai, tere ehsaas se ishq kiya hai",
      "Dil kehta hai tu mil jaaye, duniya ki har khushi mil jaaye",
      "Chand bhi sharma jaye teri ada se, itni khoobsurat tu hai"
    ],
    "love": [
      "Tum pass ho to har dard dawa lagta hai",
      "Teri ek jhalak ke liye dil bechain rehta hai",
      "Ishq tumse hai, baaki sab se matlab nahi"
    ],
    "sad": [
      "Tum bin zindagi adhoori lagti hai",
      "Jo apne the wo bhi ab paraye lagte hain",
      "Dil toota hai par shor nahi karte"
    ],
    "attitude": [
      "Mera attitude mera style hai, pasand aaye to theek warna bhad me jao",
      "Main wahi hu jisko log copy karte hain",
      "Tere jaise hazar aaye aur gaye"
    ]
  },
  "roast": {
    "all": ["battery 1% attitude 100%", "Google bhi tujhe search karke thak gaya", "Tere muh se gyan mat pel"],
    "funny": ["tu wifi hai kya signal nahi aate", "Form bharne gaya tha, form ne mujhe bhar diya"]
  }
}

SHAYARI_DATA = DATA["shayari"]
ROAST_DATA = DATA["roast"]

# ================= GLOBAL =================
ai_groups = {}
ai_mode = "normal"
afk_status = False
afk_reason = ""

MODES = {
    "normal": "You are a helpful Hinglish assistant. Reply in 2 lines max. Use emoji.",
    "savage": "You are savage roasting Hinglish AI. Reply short and funny.",
    "gf": "You are a sweet romantic girlfriend. Reply lovingly in Hinglish.",
    "funny": "You are funny meme-style AI. Reply with jokes and emojis."
}

# ================= AI FUNCTION =================
async def ai_reply(text):
    if not client: return "GROQ_API_KEY nahi lagi hai 😅"
    system_prompt = MODES[ai_mode]
    full_prompt = f"{system_prompt}\n\nUser: {text}\nBot:"
    try:
        res = client.chat.completions.create(
            messages=[{"role": "user", "content": full_prompt}],
            model="llama-3.1-8b-instant",
            max_tokens=300
        )
        return res.choices[0].message.content[:4000]
    except Exception as e:
        return f"AI error: {str(e)[:100]} 😅"

# ================= COMMANDS =================
@app.on_message(filters.me & filters.command("help", [".","/"]))
async def help_cmd(_, m):
    help_text = """**🤖 ISHIKA AI USERBOT - RENDER FREE**\n
**AI Commands**
`.autoai on/off` - Group AI ON/OFF
`.aimode normal/savage/gf/funny` - AI Mood
`.ask <question>` - AI se pucho

**Fun + Utility**
`.ping.bio.info.coin.roast.afk.restart`

**Content**
`.shayari <category>`
`.anysnap` - Random anime pic
"""
    await m.edit(help_text)

@app.on_message(filters.me & filters.command("ping", [".","/"]))
async def ping(_, m): await m.edit("🏓 PONG - Web Service pe Zinda hu")

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
        await m.edit(f"Mode changed: **{ai_mode}** 🔥")
    else:
        await m.edit("Galat mode")

@app.on_message(filters.me & filters.command("ask", [".","/"]))
async def ask(_, m):
    if len(m.command) < 2: return await m.edit("Use: `.ask ye code kya karta hai`")
    q = " ".join(m.command[1:])
    msg = await m.edit("🤔 Soch raha...")
    await msg.edit(await ai_reply(q))

@app.on_message(filters.me & filters.command("roast", [".","/"]))
async def roast(_, m):
    if not m.reply_to_message:
        return await m.edit("Kisi ke msg ko reply karke `.roast` karo")
    category = m.command[1] if len(m.command) > 1 else "all"
    data = ROAST_DATA.get(category, ROAST_DATA.get("all"))
    await m.edit(f"**{m.reply_to_message.from_user.first_name}**\n{random.choice(data)}")

@app.on_message(filters.me & filters.command("coin", [".","/"]))
async def coin(_, m):
    await m.edit(f"🪙 Result: **{random.choice(['HEADS','TAILS'])}**")

@app.on_message(filters.me & filters.command("bio", [".","/"]))
async def bio(_, m):
    user = m.reply_to_message.from_user if m.reply_to_message else m.from_user
    await m.edit(f"**Name:** {user.first_name}\n**Username:** @{user.username}\n**ID:** `{user.id}`")

@app.on_message(filters.me & filters.command("info", [".","/"]))
async def info(_, m):
    chat = await app.get_chat(m.chat.id)
    await m.edit(f"**Group:** {chat.title}\n**Members:** {chat.members_count}\n**ID:** `{chat.id}`")

@app.on_message(filters.me & filters.command("afk", [".","/"]))
async def afk(_, m):
    global afk_status, afk_reason
    afk_status = True
    afk_reason = " ".join(m.command[1:]) if len(m.command) > 1 else "AFK"
    await m.edit(f"💤 **AFK ON**\nReason: {afk_reason}")

@app.on_message(filters.me & filters.command("restart", [".","/"]))
async def restart(_, m):
    await m.edit("♻️ Restarting...")
    os.execl(sys.executable, sys.executable, *sys.argv)

# ============ ANYSNAP COMMAND ============
ANIME_APIS = [
    "https://api.waifu.pics/sfw/waifu",
    "https://api.waifu.pics/sfw/neko",
    "https://api.waifu.pics/sfw/shinobu",
    "https://api.waifu.pics/sfw/megumin",
    "https://api.waifu.pics/sfw/cuddle"
]

@app.on_message(filters.me & filters.command("anysnap", [".","/"]))
async def anysnap(_, m):
    msg = await m.edit("🎌 Loading random anime pic...")
    try:
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            url = random.choice(ANIME_APIS)
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    img_url = data.get("url")
                    await msg.delete()
                    await app.send_photo(m.chat.id, img_url, caption="🎌 **AnySnap**")
                else:
                    await msg.edit("API down hai bhai, baad me try kar")
    except Exception as e:
        await msg.edit(f"Error: {str(e)[:100]}")

# ============ SHAYARI COMMAND ============
@app.on_message(filters.me & filters.command("shayari", [".","/"]))
async def shayari(_, m):
    category = m.command[1] if len(m.command) > 1 else "all"
    data = SHAYARI_DATA.get(category, SHAYARI_DATA.get("all"))
    await m.edit(random.choice(data))

# ================= AI AUTO REPLY =================
@app.on_message(filters.group & ~filters.me)
async def group_ai(_, m: Message):
    global afk_status
    me = await app.get_me()

    if afk_status and m.reply_to_message and m.reply_to_message.from_user.id == OWNER_ID:
        await m.reply(f"💤 Me AFK hu: {afk_reason}")
        afk_status = False
        return

    if not ai_groups.get(m.chat.id): return
    if not m.text: return

    is_reply_to_me = m.reply_to_message and m.reply_to_message.from_user.id == OWNER_ID
    is_tag = f"@{me.username.lower()}" in m.text.lower()

    if is_reply_to_me or is_tag:
        await m.reply_text(await ai_reply(m.text))

@app.on_message(filters.private & ~filters.me)
async def private_ai(_, m: Message):
    if m.text:
        await m.reply_text(await ai_reply(m.text))

# ================= START =================
if __name__ == "__main__":
    print("🔥 ISHIKA AI USERBOT RAILWAY PE STARTED 🔥")
    app.run()
