import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from yt_dlp import YoutubeDL

TOKEN = '8836953701:AAEbpxTeKOpKgDFizChADZdopUOaGuFE53Y'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("🚀 خێرایی و کوالێتی بەرز", callback_data="info"))
    welcome_text = (
        "🤖 سڵاو! من بۆتی داوڵۆدکردنی ڤیدیۆم.\n\n"
        "🔗 تەنها لینکێکی تیکتۆک، ئینستاگرام، فەیسبوک یان سناپچات بنێرە، "
        "من بە بەرزترین کوالێتی و بێ وەتەرمارک بۆت دابەزێنم!"
    )
    bot.reply_to(message, welcome_text, reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_link(message):
    url = message.text.strip()
    if not url.startswith('http'):
        bot.reply_to(message, "❌ هەڵە! تکایە تەنها لینکێکی ڕاست و دروست بنێرە.")
        return

    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("🎬 ڤیدیۆ (بێ وەتەرمارک)", callback_data=f"vid|{url}"),
        InlineKeyboardButton("🎵 تەنها دەنگ (MP3)", callback_data=f"aud|{url}")
    )
    bot.reply_to(message, "🎯 لینکەکەت وەرگیرا! یەکێک لەم دوگمەکانە هەڵبژێرە:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    data = call.data.split('|')
    if data[0] == "info":
        bot.answer_callback_query(call.id, "بۆتی داوڵۆدکردن ئامادەیە!", show_alert=True)
        return
        
    action = data[0]
    url = data[1]
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    bot.edit_message_text("⚡ تکایە چاوەڕێ بکە، فایلەکە دادەبەزێنرێت...", chat_id, message_id)
    output_filename = f"media_{chat_id}"
    
    if action == 'vid':
        ydl_opts = {'format': 'best', 'outtmpl': f"{output_filename}.%(ext)s", 'quiet': True}
    else:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f"{output_filename}.%(ext)s",
            'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
            'quiet': True
        }

    downloaded_file = None
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if action == 'aud':
                downloaded_file = f"{output_filename}.mp3"
            else:
                for ext in ['.mp4', '.mkv', '.webm', '.mov']:
                    if os.path.exists(output_filename + ext):
                        downloaded_file = output_filename + ext
                        break
                if not downloaded_file:
                    downloaded_file = filename

        with open(downloaded_file, 'rb') as f:
            if action == 'vid':
                bot.send_video(chat_id, f, caption="🔥 ڤیدیۆکەت بە سەرکەوتوویی داگیرا!")
            else:
                bot.send_audio(chat_id, f, caption="🎵 دەنگەکەت بە سەرکەوتوویی داگیرا!")
        bot.delete_message(chat_id, message_id)
    except Exception as e:
        bot.edit_message_text("❌ لێبووردە، نەمتوانی ئەم لینکە دابەزێنم.", chat_id, message_id)
    finally:
        for ext in ['.mp4', '.mkv', '.webm', '.mp3', '.m4a', '.part']:
            f_path = output_filename + ext
            if os.path.exists(f_path):
                os.remove(f_path)

if __name__ == '__main__':
    print("Bot is running successfully!")
    while True:
        try:
            bot.infinity_polling(timeout=10, long_polling_timeout=5)
        except Exception:
            pass
