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
    'help': 'Zeigt diese Nachricht.',
    'toggle_extra_info': 'Schaltet zusätzliche Infos für Befehle um.',
    'set_url <url>': 'Setzt die URL der Umfrage auf <url>.',
    'reset_poll <dates>': 'Setzt die Umfrage auf die Daten <dates> zurück.',
    'chart': 'Erstellt ein Diagramm der aktuellen Umfrage.',
    'special': 'Überraschung!'
}
###############

@bot.event
async def on_ready():
    print(f'Eingeloggt als {bot.user}')

@bot.command(name='help')
async def help_c(ctx):
    output = 'Befehle:\n'
    for command, description in possible_commands.items():
        output += f'> {COMMAND_PREFIX}{command}: {description}\n'
    await ctx.send(output)
@help_c.error
async def help_c_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(':stop_sign: **Fehler** :stop_sign: **-** Parameter ist erforderlich!')
    
@bot.command(name='toggle_extra_info')
async def toggle_extra_info_c(ctx):
    global extra_info
    extra_info = not extra_info
    await ctx.send(f'Zusätzliche Infos sind jetzt {"aktiviert" if extra_info else "deaktiviert"}')
@toggle_extra_info_c.error
async def toggle_extra_info_c_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(':stop_sign: **Fehler** :stop_sign: **-** Parameter ist erforderlich!')
    
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
            await ctx.send(f'URL geändert zu: {url}')
    except Exception as e:
        await ctx.send(f':stop_sign: **Fehler** :stop_sign: **-** {e}')
@set_url_c.error
async def set_url_c_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(':stop_sign: **Fehler** :stop_sign: **-** URL ist erforderlich!')
        
@bot.command(name='reset_poll')
async def reset_poll_c(ctx, dates:str, print_link:bool=True):
    try:
        _messages = xoyow.reset_poll(dates)
        
        if extra_info:
            output = ''
            for _message in _messages:
                output += f'> {_message}\n'
            await ctx.send(output)
        else:
            if print_link:
                await ctx.send(f'@everyone Die Umfrage wurde zurückgesetzt. Unter folgendem Link könnt ihr an der neuen Umfrage teilnehmen: {xoyow.get_url(False)}')
            else:
                await ctx.send(f'Die Umfrage wurde zurückgesetzt.')
    except Exception as e:
        await ctx.send(f':stop_sign: **Fehler** :stop_sign: **-** {e}')
@reset_poll_c.error
async def reset_poll_c_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(':stop_sign: **Fehler** :stop_sign: **-** Neue Daten sind erforderlich!')        
        
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
        await ctx.send(f':stop_sign: **Fehler** :stop_sign: **-** {e}')
@chart_c.error
async def chart_c_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(':stop_sign: **Fehler** :stop_sign: **-** Parameter ist erforderlich!')   
        
@bot.command(name='special')
async def special_c(ctx):
    await ctx.send('Jannik & Natalie -> :heart: :cupid: :smiling_face_with_3_hearts:')
@special_c.error
async def special_c_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(':stop_sign: **Fehler** :stop_sign: **-** Parameter ist erforderlich!')

bot.run(TOKEN)