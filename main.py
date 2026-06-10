import discord
from discord.ext import commands
import sqlite3
import random
import asyncio
import os

# إعدادات البوت
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="-", intents=intents, help_command=None)

# --- إعداد قاعدة البيانات ---
def init_db():
    conn = sqlite3.connect('game_data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, points INTEGER)''')
    conn.commit()
    conn.close()

init_db()

# --- وظائف النقاط ---
def get_points(user_id):
    conn = sqlite3.connect('game_data.db')
    c = conn.cursor()
    c.execute("SELECT points FROM users WHERE id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else 0

def add_points(user_id, amount):
    conn = sqlite3.connect('game_data.db')
    c = conn.cursor()
    current = get_points(user_id)
    c.execute("INSERT OR REPLACE INTO users (id, points) VALUES (?, ?)", (user_id, current + amount))
    conn.commit()
    conn.close()

# --- الروليت ---
class RouletteView(discord.ui.View):
    def __init__(self, players):
        super().__init__(timeout=None)
        self.players = players

    @discord.ui.button(label="انضمام", style=discord.ButtonStyle.green)
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user not in self.players:
            self.players.append(interaction.user)
            await interaction.response.send_message(f"✅ انضم {interaction.user.name}", ephemeral=True)
        else:
            await interaction.response.send_message("⚠️ أنت مشترك!", ephemeral=True)

@bot.command()
async def روليت(ctx):
    players = []
    view = RouletteView(players)
    embed = discord.Embed(title="🎡 روليت - العجلة الكبرى", description="نظام احترافي | بانتظار 3 لاعبين للبدء...", color=discord.Color.red())
    embed.add_field(name="اللاعبين", value="0", inline=True)
    msg = await ctx.send(embed=embed, view=view)
    await asyncio.sleep(30)
    
    if len(players) < 3:
        await ctx.send("❌ تم الإلغاء، العدد أقل من 3 لاعبين.")
    else:
        await ctx.send(f"🔥 **بدأت الجولة!** المشاركون: {len(players)}")
        winner = random.choice(players)
        add_points(winner.id, 1)
        await ctx.send(f"🎉 الفائز: {winner.mention} (حصل على 1 نقطة)")

# --- أوامر النظام والتحكم ---
@bot.command()
async def هيلب(ctx):
    embed = discord.Embed(title="🎮 مركز الأوامر الاحترافي", color=discord.Color.dark_purple())
    embed.add_field(name="🎡 الألعاب", value="`-روليت` - بدء جولة جديدة", inline=False)
    embed.add_field(name="💰 النظام المالي", value="`-نقاطي` - عرض رصيدك\n`-توزيع` - توزيع نقاط (للمشرفين)", inline=False)
    embed.add_field(name="⚙️ التحكم", value="`-setup` - إظهار اللوحة", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def نقاطي(ctx):
    p = get_points(ctx.author.id)
    await ctx.send(f"💰 رصيدك الحالي: {p} نقطة")

@bot.command()
@commands.has_permissions(administrator=True)
async def توزيع(ctx, member: discord.Member, amount: int):
    add_points(member.id, amount)
    await ctx.send(f"✅ تم إضافة {amount} نقطة لـ {member.name}")

@bot.command()
async def setup(ctx):
    embed = discord.Embed(title="🎮 لوحة التحكم", description="استخدم الأزرار:", color=discord.Color.blue())
    await ctx.send(embed=embed)

bot.run(os.environ["DISCORD_TOKEN"])
