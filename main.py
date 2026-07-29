import os
from dotenv import load_dotenv
load_dotenv()
import asyncio, os, random
from io import BytesIO

from pyrogram import Client, filters
from pyrogram.types import Message, ChatPrivileges, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait
from pyrogram.raw.functions.account import UpdateProfile
from pyrogram.raw.functions.photos import UploadProfilePhoto # DeleteProfilePhotos hata diya
import aiohttp
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION = os.getenv("SESSION")

app = Client("ishikauserbot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION)
tagging = False
tagsh_active = {}
welcome_on = {}

my_name = None
my_bio = None

# ============= SETTINGS =============
SUPPORT_GROUP = "https://t.me/+AAB-iIMnebBmMWZl"
UPDATE_CHANNEL = "https://t.me/+AAB-iIMnebBmMWZl"
OWNER_LINK = "https://t.me/KARTIK_NISHAD_3"
BOT_USERNAME = "https://t.me/YourBotUsername"

# ============= FULL 17 SHAYARI =============
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

FLIRT = ["Tum haste ho to dil garden ho jata hai 😍", "Tum chai ho aur main biscuit, sath me mast lagte hai", "Teri ek jhalak dekhne ko dil taras jata hai"]
JOKES = ["Teacher: 2+2? Student: 5. Teacher: Galat. Student: Aapke hisab se 😂", "Doctor: Neend nahi aati? Patient: Nahi. Doctor: To so jao 😂"]
MEMES = ["Jab crush online aaye", "Monday morning vibes", "Exam ke 1 din pehle"]
WELCOMES = ["🎉 **WELCOME TO {chat}** 🎉\n\n👤 **Name:** {name}\n🆔 **ID:** `{id}`\n🔗 **Username:** @{username}\n\nAapke aane se group me rounak badh gayi 😍💎"]

DEVIL_NAMES = ["😈 Devil King", "👿 Lucifer", "🔥 Hell Lord", "☠️ Satan"]
DEVIL_BIOS = ["I am the darkness", "Born in hell", "King of Devils 😈", "Fear me"]

# ============= AUTO COUPLE PIC FUNCTION =============
async def generate_couple_pic():
    prompts = [
        "anime couple boy and girl holding hands, romantic sunset, aesthetic, high quality, 4k",
        "cute anime couple sitting together, cherry blossoms, romantic, detailed",
        "anime boy and girl, couple portrait, glowing, cinematic background"
    ]
    prompt = random.choice(prompts)
    api_url = f"https://image.pollinations.ai/prompt/{prompt}?width=1024&height=1024&seed={random.randint(1,99999)}&nologo=true"
    async with aiohttp.ClientSession() as session:
        async with session.get(api_url) as resp:
            img_bytes = await resp.read()
    return img_bytes

# ============= BASIC COMMANDS =============
@app.on_message(filters.me & filters.command("ping"))
async def ping(client, message: Message):
    await message.edit("🏓 **PONG!**\n`Bot zinda hai aur active hai` ⚡")

@app.on_message(filters.me & filters.command("help"))
async def help(client, message: Message):
    text = """╭━━━━━━━━━╮
   ⚡ **ISHIKA USERBOT V2.5 FULL** ⚡
╰━━━━━━━━━╯

🏷️ **TAG & ADMIN**
- `/tagall <msg>` - Sabko tag
- `/tagsh` - 17 Shayari ke sath tag 😈
- `/stoptagsh` - Tag rok do

👑 **INFO & CLONE**
- `/clone` - DP + Name + Bio copy
- `/back` - Wapas original Name/Bio

💞 **FUN & AI**
- `/shayari` - 17 Dard wali shayari 💔
- `/couple` - **AUTO AI COUPLE PIC** 💑
- `/flirt` `/joke` `/meme` `/logo` `/devil` `/tts`

📢 **BROADCAST**
- `/broadcast` `/gcast` `/dcast`

⚙️ **SETTINGS**
- `/welcome on/off` `/string` `/ping`
╭─ Made by @KARTIK_NISHAD_3 ─╮"""
    await message.edit(text)

@app.on_message(filters.me & filters.command("string"))
async def gen_string(client, message: Message):
    await message.edit(f"🔐 **STRING SESSION** 🔐\n\n`{SESSION}`\n\n`Isko kisi ko mat dena` ⚠️")

# ============= CLONE + BACK =============
@app.on_message(filters.me & filters.command("clone") & filters.reply)
async def clone(client, message: Message):
    global my_name, my_bio
    user = message.reply_to_message.from_user
    if my_name is None:
        me = await client.get_me()
        my_name, my_bio = me.first_name, me.bio
    wait = await message.edit("⏳ **Cloning in progress...**")
    full_user = await client.get_chat(user.id)
    bio = full_user.bio or ""
    photos = [p async for p in client.get_chat_photos(user.id, limit=1)]
    if photos:
        file = await client.download_media(photos[0])
        await client.invoke(UploadProfilePhoto(file=await client.save_file(file)))
        os.remove(file)
    await client.invoke(UpdateProfile(first_name=user.first_name, last_name=user.last_name or "", bio=bio))
    await wait.edit(f"✅ **CLONE SUCCESSFUL** ✅\n👤 **Name:** {user.first_name}")

@app.on_message(filters.me & filters.command("back"))
async def back(client, message: Message):
    global my_name, my_bio
    await message.edit("🔄 **Restoring Original Profile...**")
    # DeleteProfilePhotos hata diya kyunki Railway support nahi karta
    await client.invoke(UpdateProfile(first_name=my_name, bio=my_bio or ""))
    await message.edit("✅ **PROFILE RESTORED** ✅ 👑\n`Note: DP manually delete karni padegi`")

# ============= AUTO COUPLE =============
@app.on_message(filters.me & filters.command("couple"))
async def couple(client, message: Message):
    wait = await message.edit("💞 **AI se Couple Pic bana raha hu...**\n`Please wait 5-7 seconds` ✨")
    try:
        img_bytes = await generate_couple_pic()
        img = Image.open(BytesIO(img_bytes))
        output_path = "couple.jpg"
        img.save(output_path)
        caption = """💞 **RANDOM AI COUPLE PIC** 💞\n\nTag your partner and make them jealous 😏❤️\n`Generated by Pollinations AI`"""
        await wait.delete()
        await message.reply_photo(photo=output_path, caption=caption)
        os.remove(output_path)
    except Exception as e:
        await wait.edit(f"❌ **Error:** `{e}`")

# ============= SHAYARI =============
@app.on_message(filters.me & filters.command("shayari"))
async def shayari_unlimited(client, message: Message):
    sh = random.choice(SHAYARI_LIST)
    await message.edit(f"💔 **DARD WALI SHAYARI** 💔\n\n{sh}\n\n`— I FOR YOU ❤️💞🌹`")

# ============= FLIRT =============
@app.on_message(filters.me & filters.command("flirt"))
async def flirt_cmd(client, message: Message):
    await message.edit(f"😏 **FLIRT** 😏\n\n{random.choice(FLIRT)}")

# ============= JOKE =============
@app.on_message(filters.me & filters.command("joke"))
async def joke(client, message: Message):
    await message.edit(f"😂 **JOKE** 😂\n\n{random.choice(JOKES)}")

# ============= MEME =============
@app.on_message(filters.me & filters.command("meme"))
async def meme(client, message: Message):
    await message.edit(f"🤣 **MEME** 🤣\n\n{random.choice(MEMES)}")

# ============= DEVIL =============
@app.on_message(filters.me & filters.command("devil"))
async def devil_mode(client, message: Message):
    await message.edit("😈 **ENTERING DEVIL MODE...**")
    name = random.choice(DEVIL_NAMES)
    bio = random.choice(DEVIL_BIOS)
    img = Image.new('RGB', (512, 512), color = 'black')
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 80)
    except:
        font = ImageFont.load_default()
    d.text((100,200), "DEVIL", fill="red", font=font)
    img.save("devil.jpg")
    await client.invoke(UploadProfilePhoto(file=await client.save_file("devil.jpg")))
    await client.invoke(UpdateProfile(first_name=name, bio=bio))
    os.remove("devil.jpg")
    await message.edit(f"😈 **DEVIL MODE ON**\n👑 **Name:** `{name}`\n📝 **Bio:** `{bio}`")

