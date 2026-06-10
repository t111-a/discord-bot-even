import discord
from discord.ext import commands
import os
import random
import json

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="-", intents=intents, help_command=None)

SETTINGS_FILE = "settings.json"

# تحميل الإعدادات من الملف
def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f: return json.load(f)
    return {"help_channel": None, "game_channel": None}

# حفظ الإعدادات في الملف
def save_settings(data):
    with open(SETTINGS_FILE, "w") as f: json.dump(data, f)

config = load_settings()

# --- الإعدادات التفاعلية ---
@bot.command()
@commands.has_permissions(administrator=True)
async def sethelp(ctx):
    await ctx.send("✅ منشن شات المساعدة:")
    msg = await bot.wait_for('message', check=lambda m: m.author == ctx.author)
    if msg.channel_mentions:
        config["help_channel"] = msg.channel_mentions[0].id
        save_settings(config)
        await ctx.send("تم حفظ شات المساعدة!")

@bot.command()
@commands.has_permissions(administrator=True)
async def setgame(ctx):
    await ctx.send("✅ منشن شات الألعاب:")
    msg = await bot.wait_for('message', check=lambda m: m.author == ctx.author)
    if msg.channel_mentions:
        config["game_channel"] = msg.channel_mentions[0].id
        save_settings(config)
        await ctx.send("تم حفظ شات الألعاب!")

# --- القائمة التفاعلية (Help) ---
@bot.command()
async def help(ctx):
    if config["help_channel"] and ctx.channel.id != config["help_channel"]: return
    embed = discord.Embed(title="🤖 Control Panel", description="1. روليت\n2. نرد", color=discord.Color.blue())
    await ctx.send(embed=embed)

# --- نظام الأوامر المباشرة ---
@bot.event
async def on_message(message):
    if message.author.bot: return
    
    # أوامر الألعاب المباشرة بالعربي
    if message.content.strip() == "روليت":
        if config["game_channel"] and message.channel.id != config["game_channel"]: return
        await message.channel.send("🎡 بدأت جولة الروليت!")
    
    elif message.content.strip() == "نرد":
        if config["game_channel"] and message.channel.id != config["game_channel"]: return
        await message.channel.send(f"🎲 النتيجة: {random.randint(1, 6)}")

    await bot.process_commands(message)

bot.run(os.environ["DISCORD_TOKEN"])
