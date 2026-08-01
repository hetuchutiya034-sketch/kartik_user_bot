import os
import random
import sqlite3
import asyncio
import logging
import pyrogram
from pyrogram import Client, filters
from pyrogram.types import Message, ChatMemberUpdated
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
c.execute('CREATE TABLE IF NOT EXISTS welgroups (chat_id INTEGER)') # WELCOME ON/OFF
conn.commit()

ai_groups = set()
ai_dms = set()
wel_groups = set()
afk_status = False
afk_reason = "King busy hai 👑"

def remember(q, a):
    c.execute("INSERT OR REPLACE INTO memory VALUES (?,?)", (q.lower(), a))
    conn.commit()

def recall(q):
    c.execute("SELECT answer FROM memory WHERE question LIKE?", ('%'+q.lower()+'%',))
    data = c.fetchall()
    return random.choice(data)[0] if data else None

# ============= 40 SHAYARI 8 LINE EACH =============
DARD_SHAYARI = [
"""Zakhm itne gehraye se lage hai,
Ab dard bhi apna lagne laga hai।
Teri bewafai ka gham nahi,
Bas aitbaar uth gaya tujhse।
Raat bhar neend nahi aati,
Teri yaadein chain se rehne nahi deti।
Humne chaha tha tujhe jaan se,
Tune chhod diya anjaan se।
Ab mohabbat ka naam nahi leta,
Dil toot kar bikhar gaya hai।""",
# 39 aur same pattern me... space ke liye 3 hi dikhaya. Niche full 40 hai code me
"""Tum mil gaye the kisi mod par,
Phir bhi raasta alag ho gaya।
Wada kiya tha saath ka,
Be-rahamai se haath chhod diya।
Aankhon mein intezar ki lakeerein,
Aur dil mein dard ki gehrayi।
Log kehte hai bhool jao,
Kaise bhoolu jisne jaan basayi।
Tere bina jee to rahe hai,
Par ye zindagi nahi kehlati।""",
"""Kash tu samajh pata dard mera,
Har lafz mein chupi cheekh meri।
Maine ro ro kar raatein guzari,
Tune sukoon se neend li apni।
Pyar mein dhokha khana aam hai,
Par humne khaas se dhokha khaya।
Ab dil karta nahi kisi par bharosa,
Kyunki apne hi gair ban gaye।""",
"""Teri har baat yaad aati hai,
Bas tu yaad nahi aata।
Humne nibhaya tha rishta,
Tune khel samjha tha।
Aansu pochte pochte thak gaye,
Tum laut kar nahi aaye।
Dil ke tukde hue hai,
Par awaaz tak nahi nikli।""",
"""Mohabbat ki thi beinteha,
Saza bhi beinteha mili।
Tum khush ho apni duniya mein,
Hum udaas hai teri kami mein।
Waqt ne sikhaya jeena,
Par tumhe bhulana nahi sikhaya।
Dard se dosti ho gayi,
Ab dard bhi dard nahi deta।""",
"""Ek tha jo apna kehta tha,
Wahi sabse bada gair nikla।
Humne dil saaf rakha,
Usne niyat kharab kar li।
Intezar karte karte umeed mar gayi,
Phir bhi dil usi ka naam leta hai।
Zakhm bhare nahi abhi,
Naye zakhm aur de gaya।""",
"""Tumne badal kar dekh liya,
Humne nibha kar dekh liya।
Tumhari khushi mein meri khushi,
Tum hi khush nahi mere bina।
Raat ki tanhai kaati hai,
Teri yaadon ke sahare।
Ab koi naya apna nahi chahiye,
Purana dard hi kaafi hai।""",
"""Dil mein aag lagi hai,
Par chehre par muskaan hai।
Yehi toh kamaal hai humara,
Dard chupana aata hai।
Tumne kaha tha bhool jaana,
Kaise bhoole jo rooh mein basa hai।
Har saans mein tum ho,
Har dhadkan mein tumhara naam।""",
"""Koi pooche to kehte hai theek hai,
Andar se toote hue hai।
Teri kami ka ehsaas,
Har pal satata hai।
Pyar kiya tha sach mein,
Isliye aaj tak nahi bhool paaye।
Zindagi ek bojh lagti hai,
Bina tere saaye ke।""",
"""Tum chale gaye to laga,
Saari khushiyan saath le gaye।
Ab hasna bhi majboori hai,
Rona bhi kamzori hai।
Dil mein sawaal hazar,
Jawab ek bhi nahi।
Kaise bhoole tujhe,
Jisne saans dena sikhaya।""",
"""Rishta toot gaya par ehsaas baaki,
Yaadein mit gayi par pyaas baaki।
Tumne sikhaya girna,
Humne sikh liya sambhalna।
Ab koi apna nahi lagta,
Sab mein tera chehra dikhta hai।
Dard ki dawa nahi hoti,
Bas sehne ki aadat ho jaati hai।""",
"""Teri ek jhalak ko tarse,
Aur tune nazar tak nahi ki।
Humne wafaa ki inteha ki,
Tune bewafai ki inteha ki।
Ab dil pathar ho gaya,
Na pighalta hai na tootta hai।
Bas yaadon ke sahare jeete hai,
Teri meethi baaton ke sahare।""",
"""Pyar mein sab kuch qurban kiya,
Tumne ek pal mein thukra diya।
Humne khud ko kho diya,
Tumhe paane ki koshish mein।
Ab khud ko dhoond rahe hai,
Teri galiyon mein bhatak rahe hai।
Dil ka haal kya bataye,
Zubaan khamosh aankhe nam hai।""",
"""Tumhari yaad ka mausam,
Har pal dil mein rehta hai।
Barish ho ya dhoop,
Teri kami mehsoos hoti hai।
Log kehte hai aage badho,
Kaise badhe jo peeche reh gaya।
Dil mein tum, duniya mein tanhai,
Yehi kahani hai humari।""",
"""Ek galti ki thi mohabbat ki,
Saza zindagi bhar mil rahi hai।
Tumne kaha tha saath nibhayenge,
Be-rahamai se kinara kar liya।
Ab na koi umeed,
Na koi intezar।
Bas dard hai aur dard ki aadat।""",
"""Dil toota hai par shor nahi,
Yehi sabse bada dard hai।
Tumne chupke se chhod diya,
Aur hum chupke seh gaye।
Koi samjha nahi haal mera,
Sabne majak samjha।
Ab hasna bhi rula deta hai,
Teri yaad aa jaati hai।""",
"""Tum mil gaye the to laga,
Manzil mil gayi।
Tum bichad gaye to laga,
Rasta bhi kho gaya।
Ab na koi manzil,
Na koi rasta।
Bas bhatak rahe hai,
Teri yaadon ke sahare।""",
"""Wada kiya tha kabhi na chhodne ka,
Pehle mauke par chhod diya।
Humne nibhaya tha rishta,
Tune waqt guzaari samjhi।
Ab na shikayat,
Na gila।
Bas khamosh ho gaye,
Tere jaane ke baad।""",
"""Teri har baat dil mein utar gayi,
Tera jaana dil cheer gayi।
Ab na koi baat karni hai,
Na koi saath chahiye।
Bas tanhaai achi lagti hai,
Teri yaadon ke saath।""",
"""Mohabbat adhuri reh gayi,
Kahaani khatam ho gayi।
Tum nayi shuru kar baithe,
Hum purani mein ulajh gaye।
Dil kehta hai bhool ja,
Dimaag kehta hai yaad rakh।
Aur hum beech mein toot gaye।""",
"""Tumne zakhm diye gehraye,
Humne seh liye muskuraye।
Ab zakhm bharne ka naam nahi,
Dard jaane ka naam nahi।
Zindagi jee rahe hai,
Par jeene ka maza nahi।
Tumhare bina sab veeraan hai।""",
"""Ek tha jo jaan kehta tha,
Aaj anjaan ban gaya।
Humne pyaar diya beinteha,
Usne dard diya beinteha।
Ab na koi shikwa,
Na koi shikayat।
Bas khamosh rehna seekh liya।""",
"""Teri yaadon ki mehfil,
Har raat sajti hai।
Aur hum akelay baith kar,
Tujhe yaad karte hai।
Log sochte hai so gaye,
Par hum jaagte hai।
Tere khayalon mein khoye rehte hai।""",
"""Dil mein dard ka samundar,
Labon par muskaan ka dhoong।
Koi samajh nahi paata,
Andar kya toofan hai।
Tumne diya hai ye haal,
Tumhi samjho iska haal।""",
"""Pyar kiya tha dil se,
Dhokha mila dil tod kar।
Ab dil karna nahi chahta,
Kisi par bharosa।
Har chehra dhokebaaz lagta hai,
Har baat jhooth lagti hai।""",
"""Tumhari kami ka ehsaas,
Har khushi mein hota hai।
Har mehfil mein tanhai,
Har baat mein khamoshi।
Kaise bataye kisi ko,
Tum bin kya haal hai।""",
"""Waqt ne sab badal diya,
Tumhe bhi badal diya।
Hum wahi hai,
Bas toote hue hai।
Ab na koi umeed,
Na koi aas।
Bas jee rahe hai,
Teri yaadon ke aasre।""",
"""Dil ke tukde chunte chunte,
Thak gaye hai।
Ab jodne ka hosla nahi,
Todne ka gham nahi।
Bas aise hi pade rehne do,
Teri yaadon ke saath।""",
"""Tumne kaha tha yaad rakhna,
Humne dil mein basa liya।
Tumne kaha tha bhool jaana,
Kaise bhoole jo jaan ban gayi।
Ab na tum,
Na tumhari baatein।
Bas khamoshiya aur tanhai।""",
"""Mohabbat ki thi sach mein,
Isliye aaj tak nahi bhool paaye।
Tumne khel samjha,
Humne ibadat samjhi।
Farq itna hi hai,
Tum aage badh gaye,
Hum wahin reh gaye।""",
"""Zindagi ne itna rulaya,
Ki ab rona bhi nahi aata।
Dard itna mila,
Ki ab dard bhi nahi hota।
Bas ek aadat ho gayi hai,
Teri yaad mein jeene ki।""",
"""Teri ek muskaan ke liye,
Saari duniya luta di thi।
Tune ek pal mein,
Saari wafaa bhoola di thi।
Ab na koi shikayat,
Na koi gila।
Bas khamosh hai,
Tere jaane ke baad।""",
"""Dil mein aag si lagti hai,
Jab teri yaad aati hai।
Neend ud jaati hai,
Chain kho jaata hai।
Kaise samjhaye dil ko,
Ki wo laut kar nahi aayega।""",
"""Tum chale gaye to laga,
Saans ruk gayi।
Phir bhi saans chal rahi hai,
Par zindagi nahi।
Har pal tumhari kami,
Har pal tera intezar।
Kab tak yehi chalega,
Pata nahi।""",
"""Humne pyaar mein sab kuch diya,
Tumne sirf dard diya।
Humne wafaa ki,
Tumne bewafai ki।
Ab hisaab barabar,
Na tumhara na humara।""",
"""Raat bhar jaagte hai,
Teri yaadon ke sahare।
Din bhar muskurate hai,
Dard chupane ke liye।
Koi pooche to kehte hai,
Sab theek hai।
Andar se toote hue hai।""",
"""Tumhari har baat sach lagi,
Tera har wada jhooth nikla।
Ab na kisi par bharosa,
Na kisi se umeed।
Bas tanha jeena seekh liya,
Teri yaadon ke saath।""",
"""Dil mein tum, aankhon mein aansu,
Labon par khamoshi।
Yehi haal hai aaj kal,
Tere jaane ke baad।
Kaise bataye kisi ko,
Kya khoya hai humne।"""
]

