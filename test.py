import random

import discord
import matplotlib.pyplot as plt
import requests
import yt_dlp
from PIL import Image, ImageDraw, ImageFont
from discord.ext import commands
import sqlite3

from config import settings

intents = discord.Intents().all()
from collections import Counter

bot = commands.Bot(command_prefix=settings['prefix'], intents=intents, )


starter_encouragements = [
    "Добро пожаловать!"
]
yt_dl_opts = {'format': 'bestaudio/best', 'outtmpl': 'audio_file.mp3'}
ytdl = yt_dlp.YoutubeDL(yt_dl_opts)

ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'}


with sqlite3.connect("database.db") as db:
    cursor = db.cursor()
    query = """
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY,
        us_id VARCHAR
        num_page INTEGER
    );
    CREATE TABLE IF NOT EXISTS quote_all(
        id INTEGER PRIMARY KEY,
        quote VARCHAR
    )
    """
    cursor.executescript(query)


@bot.event
async def on_ready():
    print('Бот подключился к серверу Discord')


@bot.command()
async def stats(ctx):
    # Получаем объект сервера по контексту команды
    guild = ctx.guild

    # Создаем словарь для подсчета количества сообщений пользователей
    message_counts = Counter()

    # Перебираем все текстовые каналы на сервере
    for channel in guild.text_channels:
        async for message in channel.history(limit=None):
            # Проверяем, является ли автор сообщения пользователем, а не ботом
            if not message.author.bot:
                message_counts[message.author.name] += 1

    # Получаем данные для гистограммы
    users = list(message_counts.keys())
    message_nums = list(message_counts.values())

    # Создаем гистограмму
    plt.bar(users, message_nums)
    plt.xlabel('Пользователи')
    plt.ylabel('Количество сообщений')
    plt.title('Гистограмма количества сообщений по пользователям')

    # Сохраняем гистограмму в файл
    plt.savefig('histogram.png')

    # Отправляем гистограмму в чат
    await ctx.send(file=discord.File('histogram.png'))

    # Удаляем временный файл гистограммы
    plt.clf()
    plt.close()


async def download_audio(url):
    ytdl = youtube_dl.YoutubeDL(yt_dl_opts)
    info = await ytdl.extract_info(url, download=True)
    audio_filename = ytdl.prepare_filename(info)  # Получаем имя сохраненного аудио-ф


@bot.command()
async def weather(ctx, *, message: str):
    city = message
    url = 'https://api.openweathermap.org/data/2.5/weather?q=' + city + '&units=metric&lang=ru&appid=79d1ca96933b0328e1c7e3e7a26cb347'
    weather_data = requests.get(url).json()
    temperature = round(weather_data['main']['temp'])
    temperature_feels = round(weather_data['main']['feels_like'])
    speed_wind = weather_data['wind']['speed']
    descript = weather_data['weather'][0]['description']
    humidity = weather_data['main']['humidity']
    pressure = (int(weather_data['main']['pressure']) / 133.3) * 100
    await ctx.message.delete()
    recomendation = ''
    qq = f'\nСейчас в городе {city} {str(temperature)} °C\n\nОщущается как {str(temperature_feels)}°C\n\nВетер со скоростью {str(speed_wind)} м/с\n\nОписание: {descript}\n\nВлажность {humidity} % \n\nАтмосферное давление {str(round(pressure))} мм.рт.ст.\n\nРекомендации: {recomendation}\n'
    image = Image.open("3vMirNVwYS8.jpeg")
    pixels = image.load()
    x, y = image.size
    for i in range(100, x - 100):
        for j in range(200, y - 200):
            pixels[i, j] = (255, 255, 255)
    font = ImageFont.truetype("/Users/imac/Library/Fonts/MullerBlack.ttf", 32)
    drawer = ImageDraw.Draw(image)
    drawer.text((450, 150), qq, font=font, fill='black')
    image.save('new.jpeg')
    await ctx.send(file=discord.File('new.jpeg'))


@bot.event
async def on_message(message):
    if "цитату" in message.content.lower() or "цитата" in message.content.lower() or "quote" in message.content.lower():
        await bot.process_commands(message)
        w = []
        parts = message.content.split(' ')
        try:
            sqlite_connection = sqlite3.connect('database.db')
            cursor1 = sqlite_connection.cursor()
            print("Подключен к SQLite")

            sqlite_select_query = """SELECT * from quote_all"""
            cursor1.execute(sqlite_select_query)
            records = cursor1.fetchall()
            for row in records:
                w.append(row[1])
            await message.channel.send('```\n' + random.choice(w) + '\n```')
            cursor1.close()
        except sqlite3.Error as error:
            await message.channel.send("Ошибка при работе с SQLite", error)
        finally:
            if sqlite_connection:
                sqlite_connection.close()
                print("Соединение с SQLite закрыто")
    await bot.process_commands(message)


