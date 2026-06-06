import discord
from discord.ext import commands
import random, asyncio, os, json, io, time
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

# ================= أوامر النقاط =================
@bot.command(name="points")
async def points(ctx, member: discord.Member = None):
    member = member or ctx.author
    data = load_data()
    stats = data.get(str(member.id), {"roulette": 0, "team": 0, "solo": 0, "total": 0})
    
    embed = discord.Embed(title="Player Statistics", color=0x2C3E50)
    embed.set_author(name=member.display_name, icon_url=member.avatar.url)
    embed.add_field(name="Total Points", value=str(stats['total']), inline=False)
    embed.add_field(name="Roulette", value=str(stats['roulette']), inline=True)
    embed.add_field(name="Team", value=str(stats['team']), inline=True)
    embed.add_field(name="Solo", value=str(stats['solo']), inline=True)
    await ctx.send(embed=embed)

# ================= منطق الروليت (الجزء الأساسي) =================
@bot.command(name="روليت")
async def start_roulette(ctx):
    # هنا تضع منطق الروليت الكامل الخاص بك (الذي أرسلته سابقاً)
    # تأكد من إضافة update_points(winner.id, "roulette", 50) عند الفوز
    await ctx.send("Roulette starting...")

@bot.command(name="help")
async def help_cmd(ctx):
    embed = discord.Embed(title="Bot Commands", color=0x2C3E50)
    embed.add_field(name="-روليت", value="Start a new game session.", inline=False)
    embed.add_field(name="-points", value="Check your current balance.", inline=False)
    embed.add_field(name="-add_points", value="Admin only: Adjust points.", inline=False)
    await ctx.send(embed=embed)

bot.run(os.getenv("DISCORD_TOKEN"))
