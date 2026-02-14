import asyncio
import os
from pyrogram import Client, filters
from yt_dlp import YoutubeDL
from herdcalls import HerdCalls
from herdcalls.types import MediaStream

# ========== ТВОИ ДАННЫЕ ==========
BOT_TOKEN = "BOT_TOKEN"
API_ID = 38362283  # твой API ID
API_HASH = "97d45376ebd54eaf1fdf9fdd1e59ea34"
STRING_SESSION = "AgJJXKsAi_vy1lsa1qpTUmXiuMEGWLytUZgOS9Pii1g8N7U5dGav4bCUYfsae_vPPe2c9TUKT1o7rO5O3x4uZCkJhVIssUXjYU24uS4fNagu59_lcprChA5dMbK3t8wN3Xx1lLAZGx4FR36yNTyfx46Ox7gnccBIYIm3r_25wdbba78jYD2mapIeBqKI9zusDqJAtnU8SxyZ5JgVz6pySS7XEE12lIj6bsraTU48aD_WtbGYleVOmpunQEx9zzWf2-9DAR7F3tzj8ibXj10cptnupe6O4jDDGgvnDIJ2iRtax-WcjA0NzIrhWQalYtjbGPfpkhvXO2XkAThj8WRd6VDCKJHJRQAAAAHvjQQWAA"
# ================================

# Создаем клиентов
bot = Client("music_bot", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)
user = Client("user_session", session_string=STRING_SESSION, api_id=API_ID, api_hash=API_HASH)

# Инициализируем HerdCalls
herd = HerdCalls(user)

# Хранилище для активных вызовов
active_calls = {}

def get_audio_url(youtube_url):
    """Получает прямую ссылку на аудио с YouTube"""
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
            print(f"Ошибка: {e}")
            return None

@bot.on_message(filters.command("start"))
async def start_cmd(_, message):
    await message.reply_text(
        "🎵 **Music Bot с herdcalls**\n\n"
        "**Команды:**\n"
        "/join - подключиться к войсу\n"
        "/play [ссылка] - включить музыку\n"
        "/pause - пауза\n"
        "/resume - продолжить\n"
        "/stop - остановить\n"
        "/leave - отключиться\n\n"
        "**Пример:** /play https://youtu.be/dQw4w9WgXcQ"
    )

@bot.on_message(filters.command("join"))
async def join_vc(_, message):
    chat_id = message.chat.id
    
    try:
        # Подключаемся к голосовому чату
        await herd.join_group_call(chat_id)
        active_calls[chat_id] = True
        await message.reply_text("✅ Подключился к голосовому чату!")
    except Exception as e:
        await message.reply_text(f"❌ Ошибка: {e}\nСначала создай голосовой чат в группе!")

@bot.on_message(filters.command("play"))
async def play_music(_, message):
    if len(message.command) < 2:
        await message.reply_text("❌ Укажи ссылку на YouTube")
        return
    
    url = message.command[1]
    chat_id = message.chat.id
    status = await message.reply_text("🔍 Получаю аудио...")
    
    # Проверяем, подключен ли к войсу
    if chat_id not in active_calls:
        await status.edit_text("❌ Сначала подключись командой /join")
        return
    
    # Получаем ссылку на аудио
    audio_url = await asyncio.to_thread(get_audio_url, url)
    
    if not audio_url:
        await status.edit_text("❌ Не удалось получить аудио")
        return
    
    await status.edit_text("🎵 Включаю в войсе...")
    
    try:
        # Создаем поток для воспроизведения
        stream = MediaStream(audio_url)
        
        # Воспроизводим
        await herd.play(chat_id, stream)
        await status.edit_text("✅ Музыка играет в войсе!")
        
    except Exception as e:
        await status.edit_text(f"❌ Ошибка: {e}")

@bot.on_message(filters.command("pause"))
async def pause_music(_, message):
    chat_id = message.chat.id
    try:
        await herd.pause(chat_id)
        await message.reply_text("⏸ Пауза")
    except:
        await message.reply_text("❌ Не удалось поставить на паузу")

@bot.on_message(filters.command("resume"))
async def resume_music(_, message):
    chat_id = message.chat.id
    try:
        await herd.resume(chat_id)
        await message.reply_text("▶️ Продолжаю")
    except:
        await message.reply_text("❌ Не удалось продолжить")

@bot.on_message(filters.command(["stop", "leave"]))
async def stop_music(_, message):
    chat_id = message.chat.id
    try:
        await herd.leave_group_call(chat_id)
        if chat_id in active_calls:
            del active_calls[chat_id]
        await message.reply_text("⏹ Остановлено и отключился")
    except:
        await message.reply_text("❌ Ошибка отключения")

async def main():
    print("🚀 Запуск музыкального бота с herdcalls...")
    
    # Запускаем клиентов
    await user.start()
    await bot.start()
    
    print("✅ Бот готов к работе!")
    print("📱 Используй /join чтобы подключиться к войсу")
    print("🎵 /play [ссылка] чтобы включить музыку")
    
    # Держим бота активным
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