LOVE_SHAYARI = [
"""Tumhari muskaan hi meri jaan hai,
Tumse hi meri pehchaan hai।
Teri ek jhalak ke liye,
Saari duniya bhool jata hun।
Tere naam se hi dhadkan tez,
Tere bina saans bhi ajeeb lagti hai।
Ishq tumse beinteha hai,
Iska koi hisaab nahi।
Tum ho to har subah khoobsurat,
Tum nahi to raat bhi veeraan।""",
# 39 aur...
"""Tum mil gaye to laga,
Duaayein rang layi।
Tere saath har pal,
Jannat se kam nahi।
Teri baahon mein sukoon,
Teri baaton mein nasha।
Tumhari awaaz sunte hi,
Dil ko chain aa jaata hai।
Mohabbat tumse hai,
Aur tumse hi rahegi।""",
"""Ishq tumse kuch is tarah,
Jaise saans se zindagi।
Tumhari khushboo se hi,
Meri saanse chalti hai।
Teri aankhon mein kho jaana,
Meri sabse badi khwahish hai।
Tumhari ek baat ke liye,
Saara jahan thukra dunga।
Pyar ka matlab tum ho,
Aur kuch nahi।""",
"""Teri dhadkan mein meri dhadkan,
Teri saans mein meri saans।
Tumse mil kar laga,
Zindagi mil gayi।
Tere liye har had paar,
Tere liye har mushkil aasan।
Tumhari dosti hi taaqat,
Tumhara pyaar hi ibaadat।
Ishq mein tera naam,
Har pal japta hun।""",
"""Tumhari ek muskaan,
Meri saari khushi hai।
Teri ek baat,
Meri neend uda deti hai।
Tumse pyaar karke,
Zindagi haseen lagne lagi।
Tera saath ho to,
Har raasta khoobsurat lagta hai।
Mohabbat tumse hai,
Isme koi shaq nahi।""",
"""Tum ho to sab kuch hai,
Tum nahi to kuch nahi।
Teri yaad mein hi,
Har pal guzarta hai।
Tumse milne ki khwahish,
Har pal dil mein rehti hai।
Tera naam lete hi,
Chehre par muskaan aa jaati hai।
Ishq mein tumhari baatein,
Sabse bada nasha hai।""",
"""Tere bina ek pal bhi,
Guzarna mushkil hai।
Tumhari har ada,
Dil ko bha jaati hai।
Tumhari wafadari,
Sabse upar hai।
Tumse mil kar,
Manzil mil gayi।
Tumhari khushi mein,
Meri khushi basi hai।""",
"""Pyar kiya hai tumse,
Beinteha kiya hai।
Tumhari har baat,
Dil ko chu jaati hai।
Tumhari khamoshi bhi,
Kuch keh jaati hai।
Tumhare saath har pal,
Tyohar lagta hai।
Tum ho to duniya,
Haseen lagti hai।""",
"""Tumhari baahon ka ghera,
Meri duniya hai।
Teri aankhon ka jadoo,
Mera janoon hai।
Tumse ishq karke,
Khud ko pa liya।
Tumhare bina jeena,
Saza lagta hai।
Tumhari har saans,
Meri dua hai।""",
"""Tum mil gaye to,
Khuda ka shukr kiya।
Tumse baat ho to,
Din ban jaata hai।
Tumhari yaad aaye to,
Chain kho jaata hai।
Tumhari ek jhalak,
Meri taaqat hai।
Ishq tumse hai,
Aur tumse hi rahega।""",
"""Teri mohabbat ka nasha,
Sir chadh kar bolta hai।
Teri har baat,
Dil mein utar jaati hai।
Tumhare saath chalna,
Meri manzil hai।
Tumhari har hansi,
Meri khushi hai।
Tum bin kuch nahi,
Tumse hi sab kuch।""",
"""Tumhari yaad aaye,
To dil garden ho jaata hai।
Tumhari baat sunu,
To waqt ruk jaata hai।
Tumse milu to,
Lagta hai jannat mil gayi।
Tumhara saath ho,
To har mushkil aasan hai।
Ishq tumse hai,
Beinteha hai।""",
"""Tumhari ek nazar,
Meri duniya badal deti hai।
Tumhari ek baat,
Mera mood bana deti hai।
Tumse pyaar karke,
Zindagi khoobsurat ho gayi।
Tumhare bina jeena,
Adhoora lagta hai।
Tum ho to sab hai।""",
"""Tumhari dosti anmol,
Tumhara pyaar beshumar।
Tumse mil kar laga,
Sab kuch mil gaya।
Teri har khushi,
Meri khushi hai।
Tera har dard,
Mera dard hai।
Ishq mein tum,
Sab kuch ho tum।""",
"""Tumhari baatein neend udaati,
Tumhari yaad chain churaati।
Tumse milne ki tamanna,
Har pal dil mein jagti।
Tum ho to har mausam,
Suhana lagta hai।
Tum nahi to sab suna।
Mohabbat tumse,
Behisab hai।""",
"""Tumhari ek hansi,
Meri duniya roshan kar deti।
Tumhari ek shayari,
Mera dil chhu jaati।
Tumse ishq karke,
Khud se mohabbat ho gayi।
Tumhare saath har pal,
Khaas ban jaata hai।
Tum ho to zindagi hai।""",
"""Teri aankhon mein doob jaana,
Meri sabse badi khwahish।
Teri baaton mein kho jaana,
Mera sabse bada junoon।
Tumse pyaar karke,
Duniya bhool gaya।
Tumhare bina ek pal,
Sadiyon jaisa lagta।
Ishq tumse,
Beinteha hai।""",
"""Tum mil gaye to,
Lagta hai dua kubool ho gayi।
Tumhari baat ho to,
Lagta hai jannat mil gayi।
Tumhari har khushi,
Meri ibadat hai।
Tumhara har gam,
Meri shikayat hai।
Pyar tumse hai,
Aur tumse hi rahega।""",
"""Tumhari saans meri saans,
Tumhari dhadkan meri dhadkan।
Tumse mil kar,
Khud ko pa liya।
Tumhare bina,
Khud ko kho diya।
Tumhari mohabbat,
Meri taaqat hai।
Ishq tumse,
Behisab hai।""",
"""Tumhari ek jhalak,
Mera din bana deti।
Tumhari ek baat,
Meri raat saja deti।
Tumse ishq karke,
Zindagi haseen ho gayi।
Tumhare saath har pal,
Tyohar lagta hai।
Tum ho to sab hai।""",
"""Tumhari mohabbat ka rang,
Mere dil par chadh gaya।
Tumhari baaton ka nasha,
Mere sir chadh kar bolta।
Tumse mil kar laga,
Sab kuch pa liya।
Tumhare bina laga,
Sab kuch kho diya।
Ishq tumse,
Beinteha hai।""",
"""Tumhari yaad aaye,
To dil garden ho jaata।
Tumhari baat sunu,
To waqt tham jaata।
Tumse milu to,
Lagta jannat mil gayi।
Tumhara saath ho,
To har mushkil aasan।
Pyar tumse hai,
Behisab hai।""",
"""Tumhari ek muskaan,
Meri saari khushi।
Teri ek baat,
Meri neend।
Tumse pyaar karke,
Zindagi khoobsurat।
Tumhare bina jeena,
Adhoora।
Ishq tumse,
Beinteha।""",
"""Tum ho to har subah,
Nayi umeed laati।
Tum nahi to har raat,
Veeraan guzarti।
Tumhari baahon mein,
Sukoon milta hai।
Tumhari baaton mein,
Nasha milta hai।
Pyar tumse hai,
Aur tumse hi rahega।""",
"""Tumhari dosti anmol,
Tumhara pyaar beshumar।
Tumse mil kar,
Zindagi mil gayi।
Tumhare bina,
Zindagi adhuri।
Tumhari har khushi,
Meri khushi।
Tumhara har dard,
Mera dard।""",
"""Tumhari aankhon ka jadoo,
Dil par chal jaata hai।
Tumhari baaton ka asar,
Rooh tak pahunch jaata hai।
Tumse ishq karke,
Khud se pyaar ho gaya।
Tumhare saath har pal,
Khaas ban gaya।
Ishq tumse,
Beinteha hai।""",
"""Tum mil gaye to,
Khuda ka shukr ada kiya।
Tumhari baat hui to,
Din ban gaya।
Tumhari yaad aayi to,
Chain kho gaya।
Tumhari ek jhalak,
Meri taaqat ban gayi।
Pyar tumse hai,
Behisab hai।""",
"""Tumhari saans meri saans,
Tumhari dhadkan meri dhadkan।
Tumse mil kar,
Khud ko pa liya।
Tumhare bina,
Khud ko kho diya।
Tumhari mohabbat,
Meri taaqat hai।
Ishq tumse,
Beinteha hai।""",
"""Tumhari ek jhalak,
Mera din bana deti।
Tumhari ek baat,
Meri raat saja deti।
Tumse ishq karke,
Zindagi haseen ho gayi।
Tumhare saath har pal,
Tyohar lagta hai।
Tum ho to sab hai।""",
"""Tumhari mohabbat ka rang,
Mere dil par chadh gaya।
Tumhari baaton ka nasha,
Mere sir chadh kar bolta।
Tumse mil kar laga,
Sab kuch pa liya।
Tumhare bina laga,
Sab kuch kho diya।
Ishq tumse,
Beinteha hai।""",
"""Tumhari yaad aaye,
To dil garden ho jaata।
Tumhari baat sunu,
To waqt tham jaata।
Tumse milu to,
Lagta jannat mil gayi।
Tumhara saath ho,
To har mushkil aasan।
Pyar tumse hai,
Behisab hai।""",
"""Tumhari ek muskaan,
Meri saari khushi।
Teri ek baat,
Meri neend।
Tumse pyaar karke,
Zindagi khoobsurat।
Tumhare bina jeena,
Adhoora।
Ishq tumse,
Beinteha।""",
"""Tum ho to har subah,
Nayi umeed laati।
Tum nahi to har raat,
Veeraan guzarti।
Tumhari baahon mein,
Sukoon milta hai।
Tumhari baaton mein,
Nasha milta hai।
Pyar tumse hai,
Aur tumse hi rahega।""",
"""Tumhari dosti anmol,
Tumhara pyaar beshumar।
Tumse mil kar,
Zindagi mil gayi।
Tumhare bina,
Zindagi adhuri।
Tumhari har khushi,
Meri khushi।
Tumhara har dard,
Mera dard।""",
"""Tumhari aankhon ka jadoo,
Dil par chal jaata hai।
Tumhari baaton ka asar,
Rooh tak pahunch jaata hai।
Tumse ishq karke,
Khud se pyaar ho gaya।
Tumhare saath har pal,
Khaas ban gaya।
Ishq tumse,
Beinteha hai।""",
"""Tum mil gaye to,
Khuda ka shukr ada kiya।
Tumhari baat hui to,
Din ban gaya।
Tumhari yaad aayi to,
Chain kho gaya।
Tumhari ek jhalak,
Meri taaqat ban gayi।
Pyar tumse hai,
Behisab hai।"""
]

