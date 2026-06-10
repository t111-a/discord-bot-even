import discord
from discord.ext import commands
import sqlite3
import random
import asyncio
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="-", intents=intents, help_command=None)

# --- Database ---
conn = sqlite3.connect('game_data.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, points INTEGER)''')
conn.commit()

# --- Help Select Menu ---
class HelpSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Games", description="View game commands"),
            discord.SelectOption(label="Admin", description="View admin commands"),
            discord.SelectOption(label="Bank", description="View bank commands")
        ]
        super().__init__(placeholder="Select a category...", options=options)

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "Games":
            content = "Games Category:\n-roulette - Start a roulette round"
        elif self.values[0] == "Admin":
            content = "Admin Category:\n-setup - Initialize system\n-give [user] [amount] - Give points"
        else:
            content = "Bank Category:\n-points - Check your balance"
        await interaction.response.edit_message(content=content)

class HelpView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(HelpSelect())

@bot.command()
async def help(ctx):
    await ctx.send("Select a category below:", view=HelpView())

# --- Roulette Game ---
@bot.command()
async def roulette(ctx):
    await ctx.send("Roulette round started! Click the button below to join:", view=RouletteJoinView())

class RouletteJoinView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=30)
        self.players = []

    @discord.ui.button(label="Join", style=discord.ButtonStyle.primary)
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user not in self.players:
            self.players.append(interaction.user)
            await interaction.response.send_message("Joined!", ephemeral=True)
        else:
            await interaction.response.send_message("Already joined!", ephemeral=True)

# --- Admin & Bank ---
@bot.command()
@commands.has_permissions(administrator=True)
async def give(ctx, member: discord.Member, amount: int):
    c.execute("INSERT OR REPLACE INTO users (id, points) VALUES (?, COALESCE((SELECT points FROM users WHERE id=?), 0) + ?)", (member.id, member.id, amount))
    conn.commit()
    await ctx.send(f"Added {amount} points to {member.name}")

@bot.command()
async def points(ctx):
    c.execute("SELECT points FROM users WHERE id=?", (ctx.author.id,))
    res = c.fetchone()
    pts = res[0] if res else 0
    await ctx.send(f"Your balance: {pts} points")

bot.run(os.environ["DISCORD_TOKEN"])
