from dataclasses import dataclass

import datetime
import discord

from user_manager import load_user, save_user

@dataclass
class StreakData:
    current_streak: int
    max_streak: int
    last_claimed: datetime.datetime

    @staticmethod
    def from_dict(data):
        return StreakData(
            current_streak=data["current_streak"],
            max_streak=data["max_streak"],
            last_claimed=datetime.datetime.fromisoformat(data["last_claimed"])
        )

    def to_dict(self):
        return {
            "current_streak": self.current_streak,
            "max_streak": self.max_streak,
            "last_claimed": self.last_claimed.isoformat()
        }

def get_streak(user_id):
    """Returns user's streak data, returns defaults for legacy data"""
    user_data = load_user(user_id)

    if "streak" not in user_data:
        return StreakData(
            current_streak=0,
            max_streak=0,
            last_claimed=datetime.datetime.min.replace(tzinfo=datetime.UTC)
        )
    
    return StreakData.from_dict(user_data["streak"])

def check_streak_expiration(user_id):
    """Returns True if users daily streak has expired, else False"""
    cooldown_time = datetime.timedelta(hours=36)
    last_claimed = get_streak(user_id).last_claimed
    return datetime.datetime.now(datetime.UTC) - last_claimed > cooldown_time

def check_streak_cooldown(user_id):
    """Returns True if the users daily streak is on cooldown, else False"""
    last_claimed = get_streak(user_id).last_claimed
    return datetime.datetime.now(datetime.UTC).date() == last_claimed.date()

def write_streak(user_id, streak):
    """Writes streak to user data"""
    user_data = load_user(user_id)
    user_data["streak"] = streak.to_dict()
    save_user(user_id, user_data)

def update_streak(user_id):
    """Checks if current streak is a max streak and resets streak if it has expired"""
    streak = get_streak(user_id)
    if streak.current_streak > streak.max_streak:
        streak.max_streak = streak.current_streak
    if check_streak_expiration(user_id):
        streak.current_streak = 0
    write_streak(user_id, streak)

def increase_streak(user_id):
    """Increases streak if it's not on cooldown"""
    if not check_streak_cooldown(user_id):
        streak = get_streak(user_id)
        streak.current_streak += 1
        streak.last_claimed = datetime.datetime.now(datetime.UTC)
        write_streak(user_id, streak)

        return streak

async def handle_streak(interaction: discord.Interaction, user_id):
    """Entrypoint for streak logic"""
    update_streak(user_id)

    streak = increase_streak(user_id)
    if streak is not None:
        await interaction.followup.send(
            f"\U0001f525 **Daily streak increased!** You are on a **{streak.current_streak}-day** streak!",
            ephemeral=True
        )