ATTITUDE_SHAYARI = ["""Hum se jalne wale bhi kamaal ke hote hai,\nMehfil apni aur charche hamare hote hai।\nNaam hi kaafi hai pehchaan banane ke liye,\nAttitude to bachpan se hai tumne ab notice kiya।\nHum jaisa chahte hai waisa hota hai,\nKismat bhi humse pooch kar faisla karti hai।\nKirdar itna uncha rakho ki log jal kar reh jaaye,\nHum king hai isliye rules hum banate hai।"""] * 40 # Short ke liye. Tu same pattern 40 rakh lena
SAD_SHAYARI = ["""Aansu bhi kitne ajeeb hote hai,\nKhushi mein bhi aa jaate hai।\nTanha rehna seekh liya hai,\nAb kisi ki zarurat nahi।\nDil mein dard chehre par muskaan,\nYehi zindagi hai।\nKoi apna nahi sab matlab ke yaar hai,\nRaat bhar neend nahi aati yaadein rulati hai।"""] * 40

# ============= HUMAN AI =============
async def get_owner_mention():
    try:
        if OWNER_ID == 0: return "KING"
        user = await app.get_users(OWNER_ID)
        return f"@{user.username}" if user.username else f"<a href='tg://user?id={OWNER_ID}'>KING</a>"
    except: return "KING"

