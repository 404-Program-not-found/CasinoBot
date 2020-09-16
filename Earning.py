import discord
from discord.ext import commands
import random
import asyncio
import sys
import traceback
import datetime
from pyson import pyson_class as pyson
from Economy import Economy
from CasinoBot import Emoji


class Earning(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.Emoji = Emoji
        self.currency = pyson('currency')
        self.Economy = Economy(self.bot)
        
        

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if hasattr(ctx.command, 'on_error'):
            return
        cog = ctx.cog
        if cog:
            if cog._get_overridden_method(cog.cog_command_error) is not None:
                return

        ignored = (commands.CommandNotFound,)
        error = getattr(error, 'original', error)
        if isinstance(error, ignored):
            return

        if isinstance(error, commands.DisabledCommand):
            embedVar = discord.Embed(
                title=f"{self.bot.get_emoji(self.Emoji.ERROR.value)} Command disabled!",
                color=0xc20000)
            await ctx.author.send(embed=embedVar)

        elif isinstance(error, commands.NoPrivateMessage):
            try:
                embedVar = discord.Embed(
                    title=f"{self.bot.get_emoji(self.Emoji.ERROR.value)} You can only do that in a server!",
                    color=0xc20000)
                await ctx.send(embed=embedVar)
            except discord.HTTPException:
                pass
        elif isinstance(error, commands.BadArgument) or isinstance(error, commands.MissingRequiredArgument):
            embedVar = discord.Embed(
                title=f"{self.bot.get_emoji(self.Emoji.ERROR.value)} Command error, ?help for help!",
                color=0xc20000)
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
            await ctx.send(embed=embedVar)

        else:
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    class Checks():
        async def check_bank(self, ctx, stakes, currency, bot, Emoji):
            if stakes > currency.data[str(ctx.author.id)]:
                embedVar = discord.Embed(
                    title=f"{bot.get_emoji(Emoji.ERROR.value)} You do not have enough money to do this!",
                    color=0xc20000)
                await ctx.send(embed=embedVar)
                return False
            return True

    @commands.command()
    @commands.cooldown(1, 60 * 60 * 24, commands.BucketType.user)
    async def daily(self, ctx):
        ID = str(ctx.message.author.id)
        self.Economy.check_id(ID)
        amount = random.randint(800, 1000)
        self.currency.data[str(ID)] += amount
        self.currency.save()
        await ctx.send(f'''{amount} {self.currency.data["name"]} have been added to {ctx.message.author.mention}'s bank''')

    @daily.error
    async def daily_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            embedvar = discord.Embed(title=f"{self.bot.get_emoji(self.Emoji.ERROR.value)} On cooldown!",
                                     description="Cooldown will remain for "
                                                 + str(datetime.timedelta(seconds=int(error.retry_after))),
                                     color=0xc20000)
            await ctx.send(embed=embedvar)
        else:
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    @commands.command(aliases=['slot'])
    async def slots(self, ctx, stakes: int):
        if not await self.Checks().check_bank(ctx, stakes, self.currency, self.bot, self.Emoji): return
        picks = []
        ID = str(ctx.message.author.id)
        self.Economy.check_id(ID)
        self.currency.data[str(ID)] -= int(stakes)
        msg = await ctx.send(self.Emoji.BLANK.value * 3)
        for i in range(0, 3):
            picks.append(random.choice(self.Emoji.DOTS.value))
            await asyncio.sleep(1.3)
            print(picks)
            await msg.edit(content=str("".join(picks[0:i + 1])) + str(self.Emoji.BLANK.value * (2 - i)))
        repetition = 0
        for element in picks:
            if picks.count(element) == 2:
                repetition = 1.5
                break
            elif picks.count(element) == 3:
                repetition = 2
                break
        self.currency.data[str(ID)] += int(stakes * repetition)
        self.currency.save()
        if repetition == 0:
            await ctx.send(
                f'You have lost {int(stakes)} {self.currency.data["name"]}. Better luck next time!')
            return
        await ctx.send(
            f'You have won {int(stakes * repetition - stakes)} {self.currency.data["name"]}!')

    @commands.command(aliases=['coin', 'cointoss', 'flip'])
    async def toss(self, ctx, choice: str, stakes: int):
        if not await self.Checks().check_bank(ctx, stakes, self.currency, self.bot, self.Emoji) or (choice.lower() != "heads" and choice.lower() != "tails"):
            print("nope, not doing this")
            return
        ID = str(ctx.message.author.id)
        self.Economy.check_id(ID)
        self.currency.data[str(ID)] -= int(stakes)
        face = random.choice(['HEADS', 'TAILS'])
        msg = await ctx.send(self.Emoji.BLANK.value)
        await asyncio.sleep(1.3)
        await msg.edit(content=self.bot.get_emoji(id=self.Emoji[face].value))
        if choice.upper() == face:
            await ctx.send(
                f'You have won {int(stakes)} {self.currency.data["name"]}!')
            self.currency.data[str(ID)] += int(stakes * 2)
            self.currency.save()
            return
        await ctx.send(
            f'You have lost {int(stakes)} {self.currency.data["name"]}. Better luck next time!')
        self.currency.save()

    @commands.command(aliases=['rolldice', 'dice'])
    async def roll(self, ctx, stakes: int):
        if not await self.Checks().check_bank(ctx, stakes, self.currency, self.bot, self.Emoji): return
        ID = str(ctx.message.author.id)
        self.Economy.check_id(ID)
        self.currency.data[str(ID)] -= int(stakes)
        rolls = [random.randint(1, 20), random.randint(0, 20)]
        if rolls[0] <= rolls[1]:
            embedvar = discord.Embed(title="Dice Roll",
                                     description=f'You lost **{int(stakes)}** {self.currency.data["name"]}',
                                     color=0xc20000)
            embedvar.add_field(name=f'**{ctx.message.author.name}**', value=f'Rolled {rolls[0]}', inline=True)
            embedvar.add_field(name=f'**{self.bot.user.name}**', value=f'Rolled {rolls[1]}', inline=True)
            await ctx.send(embed=embedvar)
            self.currency.save()
            return
        self.currency.data[str(ID)] += int(stakes + (rolls[0] - rolls[1]) / 20 * stakes)
        embedvar = discord.Embed(title="Dice Roll",
                                 description=f'Won **{int((rolls[0] - rolls[1]) / 20 * stakes * 2)}** {self.currency.data["name"]}'
                                             f'\n\n Percentage of bet won: {int((rolls[0] - rolls[1]) / 20 * stakes * 2 / stakes * 100)}%',
                                 color=0x00c943)
        embedvar.add_field(name=f'**{ctx.message.author.name}**', value=f'Rolled {rolls[0]}', inline=True)
        embedvar.add_field(name=f'**{self.bot.user.name}**', value=f'Rolled {rolls[1]}', inline=True)
        await ctx.send(embed=embedvar)
        self.currency.save()

def setup(bot):
    bot.add_cog(Earning(bot))