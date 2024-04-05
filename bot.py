from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from pytube import YouTube
from aiogram.types import Video
import os


# Создаем объект бота
bot = Bot('6994323466:AAFcpEnwlkyE1SZ_Goq5I_C9PCS8nBqC6FI')
dp = Dispatcher(bot)

# Функция при запуске бота
async def on_startup(_):
    print("Бот запущен!")

# Обработчик команды /start
@dp.message_handler(commands='start')
async def cmd_start(message: types.Message):
    await message.answer("Привет! Я бот для скачивания видео с YouTube. Для начала отправь мне команду /download.")

link = None

# Обработчик команды /download
@dp.message_handler(commands='download')
async def cmd_download(message: types.Message):
    await message.answer("Введите ссылку на видео:")

# Обработчик текстовых сообщений для ссылки на видео
@dp.message_handler(lambda message: message.text.startswith("http"))
async def process_video_link(message: types.Message):
    global link
    link = message.text
    yt = YouTube(message.text)
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    
    # Создаем множество для хранения уникальных разрешений и форматов с аудио
    unique_formats_with_audio = set()
    
    # Итерируемся по каждому потоку видео и добавляем уникальные разрешения и форматы с аудио
    for stream in yt.streams:
        if stream.resolution and stream.includes_audio_track:
            data = f'{stream.resolution} | {stream.mime_type}'
            unique_formats_with_audio.add(data)
    
    # Добавляем уникальные разрешения и форматы с аудио на клавиатуру
    for format_data in unique_formats_with_audio:
        kb.add(KeyboardButton(format_data))
    
    await message.answer("Выберите разрешение с работающим звуком:", reply_markup=kb)

# Обработчик текстовых сообщений с разрешениями
@dp.message_handler(lambda message: message.text and '|' in message.text)
async def process_resolution_selection(message: types.Message):
    try:
        # Разбиваем сообщение на разрешение и тип видео
        resolution, mime_type = message.text.split('|')
        
        global link
        video_link = link
        
        if video_link:
            # Создаем объект YouTube для видео
            yt = YouTube(video_link)
            
            # Находим нужный поток видео по разрешению и типу видео
            stream = yt.streams.filter(res=resolution.strip(), mime_type=mime_type.strip()).first()
            
            # Отправляем сообщение о начале загрузки видео
            await message.answer("Началась загрузка видео на сервер!")
            
            # Скачиваем видео
            video_file_path = stream.download()
            
            await message.answer("Видео успешно загружено и отправляется вам...")
            # Отправляем видео пользователю и удаляем клавиатуру
            await message.answer_video(video=open(video_file_path, 'rb'), reply_markup=ReplyKeyboardRemove())
            
            # Удаляем видео с компьютера после отправки
            os.remove(video_file_path)
            
        else:
            await message.answer("Не удалось определить ссылку на видео.")
    except Exception as e:
        await message.answer("Произошла ошибка при скачивании и отправке видео: " + str(e))

if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
