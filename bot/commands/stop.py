import discord
from discord import app_commands
from discord.ext import commands

from bot.bot import RadioMonashBot
from bot.utils.logger import get_logger

logger = get_logger("StopCommand")

class Stop(commands.Cog):
    def __init__(self, bot: RadioMonashBot):
        self.bot = bot

    @app_commands.command(name="stop", description="Stop the radio stream and disconnect the bot")
    async def stop_radio(self, interaction: discord.Interaction):
        """Stop playing the radio and disconnect from the voice channel."""
        try:
            await interaction.response.defer()
            guild_id = interaction.guild_id
            if guild_id in self.bot.my_voice_clients and self.bot.my_voice_clients[guild_id].is_connected():
                voice_client = self.bot.my_voice_clients[guild_id]

                if voice_client.is_playing():
                    voice_client.stop()

                await voice_client.disconnect()
                if guild_id in self.bot.my_voice_clients:
                    del self.bot.my_voice_clients[guild_id]
                await interaction.followup.send("⏹️ Radio stream stopped and disconnected.")
            else:
                await interaction.followup.send(
                    "I'm not currently in a voice channel.", 
                    ephemeral=True
                )
        except Exception as e:
            await interaction.followup.send(f"An error occurred: {e}", ephemeral=True)
            print(f"Error in /stop command: {e}")


async def setup(bot: RadioMonashBot):
    await bot.add_cog(Stop(bot))
