from discord import app_commands
from discord.ext import commands
from bs4 import BeautifulSoup
import dns.resolver
import aiohttp
import discord
import time
import json
import sys
import os

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

    await interaction.response.send_message(embed=embed, ephemeral=ephemeral)

@tree.command(name="profile", description="Show a user's profile and information.")
@app_commands.describe(user="User to show profile.")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def profile(interaction: discord.Interaction, user: discord.User):
    embed = discord.Embed()
    embed.color = CONFIG["THEME_COLOR"]
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
        embed.color = CONFIG["THEME_COLOR"]
        embed.title = f"{user.display_name}'s Banner"
        embed.set_image(url=user_fetch.banner)

        await interaction.response.send_message(embed=embed)

    else:
        await _command_respond(
            interaction,
            color=0xff0000,
            title="Command Error",
            description="This user does not have a banner.",
            ephemeral=True
        )

@tree.command(name="restart", description="Fully restart the bot.")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def restart(interaction: discord.Interaction):
    if not interaction.user.id in CONFIG["ADMINS"]:
        return await _command_respond(
            interaction,
            color=0xff0000,
            title="Permission Error",
            description="You do not have permission to use this command.",
            ephemeral=True
        )

    await _command_respond(
        interaction,
        color=CONFIG["THEME_COLOR"],
        title="Poly ToolKit",
        description="Restarting the bot in 1 second...",
        ephemeral=False
    )

    time.sleep(1)

    os.execv(sys.executable, ["python3"] + sys.argv)

@tree.command(name="phone_lookup", description="Lookup a phone number.")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.describe(phone_number="Target's internation phone number.")
async def phone_lookup(interaction: discord.Interaction, phone_number: str):
    phone_number = phone_number.strip().replace("-", "").replace(" ", "").replace("+", "")

    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://free-lookup.net/{phone_number}") as response:
            response_text = await response.text()
            html = BeautifulSoup(response_text, "html.parser")

            try:
                infos = html.findChild("ul", {"class": "report-summary__list"}).findAll("div")
            except Exception:
                return await _command_respond(
                    interaction,
                    color=0xff0000,
                    title="Phone Lookup Error",
                    description="Invalid phone number.",
                    ephemeral=False
                )
            
            infos_dict = {k.text.strip(): infos[i+1].text.strip() if infos[i+1].text.strip() else "No information" for i, k in enumerate(infos) if not i % 2}

            embed = discord.Embed()
            embed.color = CONFIG["THEME_COLOR"]
            embed.title = "Phone Lookup"
            embed.description = "Phone number information will be shown below."

            for info in infos_dict:
                embed.add_field(name=f"{info}", value=f"`{infos_dict[info]}`", inline=True)
    
    await interaction.response.send_message(embed=embed)

@tree.command(name="dns_resolve", description="Resolve DNS to IP.")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.describe(domain="Target's domain name.")
async def dns_resolve(interaction: discord.Interaction, domain: str):
    try:
        dns_query = dns.resolver.resolve(qname=domain)
        answer = dns_query.response.answer
    except Exception:
        return await _command_respond(
            interaction,
            color=0xff0000,
            title="DNS Resolve Error",
            description="Unable to resolve the domain name you provided. Please make sure it is correct and try again.",
            ephemeral=True
        )

    embed = discord.Embed()
    embed.color = CONFIG["THEME_COLOR"]
    embed.title = "DNS Resolve"
    embed.description = f"DNS answer for {domain}:\n```{'\n'.join([data.to_text() for data in answer])}```"

    await interaction.response.send_message(embed=embed)

if __name__ == "__main__":
    client.run(token=CONFIG["TOKEN"])
