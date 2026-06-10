import discord
from discord.ext import commands
import sqlite3
import asyncio
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="-", intents=intents, help_command=None)

# إعداد قاعدة البيانات
conn = sqlite3.connect('game_data.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, points INTEGER)''')
conn.commit()

# إعدادات العجلة (رابط الـ GIF)
game_settings = {"wheel_url": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHJ4ZzVqbmRzZ254ZzVqbmRzZ254ZzVqbmRzZ254ZzVqbmRzJmVwPXYxX2ludGVybmFsX2dpZl9ieV9pZCZjdD1n/3o7TKMGpxxHOGTdzJC/giphy.gif"}
game_sessions = {}

@bot.command()
async def setwheel(ctx, url: str):
    game_settings["wheel_url"] = url
    await ctx.send("✅ تم تحديث العجلة بنجاح!")

@bot.command()
async def roulette(ctx):
    if ctx.channel.id in game_sessions:
        await ctx.send("هناك جولة تعمل بالفعل!")
        return

    game_sessions[ctx.channel.id] = {"players": []}
    
    # رسالة العداد
    msg = await ctx.send(f"🎡 **جولة روليت**\nالوقت المتبقي: 30 ثانية\nعدد اللاعبين: 0")
    # رسالة الصورة (ستظهر كصورة مباشرة)
    img_msg = await ctx.send(game_settings['wheel_url'])
    
    view = discord.ui.View()
    view.add_item(discord.ui.Button(label="انضمام", style=discord.ButtonStyle.primary, custom_id="join_game"))
    await ctx.send("اضغط انضمام للمشاركة:", view=view)
    
    for i in range(30, 0, -5):
        await asyncio.sleep(5)
        count = len(game_sessions[ctx.channel.id]["players"])
        await msg.edit(content=f"🎡 **جولة روليت**\nالوقت المتبقي: {i-5} ثواني\nعدد اللاعبين: {count}")
    
    await ctx.send("🚫 انتهى وقت الانضمام! بدأت الجولة.")
    del game_sessions[ctx.channel.id]

@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.data.get("custom_id") == "join_game":
        cid = interaction.channel.id
        if cid in game_sessions:
            if interaction.user not in game_sessions[cid]["players"]:
                game_sessions[cid]["players"].append(interaction.user)
                await interaction.response.send_message("✅ تم انضمامك!", ephemeral=True)
            else:
                await interaction.response.send_message("❌ أنت منضم بالفعل!", ephemeral=True)

@bot.command()
async def points(ctx):
    c.execute("SELECT points FROM users WHERE id=?", (ctx.author.id,))
    res = c.fetchone()
    pts = res[0] if res else 0
    await ctx.send(f"رصيدك هو: {pts} نقطة")

bot.run(os.environ["DISCORD_TOKEN"])
