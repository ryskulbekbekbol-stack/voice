import os
import asyncio
from pyrogram import Client, filters
from yt_dlp import YoutubeDL
from pytgcalls import PyTgCalls
from pytgcalls.types.stream import StreamAudio

# ========== ТВОИ ДАННЫЕ БЕРУТСЯ ИЗ ПЕРЕМЕННЫХ СРЕДЫ ==========
BOT_TOKEN = os.environ.get("BOT_TOKEN")
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH")
STRING_SESSION = os.environ.get("STRING_SESSION")
# =============================================================

# Проверка, что все данные есть
if not BOT_TOKEN or not API_ID or not API_HASH or not STRING_SESSION:
    print("❌ Ошибка: Не все переменные окружения заданы!")
    exit(1)

print("🚀 Запуск музыкального бота на Render...")

# Создаем клиентов
bot = Client("music_bot", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)
user = Client("user_session", session_string=STRING_SESSION, api_id=API_ID, api_hash=API_HASH)

# Голосовой модуль
call = PyTgCalls(user)

# Функция для получения ссылки на аудио с YouTube
def get_audio_url(youtube_url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
    }
    with YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(youtube_url, download=False)
            # Ищем формат только с аудио
            for f in info['formats']:
                if f.get('acodec') != 'none' and f.get('vcodec') == 'none':
                    return f['url']
            return info['url']
        except Exception as e:
            print(f"Ошибка получения аудио: {e}")
            return None

# Команда /start
@bot.on_message(filters.command("start"))
async def start_cmd(_, message):
    await message.reply_text(
        "🎵 **Music Bot**\n\n"
        "Команды:\n"
        "/join - подключиться к войсу\n"
        "/play [ссылка] - включить музыку\n"
        "/pause - пауза\n"
        "/resume - продолжить\n"
        "/stop - остановить\n"
        "/leave - отключиться"
    )

# Команда /join
@bot.on_message(filters.command("join"))
async def join_vc(_, message):
    try:
        # Подключаемся к голосовому чату
        await call.join_group_call(
            message.chat.id,
            StreamAudio(
                path="https://docs.evostream.com/sample_content/assets/sintel1m.mp3",
            ),
        )
        await message.reply_text("✅ Подключился к голосовому чату!")
    except Exception as e:
        await message.reply_text(f"❌ Ошибка: {e}")

# Команда /play
@bot.on_message(filters.command("play"))
async def play_music(_, message):
    if len(message.command) < 2:
        await message.reply_text("❌ Укажи ссылку на YouTube")
        return
    
    url = message.command[1]
    status = await message.reply_text("🔍 Получаю аудио...")
    
    # Получаем ссылку на аудио в отдельном потоке
    audio_url = await asyncio.to_thread(get_audio_url, url)
    
    if not audio_url:
        await status.edit_text("❌ Не удалось получить аудио")
        return
    
    await status.edit_text("🎵 Включаю в войсе...")
    
    try:
        await call.play(message.chat.id, StreamAudio(path=audio_url))
        await status.edit_text("✅ Музыка играет!")
    except Exception as e:
        await status.edit_text(f"❌ Ошибка: {e}")

# Команда /pause
@bot.on_message(filters.command("pause"))
async def pause_music(_, message):
    try:
        await call.pause(message.chat.id)
        await message.reply_text("⏸ Пауза")
    except:
        await message.reply_text("❌ Не удалось поставить на паузу")

# Команда /resume
@bot.on_message(filters.command("resume"))
async def resume_music(_, message):
    try:
        await call.resume(message.chat.id)
        await message.reply_text("▶️ Продолжаю")
    except:
        await message.reply_text("❌ Не удалось продолжить")

# Команда /stop или /leave
@bot.on_message(filters.command(["stop", "leave"]))
async def stop_music(_, message):
    try:
        await call.leave_group_call(message.chat.id)
        await message.reply_text("⏹ Отключился")
    except:
        await message.reply_text("❌ Ошибка отключения")

# Главная функция
async def main():
    await user.start()
    await bot.start()
    await call.start()
    
    print("✅ Бот готов к работе!")
    print(f"🤖 @{(await bot.get_me()).username}")
    
    # Держим бота активным
    await asyncio.Event().wait()

# Запуск
if __name__ == "__main__":
    asyncio.run(main())
