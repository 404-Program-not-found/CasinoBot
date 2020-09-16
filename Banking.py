import discord
from discord.ext import commands
import asyncio
from pyson import pyson_class as pyson
from Economy import Economy
from Earning import Earning
from CasinoBot import Emoji


class Banking(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.Emoji = Emoji
        self.currency = pyson('currency')
        self.Economy = Economy(self.bot)
        self.Checks = Earning(self.bot).Checks()

    @commands.command()
    async def transfer(self, ctx, amount: int, target: discord.Member):
        ID = str(ctx.message.author.id)
        self.Economy.check_id(ID)
        self.Economy.check_id(target.id)
        if not await self.Checks.check_bank(ctx, amount, self.currency, self.bot, self.Emoji): return
        self.currency.data[str(ID)] -= int(amount)
        self.currency.data[str(target.id)] += int(amount)
        embedvar = discord.Embed(title= "🔁 Transfer Success!",
                                 description=f"You have transferred {amount} {self.currency.data['name']} to {target.display_name}",
                                 colour=0x039e00)
        await ctx.send(embed=embedvar)
        self.currency.save()

def setup(bot):
    bot.add_cog(Banking(bot))