# ============= LOGO =============
@app.on_message(filters.me & filters.command("logo"))
async def logo_gen(client, message: Message):
    args = message.text.split()[1:]
    if len(args) == 0: return await message.edit("❌ **Use:** `/logo boy Kartik` ya `/logo girl Ishika`")
    if args[0].lower() in ["boy", "b"]: gender, name = "boy", " ".join(args[1:])
    else: gender, name = "girl", " ".join(args)
    if not name: return await message.edit("❌ **Naam kaha hai bhai?** `/logo boy Aryan`")
    wait_msg = await message.edit(f"✨ **{name} ke liye anime logo bana raha hu...** ✨")
    try:
        prompt = f"anime {gender} character portrait, aesthetic background, glowing, cinematic"
        api_url = f"https://image.pollinations.ai/prompt/{prompt}?width=1024&height=1024&seed={random.randint(1,99999)}&nologo=true"
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as resp:
                img_bytes = await resp.read()
        img = Image.open(BytesIO(img_bytes)).convert("RGB")
        draw = ImageDraw.Draw(img)
        try: font = ImageFont.truetype("arial.ttf", 100)
        except: font = ImageFont.load_default()
        x, y = (img.width - draw.textbbox((0,0), name, font=font)[2]) / 2, img.height - 180
        for i in range(1, 5): draw.text((x+i, y+i), name, font=font, fill="black")
        draw.text((x, y), name, font=font, fill="white")
        output_path = f"logo_{name}.jpg"; img.save(output_path)
        await wait_msg.delete()
        await message.reply_photo(photo=output_path, caption=f"✨ **{name} ka Anime Logo Ready** ✨\n**Gender:** {gender.capitalize()}")
        os.remove(output_path)
    except Exception as e: await wait_msg.edit(f"❌ **Error:** `{e}`")

