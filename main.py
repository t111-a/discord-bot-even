import discord
from discord.ext import commands
import sqlite3
import asyncio
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="-", intents=intents, help_command=None)

conn = sqlite3.connect('game_data.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, points INTEGER)''')
conn.commit()

game_settings = {"wheel_url": "https://media.giphy.com/media/3o7TKMGpxxHOGTdzJC/giphy.gif"}
game_sessions = {}

# --- 1. قائمة Help المنسدلة ---
class HelpSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="الألعاب", description="أوامر الروليت والألعاب"),
            discord.SelectOption(label="المدير", description="أوامر الإدارة"),
            discord.SelectOption(label="البنك", description="أوامر النقاط والتحويل")
        ]
        super().__init__(placeholder="اختر الفئة...", options=options)

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "الألعاب":
            embed = discord.Embed(title="🎮 قسم الألعاب", description="-roulette : بدء جولة\n-stop : إيقاف اللعبة")
        elif self.values[0] == "المدير":
            embed = discord.Embed(title="⚙️ قسم الإدارة", description="-give [user] [amount] : توزيع\n-reset [user] : تصفير")
        else:
            embed = discord.Embed(title="💰 قسم البنك", description="-points : عرض رصيدك\n-transfer [user] [amount] : تحويل")
        await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.command()
async def help(ctx):
    view = discord.ui.View()
    view.add_item(HelpSelect())
    await ctx.send("قائمة الأوامر، اختر الفئة:", view=view)

# --- 2. نظام الروليت (عداد + أزرار) ---
@bot.command()
async def roulette(ctx):
    if ctx.channel.id in game_sessions:
        await ctx.send("⚠️ جولة تعمل بالفعل!")
        return

    game_sessions[ctx.channel.id] = {"players": []}
    embed = discord.Embed(title="🎡 جولة روليت", description="انتظر انضمام اللاعبين...\nالوقت المتبقي: 30 ثانية\nعدد اللاعبين: 0")
    embed.set_image(url=game_settings['wheel_url'])
    
    view = discord.ui.View()
    view.add_item(discord.ui.Button(label="انضمام", style=discord.ButtonStyle.primary, custom_id="join_game"))
    view.add_item(discord.ui.Button(label="المتجر", style=discord.ButtonStyle.secondary, custom_id="shop"))
    view.add_item(discord.ui.Button(label="حقيبتي", style=discord.ButtonStyle.secondary, custom_id="bag"))
    
    msg = await ctx.send(embed=embed, view=view)
    
    for i in range(30, 0, -5):
        await asyncio.sleep(5)
        count = len(game_sessions[ctx.channel.id]["players"])
        embed.description = f"الوقت المتبقي: {i-5} ثواني\nعدد اللاعبين: {count}"
        await msg.edit(embed=embed)
    
    await ctx.send("🚫 انتهى وقت الانضمام!")
    del game_sessions[ctx.channel.id]

# --- 3. الأوامر الأخرى (بنك + إدارة) ---
@bot.command()
async def points(ctx):
    c.execute("SELECT points FROM users WHERE id=?", (ctx.author.id,))
    res = c.fetchone()
    pts = res[0] if res else 0
    await ctx.send(f"رصيدك: {pts} نقطة")

@bot.command()
@commands.has_permissions(administrator=True)
async def give(ctx, member: discord.Member, amount: int):
    c.execute("INSERT OR REPLACE INTO users (id, points) VALUES (?, COALESCE((SELECT points FROM users WHERE id=?), 0) + ?)", (member.id, member.id, amount))
    conn.commit()
    await ctx.send(f"تم توزيع {amount} لـ {member.name}")

# --- 4. معالجة الأزرار ---
@bot.event
async def on_interaction(interaction: discord.Interaction):
    custom_id = interaction.data.get("custom_id")
    if custom_id == "join_game":
        cid = interaction.channel.id
        if cid in game_sessions and interaction.user not in game_sessions[cid]["players"]:
            game_sessions[cid]["players"].append(interaction.user)
            await interaction.response.send_message("✅ تم انضمامك!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ أنت منضم بالفعل!", ephemeral=True)
    elif custom_id == "shop":
        await interaction.response.send_message("🛍️ المتجر قريباً...", ephemeral=True)
    elif custom_id == "bag":
        await interaction.response.send_message("🎒 حقيبتك فارغة.", ephemeral=True)

bot.run(os.environ["DISCORD_TOKEN"])
