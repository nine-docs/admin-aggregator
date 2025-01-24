import discord
from crawler.kubernetes import get_kubernetes_release
from crawler.docker import get_kubernetes_release
from pathlib import Path
import environ
import os

BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env(
    DEBUG=(bool, False)
)
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

TOKEN = env('TOKEN')
CHANNEL_ID = env('CHANNEL_ID')

class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged in as {self.user}')
        channel = self.get_channel(int(CHANNEL_ID))
        latest_release, released_date = get_kubernetes_release()

        if latest_release and released_date:
            embed = discord.Embed(
                title="Kubernetes Latest Release",
                description="Here are the details of the latest Kubernetes release:",
                color=0x00ff00
            )
            embed.add_field(name="Latest Release", value=latest_release, inline=False)
            embed.add_field(name="Released Date", value=released_date, inline=False)
            embed.set_footer(text="Data fetched from Kubernetes Official Website")
        else:
            embed = discord.Embed(
                title="Kubernetes Release Info",
                description="Failed to fetch the latest release information.",
                color=0xff0000
            )
        await channel.send(embed=embed)


intents = discord.Intents.default()
intents.message_content = True
client = MyClient(intents=intents)
client.run(TOKEN)