# ============= TTS =============
@app.on_message(filters.me & filters.command("tts"))
async def tts_cmd(client, message: Message):
    if len(message.command) < 2: return await message.edit("❌ **Use:** `/tts hello`")
    text = " ".join(message.command[1:])
    await message.edit(f"🎙️ **Voice bana raha hu...**\n`{text}`")
    gTTS(text, lang='hi').save("voice.ogg")
    await client.send_voice(message.chat.id, "voice.ogg")
    await message.delete()
    os.remove("voice.ogg")

# ============= TAG COMMANDS =============
@app.on_message(filters.me & filters.command("tagall") & filters.group)
async def tagall(client, message: Message):
    global tagging; tagging=True; msg=" ".join(message.command[1:]); await message.delete()
    await client.send_message(message.chat.id, "🚀 **TAGALL STARTED** 🚀")
    async for user in client.get_chat_members(message.chat.id):
        if not tagging or user.user.is_bot: continue
        await client.send_message(message.chat.id, f"[{user.user.first_name}](tg://user?id={user.user.id}) {msg}"); await asyncio.sleep(3)
    await client.send_message(message.chat.id, "✅ **TAGALL COMPLETED** ✅")

@app.on_message(filters.me & filters.command("cancel"))
async def cancel_tag(client, message: Message):
    global tagging; tagging=False; await message.edit("⛔ **TAGGING STOPPED** ⛔")

@app.on_message(filters.me & filters.command("tagsh") & filters.group)
async def tagsh(client, message: Message):
    global tagsh_active; chat_id = message.chat.id; tagsh_active[chat_id] = True
    await message.edit("🚀 **TAGSH STARTED** 🚀\n`17 Shayari me se har member ko alag tag`")
    shayari_copy = SHAYARI_LIST.copy(); random.shuffle(shayari_copy); i = 0; count = 0
    async for member in client.get_chat_members(chat_id):
        if not tagsh_active.get(chat_id): break
        if member.user and not member.user.is_bot and not member.user.is_deleted:
            shayari = shayari_copy[i % len(shayari_copy)]
            text = f"💌 **TAG {count+1}** 💌\n\n[{member.user.first_name}](tg://user?id={member.user.id})\n\n{shayari}"
            try: await client.send_message(chat_id, text); i += 1; count +=1; await asyncio.sleep(2)
            except FloodWait as e: await asyncio.sleep(e.value)
            except: pass
    tagsh_active[chat_id] = False; await client.send_message(chat_id, f"✅ **TAGSH COMPLETED** ✅\n`Total Tagged: {count} members`")

@app.on_message(filters.me & filters.command("stoptagsh"))
async def stoptagsh(client, message: Message):
    global tagsh_active; tagsh_active[message.chat.id] = False; await message.edit("⛔ **TAGSH STOPPED** ⛔")

# ============= ADMIN =============
@app.on_message(filters.me & filters.command("promote") & filters.reply)
async def promote(client, message: Message):
    await client.promote_chat_member(message.chat.id, message.reply_to_message.from_user.id, privileges=ChatPrivileges(can_manage_chat=True,can_delete_messages=True,can_restrict_members=True,can_invite_users=True,can_pin_messages=True))
    await message.edit(f"✅ **PROMOTED** ✅\n{message.reply_to_message.from_user.first_name} ko admin bana diya")

