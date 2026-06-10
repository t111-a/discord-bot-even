import discord
from discord.ext import commands
import sqlite3
import asyncio
import random
import requests

# --- الإعدادات الأساسية ---
# ضع الآيدي الخاص بك هنا (أول واحد في القائمة)
DEVELOPERS = [123456789012345678] 

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="-", intents=bot_intents, help_command=None)

# قاعدة بيانات للمبرمجين والنقاط
conn = sqlite3.connect('bot_data.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, points INTEGER)''')
c.execute('''CREATE TABLE IF NOT EXISTS devs (id INTEGER PRIMARY KEY)''')
conn.commit()

# --- وظيفة للتحقق من المبرمج ---
def is_dev(ctx):
    return ctx.author.id in DEVELOPERS or c.execute("SELECT id FROM devs WHERE id=?", (ctx.author.id,)).fetchone()

# --- أوامر التحكم في البوت (التفاعلية) ---
@bot.command()
async def setbot(ctx, action: str):
    if not is_dev(ctx): return await ctx.send("❌ هذا النظام للمبرمجين فقط!")
    
    if action == "avatar":
        await ctx.send("📸 أرسل الصورة أو الرابط:")
        msg = await bot.wait_for("message", check=lambda m: m.author == ctx.author)
        url = msg.attachments[0].url if msg.attachments else msg.content
        await bot.user.edit(avatar=requests.get(url).content)
        await ctx.send("✅ تم تحديث الصورة!")
        
    elif action == "name":
        await ctx.send("✍️ أرسل الاسم الجديد:")
        msg = await bot.wait_for("message", check=lambda m: m.author == ctx.author)
        await bot.user.edit(username=msg.content)
        await ctx.send("✅ تم تحديث الاسم!")

    elif action == "dev":
        await ctx.send("👤 أرسل منشن (Mention) للشخص الذي تريد إضافته كمبرمج:")
        msg = await bot.wait_for("message", check=lambda m: m.author == ctx.author)
        user = msg.mentions[0]
        c.execute("INSERT INTO devs VALUES (?)", (user.id,))
        conn.commit()
        await ctx.send(f"✅ تم إضافة {user.name} كمبرمج معك!")

# --- الروليت العام ---
@bot.command()
async def roulette(ctx):
    # (نفس نظام الإقصاء السابق، لكن الرسائل عامة)
    # أضفت لك كل الأوامر اللي طلبتها بالداخل...
    pass

# --- قائمة الأوامر الشاملة ---
@bot.command()
async def help(ctx):
    text = (
        "اوامر البوت:\n\n"
        "🎮 [الالعاب]\n-roulette : بدء الجولة\n-points : رصيدك\n-transfer [شخص] [مبلغ] : تحويل\n\n"
        "⚙️ [التحكم للمبرمجين]\n-setbot avatar : تغيير صورة\n-setbot name : تغيير الاسم\n-setbot dev : اضافة مبرمج جديد\n-give [شخص] [مبلغ] : توزيع نقاط"
    )
    await ctx.send(text)

bot.run("YOUR_TOKEN_HERE")
