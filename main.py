import discord
from discord.ext import commands
import os
from discord import ui
from discord.ui import View, Button
from discord import Embed, Interaction
from discord import ButtonStyle

from discord.app_commands import CommandOnCooldown
from datetime import datetime, timedelta

import asyncio

from dotenv import load_dotenv
load_dotenv()

from user_manager import load_user, save_user, user_exists, all_user_files

rep_cooldowns = {}  # {user_id: timestamp}

bot = commands.Bot(command_prefix="/", intents=discord.Intents.default())


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
        super().__init__(timeout=300)
        self.embeds = embeds
        self.current_page = 0

        # Previous and Next Buttons
        self.previous_button = Button(label="Previous", style=ButtonStyle.primary)
        self.next_button = Button(label="Next", style=ButtonStyle.primary)
        
        # Assign callbacks
        self.previous_button.callback = self.previous_page
        self.next_button.callback = self.next_page
        
        # Add buttons to the view
        self.add_item(self.previous_button)
        self.add_item(self.next_button)
        
        # Update the button state
        self.update_button_state()

    async def previous_page(self, interaction: discord.Interaction):
        if self.current_page > 0:
            self.current_page -= 1
            await self.update_message(interaction)
        else:
            await interaction.response.send_message("You're already on the first page.", ephemeral=True)

    async def next_page(self, interaction: discord.Interaction):
        if self.current_page < len(self.embeds) - 1:
            self.current_page += 1
            await self.update_message(interaction)
        else:
            await interaction.response.send_message("You're already on the last page.", ephemeral=True)

    async def update_message(self, interaction: discord.Interaction):
        embed = self.embeds[self.current_page]
        self.update_button_state()
        await interaction.response.edit_message(embed=embed, view=self)

    def update_button_state(self):
        self.previous_button.disabled = self.current_page == 0
        self.next_button.disabled = self.current_page == len(self.embeds) - 1

    def reset(self):
        self.previous_button.disabled = True
        self.next_button.disabled = False
        self.current_page = 0

def check_rep_cooldown(user_id):
    """Returns True if the user is on cooldown, else False"""
    cooldown_time = timedelta(hours=12)
    last_used = rep_cooldowns.get(user_id, datetime.min)
    return datetime.utcnow() - last_used < cooldown_time

@bot.tree.command(name="rep_plus", description="Add a positive reputation comment to the user.")
@discord.app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def rep_plus(interaction: discord.Interaction, user: discord.User, comment: str):
    if user == interaction.user:
        await interaction.response.send_message("You can't add comments to yourself!", ephemeral=True)
        return
    if check_rep_cooldown(interaction.user.id):
        await interaction.response.send_message("You can only use rep_plus and rep_minus once every 12 hours!", ephemeral=True)
        return

    user_data = load_user(user.id)
    
    user_data["comments"].append({"comment": comment, "type": 1, "author": interaction.user.name})
    user_data["reputation"] += 1

    save_user(user.id, user_data)
    rep_cooldowns[interaction.user.id] = datetime.utcnow()
    
    embed = discord.Embed(title="Reputation Increased", description=f"**{user.name}** has received positive reputation!", color=discord.Color.green())
    embed.add_field(name="Comment", value=comment)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="rep_minus", description="Add a negative reputation comment to the user.")
@discord.app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def rep_min(interaction: discord.Interaction, user: discord.User, comment: str):
    if user == interaction.user:
        await interaction.response.send_message("You can't add comments to yourself!", ephemeral=True)
        return
    if check_rep_cooldown(interaction.user.id):
        await interaction.response.send_message("You can only use rep_plus and rep_minus once every 12 hours!", ephemeral=True)
        return
    
    user_data = load_user(user.id)
    
    user_data["comments"].append({"comment": comment, "type": 0, "author": interaction.user.name})
    user_data["reputation"] -= 1

    save_user(user.id, user_data)
    rep_cooldowns[interaction.user.id] = datetime.utcnow()
    
    embed = discord.Embed(title="Reputation Decreased", description=f"**{user.name}** has received negative reputation!", color=discord.Color.red())
    embed.add_field(name="Comment", value=comment)
    await interaction.response.send_message(embed=embed)

    # Send the response with an embed
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="rep_show", description="See all reputation comments for a user, or yourself (if none specified).")
@discord.app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def rep(interaction: discord.Interaction, user: discord.User = None):
    if user is None:
        user = interaction.user
    
    if not user_exists(user.id):
        await interaction.response.send_message(f"No reputation data found for {user.name}.")
        return
    
    user_data = load_user(user.id)
    reputation = user_data["reputation"]

    if reputation > 0:
        embed_color = discord.Color.green()
    elif reputation < 0:
        embed_color = discord.Color.red()
    else:
        embed_color = discord.Color.greyple()
    # Order and categorize comments
    comments = []
    i = 0
    for entry in user_data.get("comments", []):
        i += 1
        comment = entry.get("comment")
        comid = i
        id_str = f"{comid}".rjust(4)  # pad to 4 char to keep emojis in line
        if entry.get("type") == 1:
            comments.append(f"`{id_str}` \U0001F7E2 {comment}")
        elif entry.get("type") == 0:
            comments.append(f"`{id_str}` \U0001F534 {comment}")
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

