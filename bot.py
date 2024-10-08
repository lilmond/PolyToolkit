from discord import app_commands
from discord.ext import commands
import discord
import json

CONFIG = json.load(open("./config.json", "r"))

client = commands.Bot(command_prefix="!", intents=discord.Intents.all())
tree = client.tree

@client.event
async def on_ready():
    await client.tree.sync()
    print(f"Logged In: {client.user.name}")

async def _command_respond(interaction: discord.Interaction, color: int, title: str, description: str, ephemeral: bool = True):
    embed = discord.Embed()
    embed.color = color
    embed.title = title
    embed.description = description

    return await interaction.response.send_message(embed=embed, ephemeral=ephemeral)

@tree.command(name="profile", description="Show a user's profile and information.")
@app_commands.describe(user="User to show profile.")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def profile(interaction: discord.Interaction, user: discord.User):
    embed = discord.Embed()
    embed.color = 0x7800c8
    embed.title = f"{user.display_name}'s Profile"
    embed.add_field(name="User ID:", value=f"`{user.id}`", inline=True)
    embed.add_field(name="Username:", value=f"`{user.name}`", inline=True)
    embed.add_field(name="Created At:", value=f"`{user.created_at.strftime('%m-%d-%Y %H:%M:%S')}`", inline=False)
    embed.set_image(url=user.display_avatar.url)

    await interaction.response.send_message(embed=embed)

@tree.command(name="banner", description="Show a user's banner.")
@app_commands.describe(user="User to show banner.")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def banner(interaction: discord.Interaction, user: discord.User):
    user_fetch = await client.fetch_user(user.id)

    if user_fetch.banner:
        embed = discord.Embed()
        embed.color = 0x7800c8
        embed.title = f"{user.display_name}'s Banner"
        embed.set_image(url=user_fetch.banner)

        await interaction.response.send_message(embed=embed)
    
    else:
        await _command_respond(
            interaction,
            color=0xff0000,
            title="Command Error",
            description="This user does not have a banner.",
            ephemeral=False
        )

if __name__ == "__main__":
    client.run(token=CONFIG["TOKEN"])
