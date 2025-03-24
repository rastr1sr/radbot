import discord
from discord import app_commands
from discord.ext import commands

from bot.bot import RadioMonashBot
from bot.utils.logger import get_logger

logger = get_logger("HelpCommand")

class HelpCmd(commands.Cog):
    def __init__(self, bot: RadioMonashBot):
        self.bot = bot

    @app_commands.command(name="help", description="Show available commands and information about the bot")
    async def help_command(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="📻 Radio Monash Bot Help",
            description="Listen to Radio Monash directly in your Discord server!",
            color=0x9370DB
        )
        embed.add_field(name="/play", value="Play Radio Monash in your voice channel", inline=False)
        embed.add_field(name="/stop", value="Stop the radio stream and disconnect the bot", inline=False)
        embed.add_field(name="/track", value="Show detailed information about the current track", inline=False)
        embed.add_field(name="/volume <level>", value="Adjust the volume (0-100)", inline=False)
        embed.set_footer(text="Radio Monash - Tune in anytime!")
        await interaction.response.send_message(embed=embed)
        logger.info(f"Help command used in {interaction.guild.name}")

async def setup(bot: RadioMonashBot):
    await bot.add_cog(HelpCmd(bot))
