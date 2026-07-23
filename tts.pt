from gtts import gTTS
import os

def text_to_speech(text, lang='hi'):
    tts = gTTS(text=text, lang=lang, slow=False)
    filename = f"tts_{os.urandom(4).hex()}.ogg"
    tts.save(filename)
    return filename