@bot.command()
async def hello(ctx):
    if str(ctx.message.author) == "lazarustars":
        await ctx.send("```\nХаха\nIf you need help write - !helpme\n```")
    else:
        await ctx.send("```\nНе хаха\nIf you need help write - !helpme\n```")


@bot.command()
async def helpme(ctx):
    await ctx.send(
        "```\nПривет! Я могу рассказать тебе о моих разработчиках Lancer и LAZARUS, просто пропиши команды - !whoislancer или !whoislazarus \n Так же могу пожелать тебе удачи на экзаменах - !examsoon \nНапиши слово **цитату, цитата, quote** и узнаешь интересные высказывания от интереных людей\n!weather + название города - расскажет тебе о погоде в твоем городе в данный момент\nНо я вcё ещё на этапе разработки, поэтому немногословен\n```")


@bot.command()
async def whoislancer(ctx):
    await ctx.send(
        "```\nLancer - мой создатель и участник команды разработчиков GLS\nIf you need help write - !helpme\n```")


@bot.command()
async def whoislazarus(ctx):
    await ctx.send(
        "```\nLAZARUS - мой создатель и участник команды разработчиков GLS\nIf you need help write - !helpme\n```")


@bot.command()
async def play(ctx, url: str):
    try:
        voice_client = ctx.guild.voice_client
        if not voice_client:
            voice_channel = ctx.author.voice.channel
            voice_client = await voice_channel.connect()

        voice_client.encoder_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                                        'options': '-vn'}
        info = ytdl.extract_info(url, download=False)
        audio_filename = ytdl.prepare_filename(info)
        audio_url = info["url"]
        voice_client.play(discord.FFmpegPCMAudio(audio_url, **voice_client.encoder_options))

    except AttributeError:
        await ctx.send(f"Меня тут нет")
    except UnboundLocalError:
        await ctx.send(f"Песня уже играет, подожди либо пропиши команду !stop")
    except Exception as e:
        logging.error(f"Ошибка в {ctx.command}: {e}")


@bot.command()
async def pause(ctx):
    voice_client = ctx.guild.voice_client
    if voice_client and voice_client.is_playing():
        voice_client.pause()
        await ctx.send(f"Я остановился, {ctx.message.author.mention}.")
    else:
        await ctx.send(f"песню для начала включи, {ctx.message.author.mention}.")


@bot.command()
async def resume(ctx):
    voice_client = ctx.guild.voice_client
    if voice_client:
        voice_client.resume()
        await ctx.send(f"Хорошо, возвращаю {ctx.message.author.mention}.")
    else:
        await ctx.send(f"Песню включи {ctx.message.author.mention}.")


@bot.command()
async def stop(ctx):
    try:
        voice_client = ctx.voice_client
        await voice_client.disconnect()
    except:
        await ctx.send(f"Стоп {ctx.message.author.mention}.")


import asyncio


@bot.command()
async def countmessage(ctx, username: str):
    user = discord.utils.get(ctx.guild.members, name=username)

    if user is None:
        await ctx.send(f"Пользователь {username} не найден.")
        return

    message_count = 0
    channels = ctx.guild.text_channels

    async def count_messages(channel):
        nonlocal message_count
        async for message in channel.history(limit=None):
            if message.author == user:
                message_count += 1

    # Concurrently gather results from multiple coroutines
    await asyncio.gather(*[count_messages(channel) for channel in channels])

    await ctx.send(f"Количество сообщений пользователя {username}: {message_count}")


@bot.command()
async def first_set(ctx):
    if str(ctx.message.author) == "lazarustars":
        q = []
        guild = bot.get_guild(1120722000655159336)
        f = list(str(guild.members)[27:-3].split())
        for i in f:
            if len(i) > 5 and i[:4] == 'name':
                if i == "name='Secret":
                    q.append("name='Secret Project")
                else:
                    q.append(i)
        q = list(set(q))
        q.remove("name='Сервер")
        await ctx.send(q)


bot.run(settings['token'])
