import discord
import asyncio
import os
from discord.ext import commands

# تم وضع الأيدي الخاص بك هنا
OWNER_ID = 1327923220329926677 

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="", intents=intents)

# --- دالة التصميم الموحد ---
def get_embed(title, description=""):
    return discord.Embed(title=title, description=description, color=0x2b2d31)

# --- لوحة التحكم بالإعدادات ---
class MainSettingsView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    
    @discord.ui.select(placeholder="قائمة الإعدادات", options=[
        discord.SelectOption(label="إعدادات البوت", value="bot"),
        discord.SelectOption(label="إعدادات الإدارة", value="admin")
    ])
    async def select(self, i: discord.Interaction, select: discord.ui.Select):
        if select.values[0] == "bot":
            await i.response.edit_message(embed=get_embed("إعدادات البوت"), view=BotSettingsView())
        elif select.values[0] == "admin":
            await i.response.edit_message(embed=get_embed("إعدادات الإدارة"), view=AdminSettingsView())

class BotSettingsView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="تثبيت في الروم", style=discord.ButtonStyle.success)
    async def pin(self, i, b):
        if i.user.voice:
            await i.user.voice.channel.connect()
            msg = await i.response.send_message("✅ تم التثبيت", ephemeral=True)
            await asyncio.sleep(3)
            await msg.delete()
    @discord.ui.button(label="رجوع", style=discord.ButtonStyle.secondary)
    async def back(self, i, b): await i.response.edit_message(embed=get_embed("القائمة"), view=MainSettingsView())

class AdminSettingsView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="إضافة مسؤول", style=discord.ButtonStyle.primary)
    async def add(self, i, b):
        await i.response.send_message("أرسل منشن الشخص الآن:", ephemeral=True)
        msg = await bot.wait_for('message', check=lambda m: m.author == i.user)
        conf = await i.followup.send(f"✅ تم تعيين {msg.content} مسؤولاً")
        await asyncio.sleep(5)
        await conf.delete()
    @discord.ui.button(label="رجوع", style=discord.ButtonStyle.secondary)
    async def back(self, i, b): await i.response.edit_message(embed=get_embed("القائمة"), view=MainSettingsView())

# --- لوحة التحكم بالموسيقى (التصميم في الشات) ---
class MusicControls(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="إيقاف مؤقت", style=discord.ButtonStyle.primary)
    async def pause(self, i, b): await i.response.send_message("⏸️ تم الإيقاف", ephemeral=True)
    @discord.ui.button(label="إنهاء", style=discord.ButtonStyle.danger)
    async def stop(self, i, b): await i.message.delete()

@bot.event
async def on_message(message):
    if message.author.bot: return
    # الإعدادات للمالك فقط
    if "settings" in message.content.lower() and bot.user.mentioned_in(message):
        if message.author.id == OWNER_ID:
            await message.reply(embed=get_embed("لوحة التحكم"), view=MainSettingsView())
    # تشغيل الأغاني
    if message.content.startswith(('ش ', 'p ')):
        song = message.content.split(' ', 1)[1]
        await message.reply(embed=get_embed("الآن يشتغل:", song), view=MusicControls())

bot.run(os.environ['DISCORD_TOKEN'])
