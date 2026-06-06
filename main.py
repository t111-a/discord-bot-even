import discord
from discord.ext import commands
import random, asyncio, os, re, io, time, aiohttp, json
from PIL import Image, ImageDraw, ImageFont, ImageOps

# إعداد البوت
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="-", intents=intents, help_command=None)

# ================= قاعدة البيانات =================
def load_data():
    if not os.path.exists('data.json'): return {}
    with open('data.json', 'r') as f: return json.load(f)

def save_data(data):
    with open('data.json', 'w') as f: json.dump(data, f, indent=4)

def update_points(user_id, category, amount):
    data = load_data()
    uid = str(user_id)
    if uid not in data: data[uid] = {"roulette": 0, "team": 0, "solo": 0, "total": 0}
    data[uid][category] += amount
    data[uid]["total"] += amount
    save_data(data)

# ================= الإعدادات =================
config = {
    "max_players": 20, "signup_time": 30, "settings_channel_id": None,
    "allowed_channels": [], "bomb_enabled": True, "protection_chance": 0.15
}

# ================= الأوامر =================
@bot.command(name="points")
async def points(ctx, member: discord.Member = None):
    member = member or ctx.author
    data = load_data()
    stats = data.get(str(member.id), {"roulette": 0, "team": 0, "solo": 0, "total": 0})
    
    embed = discord.Embed(title="Player Statistics", color=0x2C3E50)
    embed.set_author(name=member.display_name, icon_url=member.avatar.url)
    embed.add_field(name="Total Points", value=f"{stats['total']}", inline=False)
    embed.add_field(name="Roulette", value=f"{stats['roulette']}", inline=True)
    embed.add_field(name="Team", value=f"{stats['team']}", inline=True)
    embed.add_field(name="Solo", value=f"{stats['solo']}", inline=True)
    await ctx.send(embed=embed)

@bot.command(name="add_points")
@commands.has_permissions(administrator=True)
async def add_points(ctx, member: discord.Member, amount: int, category: str = "roulette"):
    update_points(member.id, category, amount)
    await ctx.send(f"Done: Added {amount} to {member.display_name}")

# ================= واجهة الأزرار المودرن =================
class GamePlayView(discord.ui.View):
    def __init__(self, ctx, players, role):
        super().__init__(timeout=15.0)
        self.players = players
        self.role = role
        for i, p in enumerate(players[:12]):
            btn = discord.ui.Button(label=f"{p.display_name[:10]}", style=discord.ButtonStyle.secondary, custom_id=f"p_{p.id}")
            btn.callback = self.btn_callback
            self.add_item(btn)
        
        # أزرار مودرن بدون إيموجيات
        self.add_item(discord.ui.Button(label="Revive", style=discord.ButtonStyle.primary, custom_id="revive"))
        self.add_item(discord.ui.Button(label="Random", style=discord.ButtonStyle.primary, custom_id="random"))
        if config["bomb_enabled"]:
            self.add_item(discord.ui.Button(label="Bomb", style=discord.ButtonStyle.danger, custom_id="bomb"))

    async def btn_callback(self, interaction: discord.Interaction):
        self.action = interaction.data['custom_id']
        self.stop()

# ================= تشغيل البوت =================
@bot.event
async def on_ready():
    print(f"Bot connected: {bot.user}")

bot.run(os.getenv("DISCORD_TOKEN"))
