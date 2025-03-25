import discord
from discord import app_commands
from discord.ext import commands
import asyncio

from bot.bot import RadioMonashBot
from bot.utils.logger import get_logger

logger = get_logger("PlayCommand")

class Play(commands.Cog):
    def __init__(self, bot: RadioMonashBot):
        self.bot = bot
        self.play_channels = {}

    @app_commands.command(name="play", description="Play Radio Monash in your voice channel")
    async def play_radio(self, interaction: discord.Interaction):
        if not interaction.user.voice:
            await interaction.response.send_message("You need to join a voice channel first!", ephemeral=True)
            return
        voice_channel = interaction.user.voice.channel
        guild_id = interaction.guild_id
        if guild_id in self.bot.my_voice_clients and self.bot.my_voice_clients[guild_id].is_connected():
            await interaction.response.send_message("I'm already playing in a voice channel!", ephemeral=True)
            return

        await interaction.response.defer()
        try:
            voice_client = await voice_channel.connect()
            self.bot.my_voice_clients[guild_id] = voice_client
            audio_source = discord.FFmpegPCMAudio(
                self.bot.radio_stream_url,
                before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
            )
            voice_client.play(
                discord.PCMVolumeTransformer(audio_source, volume=0.5),
                after=lambda e: logger.error(f"Player error: {e}") if e else None
            )
            track = self.bot.current_track_info or await self.bot.fetch_current_track()
            embed = discord.Embed(
                title="📻 Radio Monash Now Playing",
                description=f"Connected to **{voice_channel.name}**",
                color=0x9370DB
            )
            if track:
                embed.add_field(
                    name="Current Track",
                    value=f"**{track.get('artist', 'Unknown Artist')}** - **{track.get('title', 'Unknown Title')}**",
                    inline=False
                )
                if track.get('cover'):
                    embed.set_thumbnail(url=track.get('cover'))
            embed.set_footer(text="Use /stop to disconnect | /track for detailed track info")
            await interaction.followup.send(embed=embed)
            logger.info(f"Started playing Radio Monash in {interaction.guild.name} - {voice_channel.name}")

            self.play_channels[guild_id] = interaction.channel_id
        except Exception as e:
            logger.error(f"Error in play command: {e}")
            await interaction.followup.send(f"Error: Unable to play radio stream. {str(e)}", ephemeral=True)

async def setup(bot: RadioMonashBot):
    await bot.add_cog(Play(bot))
