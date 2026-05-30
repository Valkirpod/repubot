# Repubot
A Discord bot for tracking user reputation through user comments. Meant for harmless fun.

[Invite bot to your own server](https://discord.com/oauth2/authorize?client_id=1336229817611321354&permissions=2048&integration_type=0&scope=applications.commands+bot)

### Commands
If a user is not specified, it'll pick you by default.
| Command | Description |
|---------|-------------|
| `/rep_plus @user comment` | Give positive rep with comment text |
| `/rep_minus @user comment` | Give negative rep with comment text |
| `/rep_show @user` | View someone's reputation and comments |
| `/leaderboard show_ids` | See top users by reputation |
| `/rep_delete id` | Delete one of your comments on your page (does not affect your rep balance) |

### Self-hosting
1. Clone the repo
2. `pip install -r requirements.txt`
3. Create a `.env` file with `DISCORD_BOT_TOKEN=your_token_here`
4. `python main.py`
