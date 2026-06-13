import discord
import asyncio
import os
from discord.ext import commands

OWNER_ID = 1327923220329926677
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="", intents=intents)

# متغير لحفظ حالة الثمنيل
thumbnail_enabled = True

def get_embed(title, description=""):
    embed = discord.Embed(title=title, description=description, color=0x2b2d31)
    if thumbnail_enabled:
        embed.set_thumbnail(url=bot.user.avatar.url)
    return embed

# --- إعدادات أخرى (الثمنيل) ---
class OtherSettingsView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    
    @discord.ui.button(label="تفعيل / تعطيل الثمنيل", style=discord.ButtonStyle.secondary)
    async def toggle_thumb(self, i, b):
        global thumbnail_enabled
        thumbnail_enabled = not thumbnail_enabled
        status = "مفعل" if thumbnail_enabled else "معطل"
        await i.response.send_message(f"✅ تم تغيير حالة الثمنيل إلى: {status}", ephemeral=True)

    @discord.ui.button(label="رجوع", style=discord.ButtonStyle.secondary)
    async def back(self, i, b): await i.response.edit_message(embed=get_embed("الإعدادات"), view=MainSettingsView())

# --- القائمة الرئيسية ---
class MainSettingsView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    
    @discord.ui.select(placeholder="قائمة التحكم", options=[
        discord.SelectOption(label="إعدادات البوت", value="bot"),
        discord.SelectOption(label="إعدادات عامة", value="general"),
        discord.SelectOption(label="إعدادات أخرى", description="تفعيل / تعطيل الثمنيل في الردود", value="other")
    ])
    async def select(self, i: discord.Interaction, s: discord.ui.Select):
        if s.values[0] == "other":
            await i.response.edit_message(embed=get_embed("إعدادات أخرى", "تحكم في خيارات البوت الإضافية"), view=OtherSettingsView())
        # ... باقي القوائم

# --- نظام التشغيل ---
@bot.event
async def on_message(message):
    if message.author.bot: return
    if "settings" in message.content.lower() and bot.user.mentioned_in(message):
        if message.author.id == OWNER_ID:
            await message.reply(embed=get_embed("لوحة التحكم"), view=MainSettingsView())
    
    if message.content.startswith(('ش ', 'p ')):
        song = message.content.split(' ', 1)[1]
        await message.reply(embed=get_embed("يشتغل الحين:", song), view=MusicControls())

bot.run(os.environ['DISCORD_TOKEN'])
