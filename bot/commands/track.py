import discord
from discord import app_commands
from discord.ext import commands

from bot.bot import RadioMonashBot
from bot.utils.logger import get_logger

logger = get_logger("TrackCommand")

class Track(commands.Cog):
    def __init__(self, bot: RadioMonashBot):
        self.bot = bot

    @app_commands.command(name="track", description="Show detailed information about the current track")
    async def track_info(self, interaction: discord.Interaction):
        track = self.bot.current_track_info or await self.bot.fetch_current_track()
        if track:
            embed = self.bot.create_track_embed(track)
            await interaction.response.send_message(embed=embed)
            logger.info(f"Sent track info in {interaction.guild.name}")
        else:
            await interaction.response.send_message("Unable to fetch current track information. Please try again later.", ephemeral=True)

async def setup(bot: RadioMonashBot):
    await bot.add_cog(Track(bot))
