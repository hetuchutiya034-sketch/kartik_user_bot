from pyrogram import Client, filters
from pyrogram.types import Message, ChatPrivileges
from pyrogram.errors import FloodWait, ChatWriteForbidden
import asyncio, os, random, requests
from gtts import gTTS
import speech_recognition as sr
from googletrans import Translator
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import yt_dlp

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION = os.getenv("SESSION")

app = Client("ishikauserbot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION)
translator = Translator()
recognizer = sr.Recognizer()
tagging = False
tagsh_active = {} # tagsh ke liye
welcome_on = {}

# ============= DATA =============
SHAYARI_LIST = [
"मुझे वो पहली मुलाकात दे दो \nखुशनुमा वो फिर हालात दे दो....\n\nबात करते सो जाते थे \nफिर से मुझे वो अपनी रात दे दो...\n\nमैं उड़ती फिरती थी पूरा दिन \nफिर से मुझे वो मेरे जज़्बात दे दो....\nअब तुम बदल गए हो जाना\nफिर से मुझे वो पहली मुलाकात दे दो...!! ✍🏻❤💕🥺😥😞||",

"𝗬𝗲 𝗿𝗶𝘀𝘁𝗼𝗻 𝗸𝗲 𝘀𝗶𝗹𝘀𝗶𝗹𝗲 𝗶𝘁𝗻𝗲 𝗮𝗷𝗲𝗯 𝗸𝘆𝘂 𝗵𝗮𝗶\n𝗝𝗼 𝗻𝗮𝘀𝗶𝗯 𝗺𝗲 𝗻𝗵𝗶 𝘄𝗮𝗵𝗶 𝗱𝗶𝗹 𝗸𝗲 𝗸𝗮𝗿𝗶𝗯 𝗸𝘆𝘂 𝗵𝗮𝗶\n𝗡𝗮 𝗷𝗮𝗻𝗲 𝗸𝗮𝗶𝘀𝗲 𝗺𝗶𝗹 𝗷𝗮𝘁𝗶 𝗵𝗮𝗶 𝗹𝗼𝗴𝗼 𝗸𝗼 𝘂𝗻𝗸𝗶 𝗰𝗵𝗮𝗵𝗮𝘁\n𝗔𝗮𝗸𝗵𝗶𝗿 𝗸𝗶𝘀𝗲 𝗽𝘂𝗰𝗵𝗲𝗻 𝗸𝗶 𝗵𝘂𝗺 𝗶𝘁𝗻𝗲 𝗯𝗮𝗱𝗻𝗮𝘀𝗲𝗯 𝗸𝘆𝘂 𝗵𝗮𝗶 ||\n✍️ KARTIK ✍️",

"𝗧𝘂𝗺 𝗺𝘂𝗷𝗵𝗲 𝗰𝗵𝗼𝗿 𝗴𝘆𝗲 𝗸𝗼𝗶 𝗯𝗮𝘁 𝗻𝗵𝗶\n𝗔𝗽𝗻𝗲 𝘄𝗮𝗱𝗼𝗻 𝘀𝗲 𝗺𝘂𝗵 𝗺𝗼𝗱 𝗴𝘆𝗲 𝗸𝗼𝗶 𝗯𝗮𝘁 𝗻𝗵𝗶\n𝗠𝗲𝗿𝗮 𝗱𝗶𝗹 𝘁𝗼 𝘄𝗲𝘀𝗲 𝗵𝗶 𝗸𝗵𝗶𝗹𝗼𝗻𝗮 𝘁𝗵𝗮\n𝗲𝗸 𝗸𝗵𝗶𝗹𝗼𝗻𝗮 𝗵𝗶 𝘁𝗼𝗱 𝗴𝘆𝗲 𝗸𝗼𝗶 𝗯𝗮𝘁 𝗻𝗶 ||\n✍️ KARTIK ✍️",

"ʟᴏɢ ᴍɪʟ ᴊᴀᴛᴇ ʜᴀɪ ᴋᴀʜᴀɴɪ ʙᴀɴᴋᴀʀ\nᴅɪʟ ᴍᴇ ʙᴀs ᴊᴀᴛᴇ ʜᴀɪ ɴɪsʜᴀɴɪ ʙᴀɴᴋᴀʀ\nᴊɪɴʜᴇ ʜᴀᴍ ʀᴀᴋʜɴᴀ ᴄʜᴀʜᴛᴇ ʜᴀɪ ᴀᴘɴɪ ᴀᴀɴᴋʜᴏɴ ᴍᴇ \nᴋʏᴜ ɴɪᴋᴀʟ ᴊᴀᴛᴇ ʜᴀɪ ᴡᴏ ᴘᴀɴɪ ʙᴀɴᴋᴀʀ ||\n✍️ KARTIK ✍️",

"कहानी जिंदगी की यही है जनाब कि....!!!!\nइसमें मनचाहा किरदार नहीं मिलता....!!!!\n\nइन अल्फाजों से अपने आप को सलामत रखना \nजब कोई कहे न हमेशा तुम्हारा साथ हु।\nउसे एक सावल करना? कब तक?!\nकिसी ने मुझसे यही कहा था।\nआज जब उसे ढूंढा तो उसके अलावा सब मिला पर वो नहीं मिला ||",

"Wo khush hai parr Shayaad humse nahi,\nWo naraaz hai parr Shayaad humse nahi,\nKon kehta hai ki unke Dil mein mohabbat nahi,\nMohabbat hai parr Shayaad humse nahi ||",

"उसने सारी कुदरत को बुलाया होगा, फिर उसमें ममता का अक्स समाया होगा, \nकोशिश होगी परियों को जमीन पर लाने की, \nतब जाके खुदा ने बहनों को बनाया होगा ||",

"He Mohabbat use bhi he magar izhaar nahi karti \nab ye Kahna bhi to galat hai na ki vo mujhse pyar nhi karti \nMujhe khone ke dar se ki vah Meri hone se bhi darti hai \nVarna vo mere izhaar per Inkar nahin karti ||\n✍ KARTIK ✍",

"Tu zaruri hai har zarurat ko aazmaane ke baad...👈🏻🥀\nTu chalaana marzi apni mere marjane ke baad....!!\n\nHai sitam yeh bhi ke hum use chahte hai....🫶🏻🥹\nWoh bhi itna sitam dhaane ke baad...!!",

"Woh kitna khaas hai mere liye use batau kaise?\nMere dil me jo pyar hai uske liye woh jatau kaise?\nWoh rehta h koso dur mujh se, use dekh kr muskurau kaise?\nYeh pyar ek tarfa hi shi, pr pyar toh hai, bhul jau kaise?\nMain likhti hu bs usi ke liye pr usse sunau kaise?\nWoh rootha toh h pr kisi aur k liye main manana bhi chahu toh manau kaise || ✨",

"Mere dil ke dard ko kisne dekha haiii..\nMujhe Bus Khuda ne tadapte dekha hai..\nHum Tanhai mei baithe Rote hue...😌\nLogo ne Hume Mehfil mei Haste dekha hai.....🥀 ||",

"Mujhko sambhal aur khud bhi sambal \nMai nashe mein hu\nAaye jaan e jigar saath mai chal \nMai nashe mein hu\nOr akbar bhi mai saleem bhi mai hi shahjaha hu\nLakhon bana du taj mahal\nKyuki Mai nashe mein hu ||",

"Wo Dur Mujhse Kahi Hai Chalo Ji Ye Bhi Sahi\nHaan Hain or Bhi Husn Jamane Me\nPar Mujhe Pasand Sirf Vahi Hai ||",

"𝙳𝚒𝚕 𝚔𝚒 𝚋𝚊𝚝𝚎𝚒𝚗 💗:\nMere kandhe par Sir rakh kr us aasmaan ko dekh \nBilkul tere jaisa dikhta hai us chand ko dekh\nMujhe to hr ak cheez mai tera chehra nazar aata hai\nKabhi tu meri nazron se is jhaan ko dekh ||",

"Jiski ho jaisi ho chahe joh bhi ho tum \nMere liye toh meri ho bas meri ho tum\nSocha tha rounga gale se lipatkar tumare \nKhair yeh sab chordo aur batao Kaisi ho Tum ||",

"शोर बहुत है मगर सुनाई नही देगा!!\nदर्द दिल का चेहरे पर दिखाई नही देगा!!\nएक तुझसे बनाने के लिए मैंने बिगाड़ लि सबसे!!\nतो मेरे हक में भी कोई गवाही नहीं देगा ||",

"Ki kisi ki yaad me rona fizul h\nAur itne anmol ansu khona fizul h\nAur rona h to unke liye roo jo tum p nisar h\nUnke liye kya rona jinke ashique hazar h ||"
]

FLIRT = [
    "Tum haste ho to dil garden ho jata hai 😍",
    "Tum chai ho aur main biscuit, sath me mast lagte hai",
    "Teri ek jhalak dekhne ko dil taras jata hai"
]

WELCOMES = [
    "🔥 **WELCOME TO THE JUNGLE** 🔥\n\nHey [{name}](tg://user?id={id}) baby 😈\nItni sexy entry maari hai tune",
    "💎 **NEW DIAMOND ARRIVED** 💎\n\nWelcome {name} 😘\nTumhare aate hi group ki shaan badh gayi"
]

JOKES = [
    "Teacher: 2+2? Student: 5. Teacher: Galat. Student: Aapke hisab se 😂",
    "Doctor: Neend nahi aati? Patient: Nahi. Doctor: To so jao 😂"
]
MEMES = ["Jab crush online aaye", "Monday morning vibes", "Exam ke 1 din pehle"]

# ============= BASIC =============
@app.on_message(filters.me & filters.command("ping"))
async def ping(client, message: Message): await message.edit("🏓 Pong! Bot zinda hai")

@app.on_message(filters.me & filters.command("help"))
async def help(client, message: Message):
    text = """🔥 **ISHIKA USERBOT V1.6 ULTIMATE** 🔥

**Tag/Admin:** `/tagall` `/cancel` `/tagsh` `/stoptagsh` `/promote` `/demote` `/ban` `/unban` `/mute` `/unmute`
**Extra Admin:** `/kick` `/warn` `/zombies`
**Info:** `/id` `/info` `/purge`
**Broadcast:** `/broadcast` `/gcast` `/dcast`
**AI/Fun:** `/imagine` `/anime` `/couple` `/tts` `/shayari` `/flirt` `/joke` `/meme`
**New Tools:** `/insta` `/stt` `/tr` `/weather`
**Group:** `/welcome on/off`
**Session:** `/string`"""
    await message.edit(text)

@app.on_message(filters.me & filters.command("string"))
async def gen_string(client, message: Message):
    await message.edit(f"**String Session:**\n`{SESSION}`")

# ============= WELCOME =============
@app.on_message(filters.me & filters.command("welcome") & filters.group)
async def welcome_toggle(client, message: Message):
    global welcome_on
    if len(message.command) < 2: return await message.edit("Use: `/welcome on` or `/welcome off`")
    welcome_on[message.chat.id] = True if message.command[1] == "on" else False
    await message.edit(f"✅ Welcome {'ON' if welcome_on[message.chat.id] else 'OFF'}")

@app.on_message(filters.group & filters.new_chat_members)
async def welcome(client, message: Message):
    if not welcome_on.get(message.chat.id, True): return
    for user in message.new_chat_members:
        if not user.is_self:
            wel = random.choice(WELCOMES).format(name=user.first_name, id=user.id)
            await client.send_message(message.chat.id, wel)

# ============= AI & MEDIA =============
@app.on_message(filters.me & filters.command("imagine"))
async def imagine(client, message: Message):
    if len(message.command) < 2: return await message.edit("Use: /imagine beautiful girl")
    await message.edit("🎨 Image bana raha hu...")
    img = Image.new('RGB', (512, 512), (73, 109, 137)); ImageDraw.Draw(img).text((10,250), " ".join(message.command[1:])[:30], fill=(255,255,0))
    img.save("img.png"); await client.send_photo(message.chat.id, "img.png"); await message.delete(); os.remove("img.png")

@app.on_message(filters.me & filters.command("anime"))
async def anime_logo(client, message: Message):
    if len(message.command) < 2: return await message.edit("Use: /anime Ishika")
    await message.edit("🎨 Anime logo...")
    img = Image.open(BytesIO(requests.get("https://i.imgur.com/3Z3jW3Q.jpg").content)).resize((512,512))
    ImageDraw.Draw(img).text((256,400), " ".join(message.command[1:])[:12], fill=(255,50,150), anchor="mm")
    img.save("anime.png"); await client.send_photo(message.chat.id, "anime.png"); await message.delete(); os.remove("anime.png")

@app.on_message(filters.me & filters.command("couple"))
async def couple_logo(client, message: Message):
    if len(message.command) < 3: return await message.edit("Use: /couple boy girl")
    await message.edit("💑 Couple logo...")
    img = Image.open(BytesIO(requests.get("https://i.imgur.com/8QfZ3pL.jpg").content)).resize((512,512))
    ImageDraw.Draw(img).text((256,420), f"{message.command[1]} ❤️ {message.command[2]}", fill=(255,20,147), anchor="mm")
    img.save("couple.png"); await client.send_photo(message.chat.id, "couple.png"); await message.delete(); os.remove("couple.png")

@app.on_message(filters.me & filters.command("tts"))
async def tts_cmd(client, message: Message):
    if len(message.command) < 2: return await message.edit("Use: /tts hello")
    gTTS(" ".join(message.command[1:]), lang='hi').save("voice.ogg")
    await client.send_voice(message.chat.id, "voice.ogg"); await message.delete(); os.remove("voice.ogg")

# ============= NEW FILES =============
@app.on_message(filters.me & filters.command("shayari"))
async def shayari_unlimited(client, message: Message): await message.edit(random.choice(SHAYARI_LIST))

@app.on_message(filters.me & filters.command("flirt"))
async def flirt_cmd(client, message: Message): await message.edit(random.choice(FLIRT))

@app.on_message(filters.me & filters.command("insta"))
async def insta_dl(client, message: Message):
    if len(message.command) < 2: return await message.edit("Use: /insta reel_link")
    await message.edit("📥 Downloading...")
    with yt_dlp.YoutubeDL({'outtmpl': 'insta.%(ext)s'}) as ydl: ydl.download([message.command[1]])
    await client.send_video(message.chat.id, "insta.mp4"); await message.delete(); os.remove("insta.mp4")

@app.on_message(filters.me & filters.command("stt"))
async def stt(client, message: Message):
    if not message.reply_to_message or not message.reply_to_message.voice: return await message.edit("Reply to voice")
    file = await client.download_media(message.reply_to_message)
    with sr.AudioFile(file) as source: text = recognizer.recognize_google(recognizer.record(source), language="hi-IN")
    await message.edit(f"**Voice to Text:**\n{text}"); os.remove(file)

@app.on_message(filters.me & filters.command("tr"))
async def translate(client, message: Message):
    text = " ".join(message.command[1:]) if len(message.command) > 1 else message.reply_to_message.text
    result = translator.translate(text, dest='hi')
    await message.edit(f"**Hindi:** {result.text}")

@app.on_message(filters.me & filters.command("weather"))
async def weather(client, message: Message):
    if len(message.command) < 2: return await message.edit("Use: /weather Pune")
    await message.edit(f"🌤️ `{requests.get(f'https://wttr.in/{' '.join(message.command[1:])}?format=3').text}`")

@app.on_message(filters.me & filters.command("joke"))
async def joke(client, message: Message): await message.edit(random.choice(JOKES))

@app.on_message(filters.me & filters.command("meme"))
async def meme(client, message: Message): await message.edit(f"😂 **Meme:** {random.choice(MEMES)}")

# ============= ADMIN ALL =============
@app.on_message(filters.me & filters.command("tagall"))
async def tagall(client, message: Message):
    global tagging; tagging=True; msg=" ".join(message.command[1:]); await message.delete()
    for user in [m.user async for m in client.get_chat_members(message.chat.id) if m.user and not m.user.is_bot]:
        if not tagging: break
        await client.send_message(message.chat.id, f"[{user.first_name}](tg://user?id={user.id}) {msg}"); await asyncio.sleep(5)

@app.on_message(filters.me & filters.command("cancel"))
async def cancel_tag(client, message: Message): global tagging; tagging=False; await message.edit("Stopped")

# ============= TAGSH COMMAND NEW =============
@app.on_message(filters.me & filters.command("tagsh") & filters.group)
async def tagsh(client, message: Message):
    global tagsh_active
    chat_id = message.chat.id
    tagsh_active[chat_id] = True

    await message.edit("🚀 **TAGSH STARTED**\nHar member ko alag shayari ke sath tag kar raha hu...")

    shayari_copy = SHAYARI_LIST.copy()
    random.shuffle(shayari_copy)

    i = 0
    async for member in client.get_chat_members(chat_id):
        if not tagsh_active.get(chat_id):
            break
        if member.user and not member.user.is_bot and not member.user.is_deleted:
            shayari = shayari_copy[i % len(shayari_copy)]
            text = f"[{member.user.first_name}](tg://user?id={member.user.id})\n\n{shayari}"
            try:
                await client.send_message(chat_id, text)
                i += 1
                await asyncio.sleep(4)
            except FloodWait as e:
                await asyncio.sleep(e.value)
            except:
                pass

    tagsh_active[chat_id] = False
    await client.send_message(chat_id, "✅ **TAGSH COMPLETED**\nSabko tag kar diya")

@app.on_message(filters.me & filters.command("stoptagsh"))
async def stoptagsh(client, message: Message):
    global tagsh_active
    tagsh_active[message.chat.id] = False
    await message.edit("⛔ **TAGSH STOPPED**")

@app.on_message(filters.me & filters.command("promote"))
async def promote(client, message: Message):
    await client.promote_chat_member(message.chat.id, message.reply_to_message.from_user.id, privileges=ChatPrivileges(can_manage_chat=True,can_delete_messages=True,can_restrict_members=True,can_invite_users=True,can_pin_messages=True))
    await message.edit("✅ Promoted")

@app.on_message(filters.me & filters.command("demote"))
async def demote(client, message: Message):
    await client.promote_chat_member(message.chat.id, message.reply_to_message.from_user.id, privileges=ChatPrivileges())
    await message.edit("✅ Demoted")

@app.on_message(filters.me & filters.command("ban"))
async def ban(client, message: Message): await client.ban_chat_member(message.chat.id, message.reply_to_message.from_user.id); await message.edit("✅ Banned")
@app.on_message(filters.me & filters.command("unban"))
async def unban(client, message: Message): await client.unban_chat_member(message.chat.id, message.reply_to_message.from_user.id); await message.edit("✅ Unbanned")
@app.on_message(filters.me & filters.command("mute"))
async def mute(client, message: Message): await client.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id); await message.edit("🔇 Muted")
@app.on_message(filters.me & filters.command("unmute"))
async def unmute(client, message: Message): await client.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id, permissions=message.chat.permissions); await message.edit("🔊 Unmuted")

