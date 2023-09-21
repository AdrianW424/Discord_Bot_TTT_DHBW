import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import requests

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
client = discord.Client(intents=intents)

url_storage = {}

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!store_url'):
        _, url = message.content.split(' ', 1)
        url_storage[message.guild.id] = url
        await message.channel.send(f'URL stored: {url}')

    elif message.content.startswith('!crawl_url'):
        if message.guild.id in url_storage:
            url = url_storage[message.guild.id]
            await message.channel.send(f'Stored URL: {url}')
        else:
            await message.channel.send('No URL stored.')

client.run(TOKEN)