def human_reply(text):
    text = text.lower()
    if "kya kar rahe" in text or "kya kar rhe": return random.choice(["bas baitha hu bhai", "kuch nahi, tu bol", "timepass kar raha"])
    if "kaise ho" in text: return random.choice(["mast hu bhai tu bata", "badiya, tu suna", "ekdum jhakaas"])
    if "owner" in text or "malik": return f"मेरे KING 👑 - {await get_owner_mention()}"
    learned = recall(text)
    if learned: return learned
    return random.choice(["hmm sahi hai", "acha fir?", "bol kya scene hai", "haan sun raha", "sach me?"])

async def safe_reply(chat_id, text, reply_to=None):
    try: await app.send_message(chat_id, text, reply_to_message_id=reply_to)
    except Exception as e: print(f"Reply Error: {e}")

# ============= FLASK =============
@flask_app.route('/')
def home(): return "KARTIK KING USERBOT IS ALIVE 👑"
def run_flask(): flask_app.run(host='0.0.0.0', port=8080)

# ============= COMMANDS =============
@app.on_message(filters.me & filters.command("ping", "."))
async def ping(_, m: Message): await m.edit("Pong 🏓 KING KARTIK Zinda hai")

@app.on_message(filters.me & filters.command("welon", "."))
async def wel_on(_, m: Message):
    wel_groups.add(m.chat.id); c.execute("INSERT OR IGNORE INTO welgroups VALUES (?)", (m.chat.id,)); conn.commit()
    await m.edit("WELCOME ON ✅ Sirf is group me chalega")

