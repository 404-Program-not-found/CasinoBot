import discord
from discord.ext import commands
import random
import asyncio
import sys
import traceback
import datetime
from pyson import pyson_class as pyson


class Economy(commands.Cog):
    # Migrated to 1.0 and changed from https://github.com/stroupbslayen/Other-Discord-Bots-async/tree/master/Currency

    def __init__(self, bot):
        self.currency = pyson('currency')

    def check_id(self, ID):
        if str(ID) not in self.currency.data:
            self.currency.data[str(ID)] = 0
            self.currency.save()

    # returns bank details
    @commands.command(aliases=["vault", "stash", "purse", "wallet"])
    async def bank(self, ctx):
        self.currency = pyson('currency')
        member = ctx.message.author
        self.check_id(str(member.id))
        embedvar = discord.Embed(title="💰 Bank",
                                 description=f'the bank contains {self.currency.data[str(member.id)]} {self.currency.data["name"]}',
                                 colour=0x039e00)
        await ctx.send(embed=embedvar)

    # returns server leaderboard
    @commands.command(aliases=['leaderboards'])
    async def leaderboard(self, ctx):
        members = [(ID, score) for ID, score in self.currency.data.items() if ID != 'name']
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

def setup(bot):
    bot.add_cog(Economy(bot))