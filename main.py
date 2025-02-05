import discord
from discord.ext import commands
from dotenv import load_dotenv
import json
import os
from discord import ui
from discord.ui import View, Button
from discord import Embed, Interaction
from discord import ButtonStyle

bot = commands.Bot(command_prefix="/", intents=discord.Intents.default())

if not os.path.exists("user_data"):
    os.makedirs("user_data")

#load_dotenv()
# for local :(

#

class MyView(ui.View):
    @ui.button(label="Previous", style=ButtonStyle.primary)
    async def previous_button(self, interaction: discord.Interaction, button: ui.Button):
        # Your code for the previous button
        pass

    @ui.button(label="Next", style=ButtonStyle.primary)
    async def next_button(self, interaction: discord.Interaction, button: ui.Button):
        # Your code for the next button
        pass

class Paginator(View):
    def __init__(self, embeds):
        super().__init__(timeout=60)
        self.embeds = embeds
        self.current_page = 0

        # Add buttons to the view
        self.previous_button = Button(label="Previous", style=ButtonStyle.primary)
        self.next_button = Button(label="Next", style=ButtonStyle.primary)
        self.previous_button.callback = self.previous_page
        self.next_button.callback = self.next_page
        self.add_item(self.previous_button)
        self.add_item(self.next_button)

        # Initial button state
        self.update_button_state()

    async def previous_page(self, interaction: Interaction):
        if self.current_page > 0:
            self.current_page -= 1
            await self.update_message(interaction)
        else:
            await interaction.response.send_message("You're already on the first page.", ephemeral=True)

    async def next_page(self, interaction: Interaction):
        if self.current_page < len(self.embeds) - 1:
            self.current_page += 1
            await self.update_message(interaction)
        else:
            await interaction.response.send_message("You're already on the last page.", ephemeral=True)

    async def update_message(self, interaction: Interaction):
        embed = self.embeds[self.current_page]
        self.update_button_state()
        await interaction.response.edit_message(embed=embed, view=self)

    def update_button_state(self):
        self.previous_button.disabled = self.current_page == 0
        self.next_button.disabled = self.current_page == len(self.embeds) - 1

#

@bot.tree.command(name="rep_plus", description="Add a positive reputation comment to the user.")
@discord.app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def rep_plus(interaction: discord.Interaction, user: discord.User, comment: str):
    file_path = f"user_data/{user.id}.json"
    
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            user_data = json.load(f)
    else:
        user_data = {"comments": [], "reputation": 0}
    
    user_data["comments"].append({"comment": comment, "type": "positive"})
    user_data["reputation"] += 1
    
    with open(file_path, "w") as f:
        json.dump(user_data, f, indent=4)
    
    embed = discord.Embed(title="Reputation Added", description=f"**{user.name}** has received positive reputation!", color=discord.Color.green())
    embed.add_field(name="Comment", value=comment)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="rep_minus", description="Add a negative reputation comment to the user.")
@discord.app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def rep_min(interaction: discord.Interaction, user: discord.User, comment: str):
    file_path = f"user_data/{user.id}.json"
    
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            user_data = json.load(f)
    else:
        user_data = {"comments": [], "reputation": 0}
    
    user_data["comments"].append({"comment": comment, "type": "negative"})
    user_data["reputation"] -= 1
    
    with open(file_path, "w") as f:
        json.dump(user_data, f, indent=4)
    
    embed = discord.Embed(title="Reputation Added", description=f"**{user.name}** has received negative reputation!", color=discord.Color.red())
    embed.add_field(name="Comment", value=comment)
    await interaction.response.send_message(embed=embed)

    # Send the response with an embed
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="rep_show", description="See all reputation comments for a user.")
@discord.app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def rep(interaction: discord.Interaction, user: discord.User):
    file_path = f"user_data/{user.id}.json"
    
    # Check if the user has a data file
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            user_data = json.load(f)
        
        # Count reputation
        reputation = user_data["reputation"]
        if reputation > 0:
            embed_color = discord.Color.green()
        elif reputation < 0:
            embed_color = discord.Color.red()
        else:
            embed_color = discord.Color.greyple()
        # Order and categorize comments
        comments = []
        for entry in user_data.get("comments", []):
            comment = entry.get("comment")
            if entry.get("type") == "positive":
                comments.append(f"🟢 {comment}")
            elif entry.get("type") == "negative":
                comments.append(f"🔴 {comment}")
        comments.reverse()
        
        # Create embeds for pagination
        embeds = []
        per_page = 14
        for i in range(0, len(comments), per_page):
            embed = Embed(
                title=f"Reputation for {user.name}",
                description=f"**Reputation: {reputation}**",
                color=embed_color
            )
            embed.add_field(
                name="Comments",
                value="\n".join(comments[i:i + per_page]),
                inline=False
            )
            embed.set_footer(text=f"Page {i // per_page + 1}/{(len(comments) - 1) // per_page + 1}")
            embeds.append(embed)

        if embeds:
            view = Paginator(embeds)
            view.message = await interaction.response.send_message(embed=embeds[0], view=view)
        else:
            await interaction.response.send_message(f"No reputation comments found for {user.name}.")
    else:
        await interaction.response.send_message(f"No reputation data found for {user.name}.")

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Loaded")

bot.run(os.getenv("DISCORD_BOT_TOKEN"))
