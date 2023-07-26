import asyncio
import random
from datetime import datetime

import discord
from discord import slash_command
from discord.ext import commands


class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_giveaways = {}

    @slash_command(name="start_giveaway", description="Starts a giveaway")
    @commands.has_permissions(administrator=True)
    async def start_giveaway(self, ctx, duration: int, prize: str, channel: discord.TextChannel):
        await ctx.defer()
        embed = discord.Embed(title="🎊 | Giveaway", description="Reagiere mit 🎉 um teilzunehmen!",
                              color=discord.Color.orange(), timestamp=datetime.now())
        embed.add_field(name="💰 | Preis", value=prize, inline=False)
        embed.add_field(name="⏰ | Dauer", value=f"{duration} Sekunden", inline=False)
        file_set = discord.File(f"img/Giveaway.png", filename="Giveaway.png")
        embed.set_thumbnail(url="attachment://Giveaway.png")
        embed.set_footer(text=f"{ctx.guild.name}", icon_url=self.bot.user.avatar.url)

        message = await channel.send(embed=embed, file=file_set)
        await ctx.respond(embed = discord.Embed(
            title="Giveaway",
            description=f"Das Giveaway wurde Erfolgreich erstell und in {channel.mention} geschickt",
            color=discord.Color.orange(),
            timestamp=datetime.now()
        ))

        await message.add_reaction("🎉")

        await self.timer(message, duration, prize, channel)

        self.active_giveaways[message.id] = (ctx.author.id, prize, channel.id)

    @slash_command(name="end_giveaway")
    @commands.has_permissions(administrator=True)
    async def end_giveaway(self, ctx, message_id: int):
        if message_id in self.active_giveaways:
            author_id, prize, channel_id = self.active_giveaways.pop(message_id)
            channel = self.bot.get_channel(channel_id)

            if not channel:
                await ctx.send(embed = discord.Embed(
                    title="📛 | Channel Error",
                    description="Der Channel für das Giveaway wurde nicht gefunden",
                    color=discord.Color.orange(),
                    timestamp=datetime.now()
                ))
                return

            try:
                message = await channel.fetch_message(message_id)
            except discord.NotFound:
                await ctx.send("Es wurde kein aktives Giveaway mit dieser ID gefunden.")
                return

            reaction = discord.utils.get(message.reactions, emoji="🎉")

            if reaction and reaction.count > 1:
                winner = await self.pick_winner(message)
                if winner:
                    await channel.send(f"{winner.mention}", embed = discord.Embed(
                        title="🎊 | Gewonnen",
                        description=f"Der User {winner.mention} hat das Giveaway mit dem Preis {prize} gewonnen"
                                    "\n Bitte melde dich im <#1075879136649805986> um deine Belohnung zubekommen",
                        color=discord.Color.orange(),
                        timestamp=datetime.now()
                    ))
            else:
                await channel.send(embed = discord.Embed(
                    title="🎊 | Kein Gewinner",
                    description="Niemand hat das Giveaway gewonnen",
                    color=discord.Color.orange(),
                    timestamp=datetime.now()
            ))
        else:
            await ctx.send(embed = discord.Embed(
                title="🎊 | Keine ID",
                description="Es wurde kein Gewinnspiel mit der ID gefunden",
                color= discord.Color.orange(),
                timestamp= datetime.now()
            ))

    async def timer(self, message, duration, prize, channel):
        await asyncio.sleep(duration)
        try:
            message = await channel.fetch_message(message.id)
        except discord.NotFound:
            return

        reaction = discord.utils.get(message.reactions, emoji="🎉")

        if reaction and reaction.count > 1:
            winner = await self.pick_winner(message)
            if winner:
                await channel.send(f"{winner.mention}", embed = discord.Embed(
                        title="🎊 | Gewonnen",
                        description=f"Der User {winner.mention} hat das Giveaway mit dem Preis `{prize}` gewonnen"
                                    "\n Bitte melde dich im <#1075879136649805986> um deine Belohnung zubekommen",
                        color=discord.Color.orange(),
                        timestamp=datetime.now()
                    ))
        else:
            await channel.send(embed = discord.Embed(
                title="🎊 | Kein Gewinner",
                description="Niemand hat das Giveaway gewonnen",
                color=discord.Color.orange(),
                timestamp=datetime.now()
            ))

    async def pick_winner(self, message):
        reaction = discord.utils.get(message.reactions, emoji="🎉")
        users = await reaction.users().flatten()
        users.remove(self.bot.user)

        if users:
            winner = random.choice(users)
            return winner

        return None

def setup(bot):
    bot.add_cog(Giveaway(bot))
