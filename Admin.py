import discord
from discord.ext import commands
from pyson import pyson_class as pyson

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.currency = pyson('currency')

    def check_id(self, ID):
        if str(ID) not in self.currency.data:
            self.currency.data[str(ID)] = 0
            self.currency.save()

    @commands.is_owner()
    @commands.command()
    async def currency_type(self, ctx, ntype: str = 'dollars'):
        ''': Change name of your self.currency'''
        ptype = self.currency.data['name']
        self.currency.data['name'] = ntype
        self.currency.save()
        await ctx.send(f'The economy type has been changed from **{ptype}** to **{ntype}**')

    @commands.is_owner()
    @commands.command(pass_context=True)
    async def add(self, ctx, amount: int = 0, member: discord.Member = None):
        ''': Add points/self.currency to a member's bank'''
        ID = str(member.id)
        self.check_id(ID)
        self.currency.data[str(ID)] += amount
        self.currency.save()
        await ctx.send(f'''{amount} {self.currency.data["name"]} have been added to {member.mention}'s bank''')

    @commands.is_owner()
    @commands.command(pass_context=True)
    async def remove(self, ctx, amount: int = 0, member: discord.Member = None):
        ''': Remove points/self.currency from a member's bank'''
        ID = str(member.id)
        self.check_id(ID)
        self.currency.data[ID] -= amount
        self.currency.save()
        await ctx.send(f'''{amount} {self.currency.data["name"]} has been removed from {member.mention}'s bank''')

def setup(bot):
    bot.add_cog(Admin(bot))