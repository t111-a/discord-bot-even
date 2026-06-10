import discord
from discord.ext import commands
import sqlite3
import asyncio
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="-", intents=intents, help_command=None)

# إعدادات البوت والبيانات
game_settings = {"wheel_url": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHJ4ZzVqbmRzZ254ZzVqbmRzZ254ZzVqbmRzZ254ZzVqbmRzJmVwPXYxX2ludGVybmFsX2dpZl9ieV9pZCZjdD1n/3o7TKMGpxxHOGTdzJC/giphy.gif"}
game_sessions = {}

@bot.command()
async def roulette(ctx):
    if ctx.channel.id in game_sessions:
        await ctx.send("هناك جولة تعمل بالفعل!")
        return

    game_sessions[ctx.channel.id] = {"players": []}
    
    view = discord.ui.View(timeout=None)
    view.add_item(discord.ui.Button(label="انضمام", style=discord.ButtonStyle.primary, custom_id="join_game"))
    view.add_item(discord.ui.Button(label="المتجر", style=discord.ButtonStyle.secondary, custom_id="shop"))
    
    msg = await ctx.send(f"🎡 **Roulette Game**\n🕒 Time: 30s\n👥 Players: 0\n{game_settings['wheel_url']}", view=view)
    
    # العداد التنازلي
    for i in range(30, 0, -5):
        await asyncio.sleep(5)
        count = len(game_sessions[ctx.channel.id]["players"])
        await msg.edit(content=f"🎡 **Roulette Game**\n🕒 Time: {i-5}s\n👥 Players: {count}\n{game_settings['wheel_url']}")
    
    await ctx.send("🚫 انتهى وقت الانضمام!")
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
    elif interaction.data.get("custom_id") == "shop":
        await interaction.response.send_message("🛍️ المتجر قريباً...", ephemeral=True)

bot.run(os.environ["DISCORD_TOKEN"])
