import telebot
import db_manager as dbm


token = ""

bot = telebot.TeleBot(token)

# greating headler
@bot.message_handler(commands=['start'])
def send_welcome(message):
    dbm.create_user(message.from_user.id)
    bot.send_message(message.from_user.id, ("Hello! I'm 'OpenCV Test Bot'\n"
                                            "I can do two things:\n"
                                            "-Save your voice messages\n"
                                            "-Save photos where i find face\n"
                                            "Lets try!"))

# create DB headler
@bot.message_handler(commands=['create'])
def new_db(message):
    if message.from_user.id == 364251261:
        dbm.create_db()
        bot.reply_to(message, "New DB created")

# income voice message headler
@bot.message_handler(content_types=['voice'])
def handle_audio(message):
    voice_mes = bot.get_file(message.voice.file_id)
    url = f"https://api.telegram.org/file/bot{token}/{voice_mes.file_path}"
    r = dbm.save_voice(url, message.from_user.id)
    if r['returncode']:
        bot.send_message(message.from_user.id, 'Somesing go wrong!')
    else:
        bot.send_message(message.from_user.id,
                         f'Voice message #{r["voice_id"]} saved!')

# income photo file headler
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    photo_mes = bot.get_file(message.photo[1].file_id)
    url = f"https://api.telegram.org/file/bot{token}/{photo_mes.file_path}"
    r = dbm.save_photo(url, message.from_user.id)
    if r:
        bot.send_message(message.from_user.id, 'Somesing go wrong!')
    else:
        bot.send_message(message.from_user.id, 'Face was found!')

# bot main loop
bot.polling()
