import discord
from discord.ext import commands
import json
import os

bot = commands.Bot(command_prefix="/", intents=discord.Intents.default())

if not os.path.exists("user_data"):
    os.makedirs("user_data")

#

@bot.tree.command(name="rep_plus", description="Add a positive reputation comment to the user.")
@discord.app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def rep_plus(interaction: discord.Interaction, user: discord.User, comment: str):
    file_path = f"user_data/{user.id}.json"
    
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            user_data = json.load(f)
    else:
        user_data = {"rep_plus": [], "rep_minus": []}
    
    user_data["rep_plus"].append(comment)
    
    with open(file_path, "w") as f:
        json.dump(user_data, f, indent=4)
    
    embed = discord.Embed(title="Reputation Added", description=f"**{user.name}** has received positive reputation!", color=discord.Color.green())
    embed.add_field(name="Comment", value=comment)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="rep_min", description="Add a negative reputation comment to the user.")
@discord.app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def rep_min(interaction: discord.Interaction, user: discord.User, comment: str):
    file_path = f"user_data/{user.id}.json"
    
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            user_data = json.load(f)
    else:
        user_data = {"rep_plus": [], "rep_minus": []}
    
    user_data["rep_minus"].append(comment)
    
    with open(file_path, "w") as f:
        json.dump(user_data, f, indent=4)
    
    embed = discord.Embed(title="Reputation Added", description=f"**{user.name}** has received negative reputation!", color=discord.Color.red())
    embed.add_field(name="Comment", value=comment)
    await interaction.response.send_message(embed=embed)

    # Send the response with an embed
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="rep", description="See all reputation comments for a user.")
@discord.app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def rep(interaction: discord.Interaction, user: discord.User):
    file_path = f"user_data/{user.id}.json"
    
    # Check if the user has a data file
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            user_data = json.load(f)
        
        # Create the response content for positive and negative reputation comments
        rep_plus_comments = "\n".join(user_data["rep_plus"]) if user_data["rep_plus"] else "No positive reputation comments."
        rep_minus_comments = "\n".join(user_data["rep_minus"]) if user_data["rep_minus"] else "No negative reputation comments."
        
        # Create the embed response
        embed = discord.Embed(title=f"Reputation for {user.name}", color=discord.Color.blue())
        embed.add_field(name="Rep+ Comments", value=rep_plus_comments, inline=False)
        embed.add_field(name="Rep- Comments", value=rep_minus_comments, inline=False)
        
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message(f"No reputation data found for {user.name}.")

@bot.event
async def on_ready():
    await bot.tree.sync()
    await bot.tree.sync(guild=discord.Object(id=1336230460526821376))
    for command in bot.tree.get_commands():
        print(f"Command: {command.name}")

bot.run(os.getenv("DISCORD_BOT_TOKEN"))
