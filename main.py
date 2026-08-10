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

# ================= 160 SHAYARI DATABASE - 8 LINE LAMBI =================
LOVE = [
"""तेरी आँखों की गहराई में खो जाने का दिल करता है, तेरे लबों की मुस्कान में सिमट जाने का दिल करता है,
तेरे नाम की माला जपते जपते रात गुजर जाती है, तेरे ख्यालों में खोकर हर सुबह नई लगती है,
तेरे बिना ये दुनिया वीरान सी लगती है, तेरे साथ हर लम्हा जन्नत सा लगता है,
तू मिल जाए तो मुकम्मल हो जाए ये ज़िंदगी, तू ही मेरी मोहब्बत, तू ही मेरी इबादत है ❤️""",

"""चाहत की इस बारिश में भीगना है सिर्फ तुझसे, इश्क की इस आग में जलना है सिर्फ तुझसे,
तेरे लफ्ज़ों में सुकून मिलता है, तेरी आवाज़ में सुकून मिलता है,
हर सांस में तेरा नाम आता है, हर धड़कन तुझे ही पुकारती है,
तेरा हाथ थाम लूं तो मंजिल आसान लगती है, तू पास हो तो हर मुश्किल आसान लगती है,
तू मेरी पहली और आखिरी मोहब्बत है, तुझसे शुरू तुझपे खत्म है मेरी कहानी ❤️""",

"""दिल कहता है तुमसे घंटों बातें करूं, लब कहते हैं तुम्हारा नाम लेकर जिक्र करूं,
रात भर तेरी यादों में खोया रहता हूं, नींद आए तो ख्वाबों में तुझे पाता हूं,
तू पास हो तो वक्त ठहर सा जाता है, तू दूर हो तो दिल घबरा सा जाता है,
तेरे बगैर जीने का ख्याल भी रुला देता है, तू मेरी ज़िंदगी है तू मेरी दुनिया है ❤️""",

"""तेरा साथ हो तो हर गम भी हंसी लगता है, तेरा प्यार हो तो हर दिन दिवाली लगता है,
तेरे बिना ये चांद भी फीका फीका लगता है, तेरे बिना ये सितारे भी उदास उदास लगते हैं,
तेरी एक झलक के लिए सुबह से शाम कर देता हूं, तेरी एक आवाज़ के लिए दुनिया भुला देता हूं,
लोग पूछते हैं इतना प्यार क्यों करता है, मैं कहता हूं वो मेरी जान है इसलिए करता हूं ❤️""",
] + [f"""तेरी यादों के सहारे दिन कट जाता है, तेरे इंतजार में रात गुजर जाती है,
तेरे बिना चैन नहीं आता है, तेरे बिना सुकून नहीं आता है,
तू हंस दे तो मेरी दुनिया हंसती है, तू रो दे तो मेरी आंखें भर आती हैं,
तू मेरी धड़कन है तू मेरी सांस है, तुझसे ही मेरी पहचान है मेरी जान ❤️""" for i in range(5,41)]

SAD = [
"""रात भर जाग कर तेरे बारे में सोचा बहुत, तेरे बिना जीना कितना मुश्किल है ये जाना बहुत,
जिन्हें अपना कहा था वो सब पराए निकले, जिन पर जान लुटाई वो बेगाने निकले,
दिल के टुकड़े करके लोग तमाशा देखते हैं, मेरे जख्मों पर नमक छिड़क कर खुश होते हैं,
अब किसी से उम्मीद नहीं रही, तेरे बाद मोहब्बत से नफरत हो गई है 💔""",

"""कभी हम साथ में घंटों बातें किया करते थे, कभी हम एक दूसरे के बिना रह नहीं पाते थे,
आज वही हम एक दूसरे से बात करना गवारा नहीं करते, आज वही हम एक दूसरे को देखना पसंद नहीं करते,
वक्त ने ऐसा पलटा खाया कि सब बदल गया, प्यार कम हुआ या लोगों की नज़र लग गई,
तेरी यादें अब भी आकर रुला जाती हैं, तेरी बातें अब भी दिल को तड़पा जाती हैं 💔""",

"""तन्हाई का आलम पूछोगे तो बता नहीं पाऊंगा, दिल का हाल पूछोगे तो सुना नहीं पाऊंगा,
तेरे जाने के बाद से सांस लेना भी अज़ाब लगता है, तेरे बगैर जीना भी गुनाह लगता है,
लोग पूछते हैं क्या हुआ क्यों उदास रहते हो, मैं हंस कर कह देता हूं कुछ नहीं बस ऐसे ही,
अंदर से टूट चुका हूं पर बाहर से मुस्कुराता हूं, ये दर्द किसी को दिखा नहीं पाता हूं 💔""",

"""वादा किया था साथ निभाने का, कसम खाई थी कभी ना छोड़ने की,
आज वही वादे झूठे निकले, आज वही कसमें खोखली निकलीं,
तू चला गया मुझे अकेला छोड़कर, मैं रह गया तेरी यादों के सहारे,
लोग कहते हैं भूल जा उसे, मैं कैसे भूलूं जान उसी में बसती है 💔""",
] + [f"""तेरे जाने के बाद से हर चीज बदल गई, तेरे जाने के बाद से मैं बदल गया,
पहले हंसता था अब रोता रहता हूं, पहले मिलता था अब तरसता रहता हूं,
तेरी फोटो देखकर दिन गुजारता हूं, तेरी पुरानी चैट पढ़कर रात गुजारता हूं,
काश तू लौट आए एक बार, काश तू समझ जाए मेरा प्यार 💔""" for i in range(5,41)]

