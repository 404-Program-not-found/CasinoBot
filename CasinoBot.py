from discord.ext import commands
import os
from enum import Enum
from pyson import pyson_class as pyson

currency = pyson('currency')

if 'name' not in currency.data:
    currency.data['name'] = 'dollars'

startup_extensions = ["Economy", "Earning", "Admin", "Banking"]

class Emoji(Enum):
    YES = 749126458164641813
    NO = 749126458521157632
    ERROR = 751553187453992970
    OKAY = 751553187529490513
    WARNING = 751653673628860476
    HEADS = 755354407167721522
    TAILS = 755354408732196875
    DOTS = ["⚪", "🔴", "🔵", "🟤", "🟣", "🟢", "🟡", "🟠"]
    BLANK = "⚫"


bot = commands.Bot(command_prefix="?")

@commands.is_owner()
@bot.command()
async def load(ctx, extension_name : str):
    try:
        bot.load_extension(extension_name)
    except (AttributeError, ImportError) as e:
        await ctx.send("```py\n{}: {}\n```".format(type(e).__name__, str(e)))
        return
    await ctx.send("{} loaded.".format(extension_name))

@commands.is_owner()
@bot.command()
async def reload(ctx, extension_name : str):
    bot.unload_extension(extension_name)
    try:
        bot.load_extension(extension_name)
    except (AttributeError, ImportError) as e:
        await ctx.send("```py\n{}: {}\n```".format(type(e).__name__, str(e)))
        return
    await ctx.send("{} reloaded.".format(extension_name))

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

if __name__ == "__main__":
    for extension in startup_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            print('Failed to load extension {}\n{}'.format(extension, exc))

    bot.run(os.environ['casniotoken'])
