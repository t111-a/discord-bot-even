import discord
from discord.ext import commands
import sqlite3
import asyncio
import os
import random

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="-", intents=intents, help_command=None)

# إعدادات النظام
config = {
    "wheel_url": "https://media.giphy.com/media/3o7TKMGpxxHOGTdzJC/giphy.gif",
    "time": 30,
    "max_players": 10
}

# --- 1. التحكم في هوية البوت (الأدمن فقط) ---
@bot.command()
@commands.has_permissions(administrator=True)
async def setbot(ctx, setting: str, *, value: str):
    """
    مثال: -setbot name البوت_الجديد
    مثال: -setbot avatar [رابط_الصورة]
    """
    try:
        if setting == "name":
            await bot.user.edit(username=value)
            await ctx.send(f"تم تغيير الاسم إلى {value}")
        elif setting == "avatar":
            import requests
            img = requests.get(value).content
            await bot.user.edit(avatar=img)
            await ctx.send("تم تغيير صورة البوت")
        elif setting == "config": # لتعديل إعدادات الروليت
            key, val = value.split(" ")
            config[key] = int(val) if val.isdigit() else val
            await ctx.send(f"تم تحديث {key} إلى {val}")
    except Exception as e:
        await ctx.send(f"خطأ: {e}")

# --- 2. الأوامر العامة المحمية (الكل يشوف، الأدمن ينفذ) ---
@bot.command()
async def give(ctx, member: discord.Member, amount: int):
    if ctx.author.id != [ID_حقك_هنا]: # ضع رقم آيديك هنا للحماية
        return await ctx.send("هذا الأمر للمدير فقط!")
    # ... (كود التوزيع)
    await ctx.send(f"تم توزيع {amount} لـ {member.name}")

# --- 3. نظام الروليت (العام) ---
@bot.command()
async def roulette(ctx):
    # (نفس نظام الإقصاء السابق، لكن الرسائل عامة للكل)
    pass 

# --- 4. الـ Help (الأساسي اللي طلبته) ---
@bot.command()
async def help(ctx):
    text = (
        "قائمة الاوامر:\n\n"
        "-roulette : بدء الجولة\n"
        "-points : عرض رصيدك\n"
        "-transfer [عضو] [مبلغ] : تحويل نقاط\n"
        "-give [عضو] [مبلغ] : توزيع (خاص للمدير)\n"
        "-setbot [name/avatar/config] [القيمة] : التحكم في هوية البوت (خاص للمدير)"
    )
    await ctx.send(text)

bot.run(os.environ["DISCORD_TOKEN"])