@app.on_message(filters.me & filters.command("ban") & filters.reply)
async def ban(client, message: Message):
    await client.ban_chat_member(message.chat.id, message.reply_to_message.from_user.id)
    await message.edit(f"🔨 **BANNED** 🔨\n{message.reply_to_message.from_user.first_name}")

@app.on_message(filters.me & filters.command("kick") & filters.reply)
async def kick(client, message: Message):
    await client.ban_chat_member(message.chat.id, message.reply_to_message.from_user.id)
    await client.unban_chat_member(message.chat.id, message.reply_to_message.from_user.id)
    await message.edit(f"👢 **KICKED** 👢\n{message.reply_to_message.from_user.first_name}")

# ============= INFO =============
@app.on_message(filters.me & filters.command("id"))
async def get_id(client, message: Message):
    await message.edit(f"🆔 **ID INFO** 🆔\n\n**Chat ID:** `{message.chat.id}`\n**Your ID:** `{message.from_user.id}`")

@app.on_message(filters.me & filters.command("info") & filters.reply)
async def userinfo(client, message: Message):
    u=message.reply_to_message.from_user
    await message.edit(f"👤 **USER INFO** 👤\n\n**Name:** {u.first_name}\n**Username:** @{u.username}\n**ID:** `{u.id}`")

# ============= WELCOME =============
@app.on_message(filters.me & filters.command("welcome") & filters.group)
async def welcome_toggle(client, message: Message):
    global welcome_on
    if len(message.command) < 2: return await message.edit("❌ **Use:** `/welcome on` or `/welcome off`")
    welcome_on[message.chat.id] = True if message.command[1] == "on" else False
    await message.edit(f"✅ **WELCOME {'ON' if welcome_on[message.chat.id] else 'OFF'}** ✅")

@app.on_message(filters.group & filters.new_chat_members)
async def welcome(client, message: Message):
    if not welcome_on.get(message.chat.id, True): return
    for user in message.new_chat_members:
        if user.is_self: continue
        chat = await client.get_chat(message.chat.id)
        username = user.username if user.username else "NoUsername"
        photos = [p async for p in client.get_chat_photos(user.id, limit=1)]
        photo = photos[0].file_id if photos else None
        wel = random.choice(WELCOMES).format(name=user.first_name, id=user.id, username=username, chat=chat.title)
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("🛡️ Group Link", url=SUPPORT_GROUP)],
            [InlineKeyboardButton("📢 Channel Link", url=UPDATE_CHANNEL)],
            [InlineKeyboardButton("👑 Owner", url=OWNER_LINK)],
            [InlineKeyboardButton("➕ Add Me Baby", url=BOT_USERNAME)]
        ])
        if photo: await client.send_photo(message.chat.id, photo=photo, caption=wel, reply_markup=buttons)
        else: await client.send_message(message.chat.id, wel, reply_markup=buttons)

# ============= BROADCAST =============
@app.on_message(filters.me & filters.command("broadcast"))
async def broadcast(client, message: Message):
    if len(message.command) < 2: return await message.edit("❌ **Use:** `/broadcast your message`")
    msg = " ".join(message.command[1:]); sent, failed = 0, 0
    status = await message.edit("📢 **Broadcasting started...**")
    async for d in client.get_dialogs():
        try: await client.send_message(d.chat.id, f"📢 **BROADCAST**\n\n{msg}"); sent += 1
        except: failed += 1
        await asyncio.sleep(3)
    await status.edit(f"✅ **BROADCAST DONE** ✅\n**Sent:** {sent}\n**Failed:** {failed}")


# ============= BRAILLE ROSE COMMANDS =============
BRAILLE_ROSE_TEMPLATE = """⣤⢔⣒⠂⣀⣤⣄⣀
⣴⣿⠋⢠⣟⡼⣷⠼⣆⣼⢇⣿⣄⠱⣄
⠹⣿⡀⣆⠙⠢⠐⠉⣴⣾⣽⢟⡰⠃
⠀⠈⢿⣿⣦ ⠤⢴⣿⠿⢋⣴⡏
⠀⠀ ⢸⡙⠻⣿⣶⣦⣭⣉⠁⣿
⠀⠀⠀⣷ ⠈{name}⠉⡟
⠀⠀⢀ ⣘⣦⣀ ⣀⡴⠊
⠀⠈⠙⠛⢻⣿⣿⣿⣿⠻⣧⡀
⠀⠀⠀⠈⠫⣿⠉⠻⣇⠘⠓⠂
⠀⠀⠀⠀⠀⠀⠀⣿
⢶⣾⣿⣶⣄ ⣿
⠀⠹⣿⣿⣧ ⢸⣿
⠀⠀⠈⠙⠻⢿⣿⠿⠛⣄⢸⡇
⠀⠀⠀⠀⠀⠀⠘⣿⡇
⠀⠀⠀⠀⠀⣿
⠀⠀⠀⠀⠀⠀⠀⣿⠇
⠀⠀⠀⠀⠀⠀⠀⠋"""

