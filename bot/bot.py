import discord
from discord import app_commands
from discord.ext import commands, tasks
import aiohttp
import asyncio

from bot.utils.logger import get_logger

logger = get_logger("RadioMonashBot")

class RadioMonashBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.voice_states = True
        super().__init__(command_prefix="!", intents=intents)

        self.radio_stream_url = "https://play.radioking.io/radio-monash"
        self.api_base_url = "https://api.radioking.io/widget/radio/radio-monash"
        self.my_voice_clients = {}
        self.current_track_info = None

    async def setup_hook(self):
        # Load commands from the commands folder.
        await self.load_extension("bot.commands.play")
        await self.load_extension("bot.commands.stop")
        await self.load_extension("bot.commands.track")
        await self.load_extension("bot.commands.volume")
        await self.load_extension("bot.commands.help_cmd")
        self.track_update_task.start()

    async def on_ready(self):
        logger.info(f"Logged in as {self.user} (ID: {self.user.id})")
        logger.info(f"Connected to {len(self.guilds)} guild(s)")
        await self.change_presence(activity=discord.Activity(
            type=discord.ActivityType.streaming,
            name="Radio Monash"
        ))
        try:
            synced = await self.tree.sync()
            logger.info(f"Synced {len(synced)} command(s)")
        except Exception as e:
            logger.error(f"Failed to sync commands: {e}")

    @tasks.loop(minutes=1)
    async def track_update_task(self):
        """Periodically update the current track information and notify active channels."""
        try:
            new_track = await self.fetch_current_track()
            if (self.current_track_info and new_track and 
                self.current_track_info.get('title') != new_track.get('title') and
                self.my_voice_clients):
                for guild_id, voice_client in self.my_voice_clients.items():
                    guild = self.get_guild(guild_id)
                    if guild and voice_client.is_connected():
                        for channel in guild.text_channels:
                            if channel.permissions_for(guild.me).send_messages:
                                embed = self.create_track_embed(new_track)
                                await channel.send("🎵 Now playing:", embed=embed)
                                break
            self.current_track_info = new_track
        except Exception as e:
            logger.error(f"Error in track update task: {e}")

    @track_update_task.before_loop
    async def before_track_update(self):
        await self.wait_until_ready()

    async def fetch_current_track(self):
        """Fetch current track information from Radio Monash API."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.api_base_url}/track/current") as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"API returned status {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Error fetching track data: {e}")
            return None

    def create_track_embed(self, track_data):
        """Create a rich embed for track information."""
        if not track_data:
            return None

        embed = discord.Embed(
            title=track_data.get('title', 'Unknown Title'),
            color=0x9370DB
        )
        embed.set_author(name="Radio Monash")
        embed.add_field(name="Artist", value=track_data.get('artist', 'Unknown Artist'), inline=True)
        if track_data.get('album'):
            embed.add_field(name="Album", value=track_data.get('album'), inline=True)
        duration = track_data.get('duration', 0)
        if duration:
            minutes = int(duration) // 60
            seconds = int(duration) % 60
            embed.add_field(name="Duration", value=f"{minutes}:{seconds:02d}", inline=True)
        if track_data.get('cover'):
            embed.set_thumbnail(url=track_data.get('cover'))
        if track_data.get('buy_link'):
            embed.add_field(name="Stream/Buy", value=f"[Listen Online]({track_data.get('buy_link')})", inline=False)
        embed.set_footer(text="Tune in radiomonash.online")
        return embed

    async def on_voice_state_update(self, member, before, after):
        """Handle voice state updates to detect when bot is disconnected."""
        if member.id == self.user.id and before.channel and not after.channel:
            guild_id = before.channel.guild.id
            if guild_id in self.my_voice_clients:
                del self.my_voice_clients[guild_id]
                logger.info(f"Bot was disconnected from voice in guild {guild_id}")
