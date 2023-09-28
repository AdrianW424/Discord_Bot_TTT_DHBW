import os
import discord
from dotenv import load_dotenv
from urllib.error import HTTPError

import xoyondo_wrapper as xyw

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
client = discord.Client(intents=intents)

xoyow = xyw.Xoyondo_Wrapper("https://xoyondo.com/dp/tDKDAFzoWdtzhBR/hlro3gVHMq")

url_storage = {}

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if message.content.startswith('!help'):
        await message.channel.send('Commands:\n!help\n!set_url <url>\n!reset_poll <dates>\n!chart')

    if message.content.startswith('!set_url'):
        _, url = message.content.split(' ', 1)
        try:
            xoyow.set_url(url)
            await message.channel.send(f'Changed URL to: {url}')
        except Exception as e:
            await message.channel.send(f'Error: {e}')

    elif message.content.startswith('!reset_poll'):
        _, dates = message.content.split(' ', 1)
        try:
            messages = xoyow.reset_poll(dates)
            await message.channel.send(f'Poll was reset')
        except Exception as e:
            await message.channel.send(f'Error: {e}')
            
    elif message.content.startswith('!chart'):
        try:
            buf, messages = xoyow.create_plot()
            await message.channel.send(file=discord.File(buf, 'chart.png'))
        except Exception as e:
            await message.channel.send(f'Error: {e}')
    else:
        await message.channel.send('Unknown command')

client.run(TOKEN)
