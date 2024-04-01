import discord
import random
import requests
from discord.ext import commands
from config import settings
from nacl import *
from asyncio import sleep
import pafy
from PIL import Image, ImageDraw, ImageFont
from discord import FFmpegPCMAudio, PCMVolumeTransformer
from discord.voice_client import VoiceClient
import yt_dlp
import matplotlib.pyplot as plt
from collections import Counter
from tabulate import tabulate

intents = discord.Intents().all()
bot = commands.Bot(command_prefix=settings['prefix'], intents=intents, )
starter_encouragements = [
    "Добро пожаловать!"
]
yt_dl_opts = {'format': 'bestaudio/best', 'outtmpl': 'audio_file.mp3'}
ytdl = yt_dlp.YoutubeDL(yt_dl_opts)
ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'}


@bot.command()
async def stats(ctx):
    guild = ctx.guild
    message_counts = Counter()
    for channel in guild.text_channels:
        async for message in channel.history(limit=None):
            if not message.author.bot:
                message_counts[message.author.name] += 1
    users = list(message_counts.keys())
    message_nums = list(message_counts.values())
    plt.bar(users, message_nums)
    plt.xlabel('Пользователи')
    plt.ylabel('Количество сообщений')
    plt.title('Гистограмма количества сообщений по пользователям')
    plt.savefig('histogram.png')
    await ctx.send(file=discord.File('histogram.png'))
    plt.clf()
    plt.close()


@bot.command()
async def stock_daily(ctx, *, message: str):
    main_data = []
    corp = message
    await ctx.send('```\nВНИМАНИЕ! КИРИЛЛ ТРЕЩЁВ \n```')
    url = 'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=' + corp + '&interval=5min&apikey=U6P7CXOHBOMKUUQ7'
    r = requests.get(url)
    data = r.json()
    last_update = data['Meta Data']['3. Last Refreshed']
    corporation = data['Meta Data']['2. Symbol']
    interval = data['Meta Data']['4. Interval']
    time_zone = data['Meta Data']['6. Time Zone']
    w = data['Time Series (5min)']
    await ctx.send('```\nПоследнее обновление: ' + str(last_update) + '\n' +
                   'Название акции: ' + str(corporation) + '\n' +
                   'Интервал: ' + str(interval) + '\n' +
                   'Часовой пояс: ' + str(time_zone) + '\n```')
    for k in w:
        main_data.append([float(w[k]['1. open'][:-2]), k])
    main_data = main_data[::-1]
    headers = ["Price", "Time"]
    rows_per_message = 20
    chunks = [main_data[i:i+rows_per_message] for i in range(0, len(main_data), rows_per_message)]
    for chunk in chunks:
        table = tabulate(chunk, headers=headers, tablefmt="grid")
        await ctx.send(f"```\n{table}\n```")
    prices = [main_data[data][0] for data in range(0, len(main_data), 3)]
    times = [main_data[data][1] for data in range(0, len(main_data), 3)]
    plt.plot(times, prices)
    plt.xlabel('Time')
    plt.ylabel('Price')
    plt.title('Dollar Exchange Rate ' + str(corp))
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('graph.png')
    await ctx.send(file=discord.File('graph.png'))
    plt.show()


bot.run(settings['token'])
