import discord
from discord.ext import commands
import sqlite3
import asyncio
import os
import random

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="-", intents=intents, help_command=None)

# إعدادات اللعبة (للكل)
config = {
    "wheel_url": "https://media.giphy.com/media/3o7TKMGpxxHOGTdzJC/giphy.gif",
    "time": 30,
    "max_players": 10
}

conn = sqlite3.connect('game_data.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, points INTEGER)''')
conn.commit()

game_sessions = {}

# --- 1. الإعدادات ---
@bot.command()
@commands.has_permissions(administrator=True)
async def setconfig(ctx, key: str, value: str):
    if key in config:
        config[key] = value if key == "wheel_url" else int(value)
        await ctx.send(f"تم تحديث {key} إلى {value}")
    else:
        await ctx.send("هذا الإعداد غير موجود")

# --- 2. الروليت الإقصائي (الكل يشوف) ---
@bot.command()
async def roulette(ctx):
    if ctx.channel.id in game_sessions: return
    game_sessions[ctx.channel.id] = {"players": []}
    
    embed = discord.Embed(title="روليت الاقصاء", description=f"الوقت: {config['time']} ث\nاللاعبين: 0/{config['max_players']}")
    embed.set_image(url=config['wheel_url'])
    
    view = discord.ui.View()
    # الزر للكل
    view.add_item(discord.ui.Button(label="انضمام", custom_id="join_game"))
    
    msg = await ctx.send(embed=embed, view=view)
    
    await asyncio.sleep(config['time'])
    
    players = game_sessions[ctx.channel.id]["players"]
    if len(players) < 2:
        await ctx.send("عدد اللاعبين غير كافٍ")
        return

    # نظام الإقصاء (الكل يشوف الخروج)
    while len(players) > 1:
        await asyncio.sleep(3)
        loser = random.choice(players)
        players.remove(loser)
        await ctx.send(f"تم اقصاء {loser.name} ! المتبقون: {len(players)}")
    
    await ctx.send(f"الفائز هو {players[0].mention}!")
    del game_sessions[ctx.channel.id]

# --- 3. البنك والأوامر ---
@bot.command()
async def points(ctx):
    c.execute("SELECT points FROM users WHERE id=?", (ctx.author.id,))
    res = c.fetchone()
    await ctx.send(f"رصيدك: {res[0] if res else 0}")

@bot.command()
async def transfer(ctx, member: discord.Member, amount: int):
    c.execute("UPDATE users SET points = points - ? WHERE id=?", (amount, ctx.author.id))
    c.execute("INSERT OR REPLACE INTO users (id, points) VALUES (?, COALESCE((SELECT points FROM users WHERE id=?), 0) + ?)", (member.id, member.id, amount))
    conn.commit()
    await ctx.send(f"تم تحويل {amount} لـ {member.name}")

# --- 4. الـ Help (نصي صريح) ---
@bot.command()
async def help(ctx):
    text = "قائمة الاوامر:\n\n-roulette : بدء الجولة\n-points : رصيدك\n-transfer : تحويل نقاط\n-give : توزيع (للادارة)\n-setconfig : ضبط الاعدادات"
    await ctx.send(text)

@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.data.get("custom_id") == "join_game":
        cid = interaction.channel.id
        if cid in game_sessions and interaction.user not in game_sessions[cid]["players"]:
            if len(game_sessions[cid]["players"]) < config["max_players"]:
                game_sessions[cid]["players"].append(interaction.user)
                await interaction.response.send_message(f"{interaction.user.name} انضم للجولة!")
            else:
                await interaction.response.send_message("الجولة ممتلئة!")
        else:
            await interaction.response.send_message("انت منضم بالفعل!")

bot.run(os.environ["DISCORD_TOKEN"])