async def leaderboard_data():
    """Generates leaderboard embed once every 5 minutes.
       The update status is set to True when the leaderboard is being updatedm, else False."""
    global update_status
    update_status = True

    leaderboard = []
    for user_id, data in all_user_files():
        reputation = data.get("reputation", 0)
        leaderboard.append((user_id, reputation))
    
    leaderboard.sort(key=lambda x: x[1], reverse=True)

    global embeds, embeds_with_ids
    embeds, embeds_with_ids = [], []

    per_page = 20
    for i in range(0, len(leaderboard), per_page):
        embed = discord.Embed(title="\U0001F3C6 Reputation Leaderboard \U0001F3C6", color=discord.Color.gold())
        embed_with_ids = discord.Embed(title="\U0001F3C6 Reputation Leaderboard \U0001F3C6", color=discord.Color.gold())

        lines = []
        lines_with_ids = []
        medals = {1: "\U0001F947", 2: "\U0001F948", 3: "\U0001F949"}

        for rank, (user_id, rep) in enumerate(leaderboard[i:i + per_page], start=i + 1):
            try:
                user = await bot.fetch_user(user_id)
                username = user.name
            except:
                username = f"Unknown ({user_id})"
            
            prefix = medals.get(rank, f"`#{rank}`")
            lines.append(f"{prefix} **{username}** — {rep} rep")
            lines_with_ids.append(f"{prefix} **{username}** — {rep} rep\n`{user_id}`")

        embed.description = "\n".join(lines)
        embed_with_ids.description = "\n".join(lines_with_ids)

        embed_with_ids.set_footer(text=f"Page {i // per_page + 1}/{(len(leaderboard) - 1) // per_page + 1}")
        embed.set_footer(text=f"Page {i // per_page + 1}/{(len(leaderboard) - 1) // per_page + 1}")

        embeds_with_ids.append(embed_with_ids)
        embeds.append(embed)

    global view, view_with_ids
    view = Paginator(embeds)
    view_with_ids = Paginator(embeds_with_ids)

    update_status = False

    await asyncio.sleep(300) # 5 minutes

@bot.tree.command(name="leaderboard", description="See the top users with the highest reputation.")
@discord.app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def rep_leaderboard(interaction: discord.Interaction, show_ids: bool = False):
    await interaction.response.defer()

    if embeds:
        if show_ids:
            view_with_ids.reset()
            view_with_ids.message = await interaction.followup.send(embed=embeds_with_ids[0], view=view_with_ids)
        else:
            view.reset()
            view.message = await interaction.followup.send(embed=embeds[0], view=view)
    else:
        await interaction.followup.send("No reputation data available.")

@bot.tree.command(name="rep_delete", description="Delete a specific reputation comment by its ID.")
@discord.app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def rep_delete(interaction: discord.Interaction, comment_id: int):
    user = interaction.user

    if not user_exists(user.id):
        await interaction.response.send_message(f"No reputation data found for {user.name}.", ephemeral=True)
        return

    user_data = load_user(user.id)
    comments = user_data.get("comments", [])

    if comment_id < 1 or comment_id > len(comments):
        await interaction.response.send_message(f"Invalid comment ID. {user.name} has {len(comments)} comments.", ephemeral=True)
        return

    # Delete the comment (1-based index)
    deleted_comment = comments.pop(comment_id - 1)  # Since JSON order is unchanged
    save_user(user.id, user_data)

    await interaction.response.send_message(
        f"Deleted comment **[{comment_id}]** from {user.name}: `{deleted_comment['comment']}`",
        ephemeral=True
    )

@bot.event
async def on_ready():
    await bot.tree.sync()
    bot.loop.create_task(update_leaderboard())
    print("Loaded")

async def update_leaderboard():
     while True:
         try:
            await leaderboard_data()
         except Exception as e:
                print(f"Leaderboard update failed: {e}")
                await asyncio.sleep(300)

bot.run(os.getenv("DISCORD_BOT_TOKEN"))