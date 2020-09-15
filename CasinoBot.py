import discord
from discord.ext import commands
import random
import asyncio
import re
import sqlite3
import itertools
import traceback
from enum import Enum
import datetime
from pyson import pyson_class as pyson

currency = pyson('currency')

if 'name' not in currency.data:
    currency.data['name'] = 'dollars'


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


class Economy(commands.Cog):
    # Migrated to 1.0 and changed from https://github.com/stroupbslayen/Other-Discord-Bots-async/tree/master/Currency
    class Decorators(object):
        @classmethod
        def is_approved(self):
            pass

    def check_id(self, ID):
        if str(ID) not in currency.data:
            currency.data[str(ID)] = 0
            currency.save()

    @commands.is_owner()
    @commands.command()
    async def currency_type(self, ctx, ntype: str = 'dollars'):
        ''': Change name of your currency'''
        ptype = currency.data['name']
        currency.data['name'] = ntype
        currency.save()
        await ctx.send(f'The economy type has been changed from **{ptype}** to **{ntype}**')

    @commands.is_owner()
    @commands.command(pass_context=True)
    async def add(self, ctx, amount: int = 0, member: discord.Member = None):
        ''': Add points/currency to a member's bank'''
        ID = str(member.id)
        self.check_id(ID)
        currency.data[str(ID)] += amount
        currency.save()
        await ctx.send(f'''{amount} {currency.data["name"]} have been added to {member.mention}'s bank''')

    @commands.is_owner()
    @commands.command(pass_context=True)
    async def remove(self, ctx, amount: int = 0, member: discord.Member = None):
        ''': Remove points/currency from a member's bank'''
        ID = str(member.id)
        self.check_id(ID)
        currency.data[ID] -= amount
        currency.save()
        await ctx.send(f'''{amount} {currency.data["name"]} has been removed from {member.mention}'s bank''')

    # returns bank details
    @commands.command(pass_context=True, aliases=["vault", "stash", "purse", "wallet"])
    async def bank(self, ctx):
        member = ctx.message.author
        self.check_id(str(member.id))
        embedvar = discord.Embed(title="💰 Bank",
                                 description=f'the bank contains {currency.data[str(member.id)]} {currency.data["name"]}',
                                 colour=0x039e00)
        await ctx.send(embed=embedvar)

    # returns server leaderboard
    @commands.command(aliases=['leaderboards'])
    async def leaderboard(self, ctx):
        members = [(ID, score) for ID, score in currency.data.items() if ID != 'name']
        if len(members) == 0:
            await ctx.send('I have nothing to show. ?daily to get your first income!')
            return
        ordered = sorted(members, key=lambda x: x[1], reverse=True)
        players = ''
        scores = ''
        for ID, score in ordered[:10]:
            if ctx.guild.get_member(int(ID)):
                player = ctx.guild.get_member(int(ID))
                print(player)
                players += player.mention + '\n'
                scores += str(score) + '\n'
        embed = discord.Embed(title='Leaderboard')
        embed.add_field(name='Player', value=players)
        embed.add_field(name='Cash', value=scores)
        await ctx.send(embed=embed)


class Earning(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    class Checks():
        async def check_bank(self, ctx, stakes):
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
        Economy().check_id(ID)
        amount = random.randint(50, 80)
        currency.data[str(ID)] += amount
        currency.save()
        await ctx.send(f'''{amount} {currency.data["name"]} have been added to {ctx.message.author.mention}'s bank''')

    @daily.error
    async def daily_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            embedvar = discord.Embed(title=f"{bot.get_emoji(Emoji.ERROR.value)} On cooldown!",
                                     description="Cooldown will remain for "
                                                 + str(datetime.timedelta(seconds=int(error.retry_after))),
                                     color=0xc20000)
            await ctx.send(embed=embedvar)
        else:
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    @commands.command(aliases=['slot'])
    async def slots(self, ctx, stakes: int):
        if not await self.Checks().check_bank(ctx, stakes): return
        picks = []
        ID = str(ctx.message.author.id)
        Economy().check_id(ID)
        currency.data[str(ID)] -= int(stakes)
        msg = await ctx.send(Emoji.BLANK.value * 3)
        for i in range(0, 3):
            picks.append(random.choice(Emoji.DOTS.value))
            await asyncio.sleep(1.3)
            print(picks)
            await msg.edit(content=str("".join(picks[0:i + 1])) + str(Emoji.BLANK.value * (2 - i)))
        repetition = 0
        for element in picks:
            if picks.count(element) == 2:
                repetition = 1.5
                break
            elif picks.count(element) == 3:
                repetition = 2
                break
        currency.data[str(ID)] += int(stakes * repetition)
        currency.save()
        if repetition == 0:
            await ctx.send(
                f'You have lost {int(stakes)} {currency.data["name"]}. Better luck next time!')
            return
        await ctx.send(
            f'You have won {int(stakes * repetition - stakes)} {currency.data["name"]}!')

    @commands.command(aliases=['coin', 'cointoss'])
    async def toss(self, ctx, choice: str, stakes: int):
        if not await self.Checks().check_bank(ctx, stakes) or (choice.lower() != "heads" and choice.lower() != "tails"):
            print("nope, not doing this")
            return
        ID = str(ctx.message.author.id)
        Economy().check_id(ID)
        currency.data[str(ID)] -= int(stakes)
        face = random.choice(['HEADS', 'TAILS'])
        msg = await ctx.send(Emoji.BLANK.value)
        await asyncio.sleep(1.3)
        await msg.edit(content=bot.get_emoji(id=Emoji[face].value))
        if choice.upper() == face:
            await ctx.send(
                f'You have won {int(stakes)} {currency.data["name"]}!')
            currency.data[str(ID)] += int(stakes * 2)
            return
        await ctx.send(
            f'You have lost {int(stakes)} {currency.data["name"]}. Better luck next time!')

    @commands.command(aliases=['rolldice', 'dice'])
    async def roll(self, ctx, stakes: int):
        if not await self.Checks().check_bank(ctx, stakes): return
        ID = str(ctx.message.author.id)
        Economy().check_id(ID)
        currency.data[str(ID)] -= int(stakes)
        rolls = [random.randint(1, 20), random.randint(0, 20)]
        if rolls[0] <= rolls[1]:
            embedvar = discord.Embed(title="Dice Roll", description=f'You lost **{int(stakes)}** {currency.data["name"]}',
                                     color=0xc20000)
            embedvar.add_field(name=f'**{ctx.message.author.name}**', value=f'Rolled {rolls[0]}', inline=True)
            embedvar.add_field(name=f'**{bot.user.name}**', value=f'Rolled {rolls[1]}', inline=True)
            await ctx.send(embed=embedvar)
            return
        currency.data[str(ID)] += int(stakes + (rolls[0] - rolls[1]) / 20 * stakes)
        embedvar = discord.Embed(title="Dice Roll",
                                 description=f'Won **{int((rolls[0] - rolls[1]) / 20 * stakes * 2)}** {currency.data["name"]}'
                                 f'\n\n Percentage of bet won: {int((rolls[0] - rolls[1]) / 20 * stakes * 2 / stakes*100)}%',
                                 color=0x00c943)
        embedvar.add_field(name=f'**{ctx.message.author.name}**', value=f'Rolled {rolls[0]}', inline=True)
        embedvar.add_field(name=f'**{bot.user.name}**', value=f'Rolled {rolls[1]}', inline=True)
        await ctx.send(embed=embedvar)


bot = commands.Bot(command_prefix="?")

def setup(bot):
    bot.add_cog(Economy())
    bot.add_cog(Earning(bot))


@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))


bot.run('Token')