@app.on_message(filters.me & filters.command("kick"))
async def kick(client, message: Message):
    await client.ban_chat_member(message.chat.id, message.reply_to_message.from_user.id)
    await client.unban_chat_member(message.chat.id, message.reply_to_message.from_user.id)
    await message.edit("👢 Kicked")

@app.on_message(filters.me & filters.command("warn"))
async def warn(client, message: Message):
    await message.edit(f"⚠️ **Warning**\n{message.reply_to_message.from_user.first_name} agli baar ban")

@app.on_message(filters.me & filters.command("zombies"))
async def zombies(client, message: Message):
    count=0
    async for m in client.get_chat_members(message.chat.id):
        if m.user.is_deleted: await client.ban_chat_member(message.chat.id,m.user.id); await client.unban_chat_member(message.chat.id,m.user.id); count+=1
    await message.edit(f"✅ {count} Zombies deleted")

# ============= INFO & BROADCAST =============
@app.on_message(filters.me & filters.command("id"))
async def get_id(client, message: Message): await message.edit(f"Chat ID: `{message.chat.id}`\nYour ID: `{message.from_user.id}`")

@app.on_message(filters.me & filters.command("info"))
async def userinfo(client, message: Message):
    u=message.reply_to_message.from_user; await message.edit(f"**Name:** {u.first_name}\n**Username:** @{u.username}\n**ID:** `{u.id}`")

