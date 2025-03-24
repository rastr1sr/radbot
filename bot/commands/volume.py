import discord
from discord import app_commands
from discord.ext import commands

from bot.bot import RadioMonashBot
from bot.utils.logger import get_logger

logger = get_logger("VolumeCommand")

class Volume(commands.Cog):
    def __init__(self, bot: RadioMonashBot):
        self.bot = bot

    @app_commands.command(name="volume", description="Adjust the volume of the radio stream (0-100)")
    @app_commands.describe(level="Volume level between 0 and 100")
    async def set_volume(self, interaction: discord.Interaction, level: int):
        if not 0 <= level <= 100:
            await interaction.response.send_message("Volume must be between 0 and 100.", ephemeral=True)
            return
        guild_id = interaction.guild_id
        if guild_id not in self.bot.my_voice_clients or not self.bot.my_voice_clients[guild_id].is_connected():
            await interaction.response.send_message("I'm not currently playing in a voice channel.", ephemeral=True)
            return
        volume = level / 100
        voice_client = self.bot.my_voice_clients[guild_id]
        if hasattr(voice_client.source, 'volume'):
            voice_client.source.volume = volume
            await interaction.response.send_message(f"🔊 Volume set to {level}%")
            logger.info(f"Volume set to {level}% in {interaction.guild.name}")
        else:
            await interaction.response.send_message("Unable to adjust volume for the current stream.", ephemeral=True)

async def setup(bot: RadioMonashBot):
    await bot.add_cog(Volume(bot))