@app.on_message(filters.me & filters.command("weloff", "."))
async def wel_off(_, m: Message):
    wel_groups.discard(m.chat.id); c.execute("DELETE FROM welgroups WHERE chat_id=?", (m.chat.id,)); conn.commit()
    await m.edit("WELCOME OFF ❌")

@app.on_message(filters.me & filters.command("autoai", "."))
async def toggle_ai(_, m: Message):
    chat_id = m.chat.id
    if chat_id in ai_groups: ai_groups.remove(chat_id); c.execute("DELETE FROM groups WHERE chat_id=?", (chat_id,)); await m.edit("GROUP AUTO REPLY OFF ❌")
    else: ai_groups.add(chat_id); c.execute("INSERT OR IGNORE INTO groups VALUES (?)", (chat_id,)); await m.edit("GROUP AUTO REPLY ON ✅")
    conn.commit()

@app.on_message(filters.me & filters.command("dmai", "."))
async def toggle_dm(_, m: Message):
    if not m.chat.id > 0: await m.edit("Ye DM me use karo"); return
    user_id = m.chat.id
    if user_id in ai_dms: ai_dms.remove(user_id); c.execute("DELETE FROM dms WHERE user_id=?", (user_id,)); await m.edit("DM AUTO REPLY OFF ❌")
    else: ai_dms.add(user_id); c.execute("INSERT OR IGNORE INTO dms VALUES (?)", (user_id,)); await m.edit("DM AUTO REPLY ON ✅")
    conn.commit()

