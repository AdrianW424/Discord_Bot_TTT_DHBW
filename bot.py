import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import xoyondo_wrapper as xyw

### globals ###
url_storage = {}
extra_info = False
COMMAND_PREFIX = '!tf_'

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents, help_command=None)

xoyow = xyw.Xoyondo_Wrapper("https://xoyondo.com/dp/tDKDAFzoWdtzhBR/hlro3gVHMq")

possible_commands = {
    'help': 'Shows this message.',
    'toggle_extra_info': 'Toggles extra info for commands.',
    'set_url <url>': 'Sets the URL of the poll to <url>.',
    'reset_poll <dates>': 'Resets the poll to the dates <dates>.',
    'chart': 'Creates a chart of the current poll.'
}
###############

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.command(name='help')
async def help_c(ctx):
    output = 'Commands:\n'
    for command, description in possible_commands.items():
        output += f'> {COMMAND_PREFIX}{command}: {description}\n'
    await ctx.send(output)
@help_c.error
async def help_c_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('**Error -** Parameter is required!')
    
@bot.command(name='toggle_extra_info')
async def toggle_extra_info_c(ctx):
    global extra_info
    extra_info = not extra_info
    await ctx.send(f'Extra info is now {"on" if extra_info else "off"}')
@toggle_extra_info_c.error
async def toggle_extra_info_c_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('**Error -** Parameter is required!')
    
@bot.command(name='set_url')
async def set_url_c(ctx, url:str):
    try:
        _messages = xoyow.set_url(url)
        
        if extra_info:
            output = ''
            for _message in _messages:
                output += f'> {_message}\n'
            await ctx.send(output)
        else:
            await ctx.send(f'Changed URL to: {url}')
    except Exception as e:
        await ctx.send(f'**Error -** {e}')
@set_url_c.error
async def set_url_c_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('**Error -** URL is required!')
        
@bot.command(name='reset_poll')
async def reset_poll_c(ctx, dates:str):
    try:
        _messages = xoyow.reset_poll(dates)
        
        if extra_info:
            output = ''
            for _message in _messages:
                output += f'> {_message}\n'
            await ctx.send(output)
        else:
            await ctx.send(f'Poll was reset. You ')
    except Exception as e:
        await ctx.send(f'**Error -** {e}')
@reset_poll_c.error
async def reset_poll_c_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('**Error -** New dates are required!')        
        
@bot.command(name='chart')
async def chart_c(ctx):
    try:
        buf, _messages = xoyow.create_plot()
        
        if extra_info:
            output = ''
            for _message in _messages:
                output += f'> {_message}\n'
            await ctx.send(output)
        else:
            await ctx.send(file=discord.File(buf, 'chart.png'))
    except Exception as e:
        await ctx.send(f'**Error -** {e}')
@chart_c.error
async def chart_c_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('**Error -** Parameter is required!')            

bot.run(TOKEN)