@app.on_message(filters.me & filters.command("purge"))
async def purge(client, message: Message):
    for i in range(message.reply_to_message.id, message.id):
        try: await client.delete_messages(message.chat.id, i)
        except: pass
    await message.reply("✅ Purged")

@app.on_message(filters.me & filters.command("broadcast"))
async def broadcast(client, message: Message):
    msg=" ".join(message.command[1:]); sent=0
    async for d in client.get_dialogs():
        try: await client.send_message(d.chat.id, f"📢 {msg}"); sent+=1
        except: pass
        await asyncio.sleep(4)
    await message.edit(f"✅ Sent to {sent} chats")

@app.on_message(filters.me & filters.command("gcast"))
async def gcast(client, message: Message):
    msg=" ".join(message.command[1:]); sent=0
    async for d in client.get_dialogs():
        if d.chat.type in ["group","supergroup"]:
            try: await client.send_message(d.chat.id, f"📢 {msg}"); sent+=1
            except: pass
            await asyncio.sleep(4)
    await message.edit(f"✅ Sent to {sent} groups")

@app.on_message(filters.me & filters.command("dcast"))
async def dcast(client, message: Message):
    msg=" ".join(message.command[1:]); sent=0
    async for d in client.get_dialogs():
        if d.chat.type=="private" and not d.chat.is_bot:
            try: await client.send_message(d.chat.id, f"📢 {msg}"); sent+=1
            except: pass
            await asyncio.sleep(4)
    await message.edit(f"✅ Sent to {sent} users")

print("ISHIKA USERBOT V1.6 FULL STARTED ✅")
app.run()