ATTITUDE = [
"""हम वो नहीं जो गिर कर संभल ना सकें, हम वो हैं जो गिर कर भी तूफान बन जाएं,
दुश्मनी करनी है तो सामने से करो, पीठ पीछे वार करने वालों से हम बात नहीं करते,
शेर को सोता हुआ देखकर कमजोर मत समझना, जिस दिन जाग गया उस दिन तहलका मच जाएगा,
नाम सुनकर फ्लावर समझे क्या, हम फायर हैं फायर, जल जाओगे पास आओगे तो 😈""",

"""तेवर हमारा बादशाहों वाला है इसलिए लोग जलते हैं, अंदाज़ हमारा नवाबों वाला है इसलिए लोग डरते हैं,
झुकना हमें आता नहीं और रुकना हमें पसंद नहीं, जिस रास्ते पर चल पड़ते हैं इतिहास बना देते हैं,
इज्जत करते हैं इसलिए शरीफ हैं, वरना हम भी कम नहीं हैं,
दोस्ती निभाएं तो जान दे दें, दुश्मनी करें तो जहान हिला दें 😈""",

"""जिन्हें लगता है हम अकेले हैं, उन्हें बता दो हम अकेले नहीं नवाब हैं,
भीड़ के पीछे चलने का शौक नहीं, अपना रास्ता खुद बनाने का शौक है,
गलत को गलत कहने की हिम्मत रखते हैं, सच के लिए दुनिया से लड़ने की हिम्मत रखते हैं,
हम जैसे हैं लाजवाब हैं, हमारी कॉपी करने वाले नाकामयाब हैं 😈""",

"""समय समय की बात है, आज तुम्हारा कल हमारा होगा,
जो आज हमें गिराने चले हैं, कल वही हमें उठाने आएंगे,
हम हार मानने वालों में से नहीं, हम ठोकर खाकर भी आगे बढ़ने वालों में से हैं,
तारीफ करनी है तो सामने करो, बुराई करनी है तो पीठ पीछे करो 😈""",
] + [f"""हमारा अंदाज़ ही अलग है, हमारा स्वैग ही अलग है,
भीड़ में रहकर भी सबसे अलग दिखते हैं, तूफान में भी मुस्कुराते रहते हैं,
दुश्मन भी तारीफ करें ऐसा काम करते हैं, दोस्त भी फक्र करें ऐसा नाम करते हैं,
टक्कर में आने से पहले सोच लेना, हम वो नहीं जो आसानी से हार मान जाएं 😈""" for i in range(5,41)]

GF = [
"""तू मेरी जान है तू मेरी पहचान है, तेरे बिना ये दिल वीरान है,
तेरी एक कॉल के लिए दिन भर तरसता हूं, तेरे एक मैसेज के लिए पल पल तड़पता हूं,
तू रूठ जाए तो मेरी दुनिया रूठी लगती है, तू हंस दे तो मेरी दुनिया हंसती लगती है,
प्रॉमिस करता हूं कभी तुझे रुलाऊंगा नहीं, बस तू मेरा साथ कभी मत छोड़ना मेरी जान ❤️""",

"""तू मेरी सुबह है तू मेरी शाम है, तू ही मेरी धड़कन तू ही मेरा नाम है,
लोग पूछते हैं इतना प्यार क्यों करता है, मैं कहता हूं वो मेरी ज़िंदगी है इसलिए करता हूं,
तू साथ हो तो हर मुश्किल आसान लगती है, तू दूर हो तो हर खुशी बेकार लगती है,
I Love You सोना, I Love You जान, तुझसे ही मेरी दुनिया तुझसे ही मेरी पहचान ❤️""",

"""तेरी आंखों में अपना घर देखता हूं, तेरे बालों में अपनी दुनिया देखता हूं,
तेरे हाथों में अपना कल देखता हूं, तेरे कंधे पर अपना आज देखता हूं,
लोग प्यार को टाइमपास कहते हैं, मैं प्यार को इबादत कहता हूं,
तू मिल गई तो मुकम्मल हो गई ज़िंदगी, तू मिल गई तो जन्नत मिल गई ❤️""",

"""सुबह उठकर सबसे पहले तेरा चेहरा याद आता है, रात सोने से पहले आखिरी ख्याल तेरा आता है,
तेरी एक झलक के लिए दिन भर इंतजार करता हूं, तेरी एक आवाज़ के लिए सब कुछ कुर्बान करता हूं,
तू नाराज़ हो जाए तो चैन नहीं आता, तू मान जाए तो जान में जान आती है,
तू मेरी हो और हमेशा मेरी ही रहना, ये वादा है मेरा तुमसे मेरी जान ❤️""",
] + [f"""तू मेरी खुशी है तू मेरा गम है, तू मेरी हंसी है तू मेरा आंसू है,
तेरे बिना एक पल भी रह नहीं सकता, तेरे बिना एक सांस भी ले नहीं सकता,
तू साथ दे तो दुनिया से लड़ जाऊं, तू साथ दे तो पहाड़ भी हिला दूं,
बस तू मेरा हाथ थाम ले और कभी मत छोड़ना, I Love You मेरी जान ❤️""" for i in range(5,41)]

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
