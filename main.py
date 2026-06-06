import discord
from discord.ext import commands
import random
import asyncio
import os
import re
import io
import time
import aiohttp
import json
from PIL import Image, ImageDraw, ImageFont, ImageOps

# إعداد البوت
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="-", intents=intents, help_command=None)

# ================= دالة إدارة النقاط =================
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

# ================= إعدادات الروليت =================
roulette_config = {
    "max_players": 20, "signup_time": 30, "settings_channel_id": None,
    "allowed_channels": [], "bg_url": "https://i.ibb.co/V9Xm8Yn/roulette-wheel.gif",
    "features_enabled": True, "bomb_enabled": True, "protection_chance": 0.15,
    "counter_chance": 0.15, "msg_timeout": "تم طرد {victim} لعدم الاختيار",
    "msg_random": "تم طرد {victim} عشوائياً", "msg_normal": "تم طرد {victim} من الجولة"
}

# ================= محرك تصميم الفائز مع الأجنحة =================
async def generate_winner_image(avatar_url: str, name: str) -> io.BytesIO:
    avatar_bytes = await download_image(avatar_url)
    if not avatar_bytes: return None
    avatar_img = Image.open(io.BytesIO(avatar_bytes)).convert("RGBA")
    base_img = Image.new("RGBA", (800, 500), (0, 0, 0, 0))
    
    # دمج الأجنحة (تأكد من وجود wings.png في المجلد)
    if os.path.exists("wings.png"):
        wings = Image.open("wings.png").convert("RGBA").resize((800, 500))
        base_img.alpha_composite(wings)
    
    # ... (بقية كود الرسم الذي أرسلته سابقاً) ...
    # (تم اختصار الجزء هنا لتوفير المساحة، استخدم كودك الأصلي للرسم مع إضافة الأسطر أعلاه)
    
    output = io.BytesIO()
    base_img.save(output, format="PNG")
    output.seek(0)
    return output

# ================= أوامر النقاط الجديدة =================
@bot.command(name="points")
async def points(ctx, member: discord.Member = None):
    member = member or ctx.author
    data = load_data()
    stats = data.get(str(member.id), {"roulette": 0, "team": 0, "solo": 0, "total": 0})
    
    embed = discord.Embed(title="نقاطي", color=0x99AAB5)
    embed.set_author(name=member.display_name, icon_url=member.avatar.url)
    embed.add_field(name="Total Points", value=f"**{stats['total']}**", inline=False)
    embed.add_field(name="Roulette", value=f"{stats['roulette']}", inline=True)
    embed.add_field(name="Team", value=f"{stats['team']}", inline=True)
    embed.add_field(name="Solo", value=f"{stats['solo']}", inline=True)
    await ctx.send(embed=embed)

@bot.command(name="add_points")
@commands.has_permissions(administrator=True)
async def add_points(ctx, member: discord.Member, amount: int, category: str = "roulette"):
    update_points(member.id, category, amount)
    await ctx.send(f"✅ تم إضافة {amount} نقطة لـ {member.display_name}")

# ================= دمج الربط التلقائي =================
# في نهاية دالة start_roulette داخل (if len(players) == 1):
# أضف السطر التالي:
# update_points(winner.id, "roulette", 50)