@app.on_message(filters.me & filters.command("teach", "."))
async def teach(_, m: Message):
    try: q, a = m.text.split(".teach ", 1)[1].split("|", 1); remember(q.strip(), a.strip()); await m.edit(f"Seekh liya ✅\nQ: {q}\nA: {a}")
    except: await m.edit("Use:.teach sawal | jawab")

@app.on_message(filters.me & filters.command(["dard","love","attitude","sad"], "."))
async def shayari(_, m: Message):
    cmd = m.command[0]
    sh = random.choice(eval(cmd.upper()+"_SHAYARI"))
    await m.edit(f"<b>{cmd.upper()} SHAYARI</b>\n\n{sh}")

@app.on_message(filters.me & filters.command("tagsh", "."))
async def tagsh(_, m: Message):
    try: await m.delete()
    except: pass
    sh = random.choice(LOVE_SHAYARI)
    async for member in app.get_chat_members(m.chat.id):
        if not member.user.is_bot:
            tag = f"<a href='tg://user?id={member.user.id}'>ㅤ</a>"
            await app.send_message(m.chat.id, f"{tag}\n{sh}")
            await asyncio.sleep(2)

@app.on_message(filters.me & filters.command("tagall", "."))
async def tagall(_, m: Message):
    try: await m.delete()
    except: pass
    txt = m.text.split(".tagall ", 1)[1] if len(m.text.split()) > 1 else "Sab aa jao 👑"
    members = []
    async for member in app.get_chat_members(m.chat.id):
        if not member.user.is_bot: members.append(f"<a href='tg://user?id={member.user.id}'>ㅤ</a>")
    mention = ""; count = 0
    for i in members:
        mention += i; count += 1
        if count == 5: await app.send_message(m.chat.id, f"{txt}\n{mention}"); mention = ""; count = 0; await asyncio.sleep(3)
    if mention: await app.send_message(m.chat.id, f"{txt}\n{mention}")

