import datetime
import discord
from discord.ext import commands
from dotenv import load_dotenv
from fuzzywuzzy import fuzz
import os
import pytz
import xoyondo_wrapper as xyw

### globals ###
url_storage = {}
extra_info = False
COMMAND_PREFIX = '!tf_'

load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents, help_command=None)

XOYONDO_URL = os.getenv('XOYONDO_URL')

xoyow = xyw.Xoyondo_Wrapper(XOYONDO_URL, print_messages=False)

possible_commands = {
    'help': 'Zeigt diese Nachricht.',
    'toggle_extra_info': 'Schaltet zusätzliche Infos für Befehle um.',
    'set_url <url>': 'Setzt die URL der Umfrage auf <url>.',
    'reset_poll <dates>': 'Setzt die Umfrage auf die Daten <dates> zurück.',
    'chart': 'Erstellt ein Diagramm der aktuellen Umfrage.',
    'special': 'Überraschung!',
    'special_for_jannik': 'Überraschung für Jannik! |**Notiz vom Entwickler: Das ist für dich Jannik :heart:**|',
    'erase': 'Löscht den Command des Users und die dazugehörige Antwort des Bots.'
}
###############

### functions ###
def get_current_week(offset=0):
    day = datetime.date.today() + datetime.timedelta(days=7*offset)
    year, week, _ = day.isocalendar()
    return f'{year}/{week}'

def get_current_month(offset=0):
    day = datetime.date.today() + datetime.timedelta(days=30*offset)
    year, month = day.year, day.month
    return f'{year}/{month}'
#################

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
        
        # open file .env and change the line with XOYONDO_URL to XOYONDO_URL = url
        with open('.env', 'r') as f:
            lines = f.readlines()
        with open('.env', 'w') as f:
            for line in lines:
                if line.startswith('XOYONDO_URL'):
                    f.write(f'XOYONDO_URL = {url}\n')
                else:
                    f.write(line)
        
        if extra_info:
            output = ''
            for _message in _messages:
                output += f'> {_message}\n'
            await ctx.send(output)
        
        await ctx.send(f'URL geändert zu: <{url}>')
    except Exception as e:
        await ctx.send(f':stop_sign: **Fehler** :stop_sign: **-** {e}')
@set_url_c.error
async def set_url_c_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(':stop_sign: **Fehler** :stop_sign: **-** URL ist erforderlich!')
        
@bot.command(name='reset_poll')
async def reset_poll_c(ctx, dates:str, print_link:bool=True):
    try:
        messages = []
        if dates.startswith('week_'):
            year_week = dates.split('week_')[1]
            
            if year_week == 'current':
                year_week = get_current_week()
            elif year_week == 'next':
                year_week = get_current_week(offset=1)
                
            dates, _messages = xoyow.get_dates_for_week(year_week)
            messages.extend(_messages)
        elif dates.startswith('month_'):
            year_month = dates.split('month_')[1]
            
            if year_month == 'current':
                year_month = get_current_month()
            elif year_month == 'next':
                year_month = get_current_month(offset=1)
                
            dates, _messages = xoyow.get_dates_for_month(year_month)
            messages.extend(_messages)
            
        _messages = xoyow.reset_poll(dates)
        messages.extend(_messages)
        
        if extra_info:
            output = ''
            for message in messages:
                output += f'> {message}\n'
            await ctx.send(output)

        if print_link:
            await ctx.send(f'@everyone Die Umfrage wurde zurückgesetzt. Unter folgendem Link könnt ihr an der neuen Umfrage teilnehmen: <{xoyow.get_url(False)}>')
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
        
        for chart in buf:
            await ctx.send(file=discord.File(chart, 'chart.png'))
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
        
@bot.command(name='special_for_jannik')
async def special_for_jannik_c(ctx):
    await ctx.send('Adrian & Pauline -> :heart: :cupid: :smiling_face_with_3_hearts:')
@special_for_jannik_c.error
async def special_for_jannik_c_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(':stop_sign: **Fehler** :stop_sign: **-** Parameter ist erforderlich!')


@bot.command(name='erase')
async def erase_c(ctx, text:str, time_delta:int=1, long_answer:bool=False):
    try:
        # List to hold messages to be deleted
        messages_to_delete = []

        # Fetch the recent messages
        recent_messages = [recent_message async for recent_message in ctx.channel.history(limit=100)]
        print("Count of messages in channel: ", len(recent_messages))

        for message in recent_messages:
            # Check time delta first
            utc_now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
            print(f"Message has been created {utc_now - message.created_at} ago")
            if (utc_now - message.created_at).seconds > time_delta*60:
                break
            
            print("text: ", text)
            print(f"Message content: {message.content}")

            # Check if the message is similar to the text string using fuzzy matching
            print("Message likely to be deleted:", fuzz.ratio(text.lower(), message.content.lower()))
            if fuzz.ratio(text.lower(), message.content.lower()) >= 80:  # you can adjust the threshold as needed
                messages_to_delete.append(message)

        # Delete the collected messages
        for msg in messages_to_delete:
            await msg.delete()

        # Send a confirmation message and then delete it after a few seconds
        if long_answer:
            await ctx.send(f'{len(messages_to_delete)} message(s) similar to `{text}` from the past {time_delta} minute(s) {"has" if len(messages_to_delete) == 1 else "have"} been deleted.')
        else:
            await ctx.send(f'{len(messages_to_delete)} message(s) from the past {time_delta} minute(s) {"has" if len(messages_to_delete) == 1 else "have"} been deleted.')

    except Exception as e:
        await ctx.send(f':stop_sign: **Fehler** :stop_sign: **-** {e}')

@erase_c.error
async def erase_c_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(':stop_sign: **Fehler** :stop_sign: **-** Parameter ist erforderlich!')
    

bot.run(DISCORD_TOKEN)