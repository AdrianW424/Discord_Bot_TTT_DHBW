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

commands = {
    'help': 'Shows this message.',
    'toggle_extra_info': 'Toggles extra info for commands.',
    'set_url <url>': 'Sets the URL of the poll to <url>.',
    'reset_poll <dates>': 'Resets the poll to the dates <dates>.',
    'chart': 'Creates a chart of the current poll.'
}

extra_info = False

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if message.content.startswith('!tf_help'):
        output = 'Commands:\n'
        for command, description in commands.items():
            output += f'> !tf_{command}: {description}\n'
        await message.channel.send(output)
        
    if message.content.startswith('!tf_toggle_extra_info'):
        global extra_info
        extra_info = not extra_info
        await message.channel.send(f'Extra info is now {"on" if extra_info else "off"}')

    if message.content.startswith('!tf_set_url'):
        try:
            _, url = message.content.split(' ', 1)
            try:
                _messages = xoyow.set_url(url)
                
                if extra_info:
                    output = ''
                    for _message in _messages:
                        output += f'> {_message}\n'
                    await message.channel.send(output)
                else:
                    await message.channel.send(f'Changed URL to: {url}')
            except Exception as e:
                await message.channel.send(f'**Error -** {e}')
        except Exception as e:
            await message.channel.send(f'**Error -** No parameters given.')

    elif message.content.startswith('!tf_reset_poll'):
        try:
            _, dates = message.content.split(' ', 1)
            try:
                _messages = xoyow.reset_poll(dates)
                
                if extra_info:
                    output = ''
                    for _message in _messages:
                        output += f'> {_message}\n'
                    await message.channel.send(output)
                else:
                    await message.channel.send(f'Poll was reset')
            except Exception as e:
                await message.channel.send(f'**Error -** {e}')
        except Exception as e:
            await message.channel.send(f'**Error -** No parameters given.')
            
    elif message.content.startswith('!tf_chart'):
        try:
            buf, _messages = xoyow.create_plot()
            
            if extra_info:
                output = ''
                for _message in _messages:
                    output += f'> {_message}\n'
                await message.channel.send(output)
            else:
                await message.channel.send(file=discord.File(buf, 'chart.png'))
        except Exception as e:
            await message.channel.send(f'**Error -** {e}')

client.run(TOKEN)