ROMANTIC_ROSE = """⣤⢔⣒⠂⣀⣤⣄⣀
⣴⣿⠋⢠⣟⡼⣷⠼⣆⣼⢇⣿⣄⠱⣄
⠹⣿⡀⣆⠙⠢⠐⠉⣴⣾⣽⢟⡰⠃
⠀⠈⢿⣿⣦ ⠤⢴⣿⠿⢋⣴⡏
⠀⠀ ⢸⡙⠻⣿⣶⣦⣭⣉⠁⣿
⠀⠀⠀⣷ ⠈{name}⠉⡟
⠀⠀⢀ ⣘⣦⣀ ⣀⡴⠊
⠀⠈⠙⠛⠛⢻⣿⣿⠻⣧⡀
⠀⠀⠀⠈⠫⣿ {line1} ⠻⣇
⠀⠀⠀⣿ {line2}
⢶⣾⣿⣶⣄ ⣿
⠀⠹⣿⣿⣧ ⢸⣿
⠀⠀⠈⠙⠻⢿⣿⠿⠛⣄⢸⡇
⠀⠀⠀⠀⠘⣿⡇
⠀⠀⠀⣿
⠀⠀⠀⣿⠇
⠀⠀⠀⠀⠀⠀⠀⠋"""


@app.on_message(filters.me & filters.command("rosename", "."))
async def name_rose(client, message: Message):
    if len(message.command) < 2:
        return await message.edit("❌ **Use:** `.rosename KARTIK`")
    
    name = " ".join(message.command[1:]).upper()
    if len(name) > 10:
        return await message.edit("❌ **Naam 10 letters se chota rakho**")
    
    rose = BRAILLE_ROSE_TEMPLATE.format(name=name)
    await message.edit(f"🌹 **{name} KA BRAILLE ROSE** 🌹\n\n`{rose}`")


@app.on_message(filters.me & filters.command("romanticrose", "."))
async def romantic_rose(client, message: Message):
    args = message.command[1:]
    if len(args) < 3:
        return await message.edit("❌ **Use:** `.romanticrose NAME LINE1 LINE2`\nEx: `.romanticrose PRIYA I LOVE YOU`")

    name = args[0].upper()
    line1 = " ".join(args[1:2]).upper()
    line2 = " ".join(args[2:]).upper()

    if len(line1) > 8: line1 = line1[:8]
    if len(line2) > 12: line2 = line2[:12]
    if len(name) > 10: name = name[:10]

    rose = ROMANTIC_ROSE.format(name=name, line1=line1, line2=line2)
    await message.edit(f"❤️ **ROMANTIC ROSE FOR {name}** ❤️\n\n`{rose}`")


@app.on_message(filters.me & filters.command("50rose", "."))
async def fifty_rose(client, message: Message):
    names = ["KARTIK","ISHIKA","PRIYA","RAHUL","ANJALI","ARJUN","SNEHA","VIKAS","PAYAL","AMAN",
             "NEHA","ROHIT","POOJA","AJAY","RITU","SUMIT","KIRAN","DEEPAK","SHRUTI","MOHIT",
             "SIMRAN","SAHIL","TANU","NIKHIL","ANITA","VARUN","RIA","AKASH","MUSKAN","KUNAL",
             "ANUSHA","RAJ","KHUSHI","SACHIN","DIVYA","YASH","TANVI","ABHISHEK","NANDINI","VIVEK",
             "SAKSHI","HARSH","MEERA","ADITYA","JYOTI","RITESH","KOMAL","ANKIT","PALAK","LOVE"]
    
    await message.edit("⏳ **50 Rose bana raha hu...**")
    for name in names:
        rose = BRAILLE_ROSE_TEMPLATE.format(name=name)
        await client.send_message(message.chat.id, f"🌹 **{name}** 🌹\n\n`{rose}`")
        await asyncio.sleep(1.5)
        
print("🔥 ISHIKA USERBOT V2.5 FULL STARTED ✅ 17 SHAYARI + AI COUPLE 🔥")
app.run()