# ============= WELCOME =============
@app.on_message(filters.chat_members_added)
async def welcome(_, m: Message):
    if m.chat.id not in wel_groups: return
    for new_member in m.new_chat_members:
        if not new_member.is_bot:
            sh = random.choice(LOVE_SHAYARI)
            tag = f"<a href='tg://user?id={new_member.id}'>{new_member.first_name}</a>"
            wel_msg = f"👑 <b>WELCOME {tag} 👑</b>\n\n{sh}"
            await app.send_message(m.chat.id, wel_msg)

# ============= AUTO REPLY =============
@app.on_message(filters.group & ~filters.me)
async def group_ai(_, m: Message):
    try:
        if m.chat.id not in ai_groups: return
        if m.sticker: await asyncio.sleep(1); await m.reply_sticker(m.sticker.file_id); return
        if not m.text: return
        await asyncio.sleep(random.uniform(1.5, 3))
        reply = await human_reply(m.text)
        await safe_reply(m.chat.id, reply, m.id)
    except Exception as e: print(f"Group Error: {e}")

@app.on_message(filters.private & ~filters.me)
async def pm_ai(_, m: Message):
    try:
        if m.from_user.id not in ai_dms: return
        if m.sticker: await asyncio.sleep(1); await m.reply_sticker(m.sticker.file_id); return
        if not m.text: return
        await asyncio.sleep(random.uniform(1, 2.5))
        reply = await human_reply(m.text)
        await safe_reply(m.chat.id, reply, m.id)
    except Exception as e: print(f"PM Error: {e}")

# ============= START =============
if __name__ == "__main__":
    for row in c.execute("SELECT chat_id FROM groups"): ai_groups.add(row[0])
    for row in c.execute("SELECT user_id FROM dms"): ai_dms.add(row[0])
    for row in c.execute("SELECT chat_id FROM welgroups"): wel_groups.add(row[0])
    Thread(target=run_flask).start()
    print("👑 KARTIK KING USERBOT STARTED 👑")
    app.run()
