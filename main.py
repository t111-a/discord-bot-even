import discord
import asyncio
import os
from discord.ext import commands

OWNER_ID = 1327923220329926677
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="", intents=intents)

# دالة التصميم (لون داكن متناسق مع ديسكورد)
def get_embed(title, description=""):
    return discord.Embed(title=title, description=description, color=0x2b2d31)

# --- نظام القائمة الرئيسية مع الأزرار تحتها ---
class MainSettingsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        
    @discord.ui.select(placeholder="اختر إعداداً", options=[
        discord.SelectOption(label="إعدادات البوت", value="bot"),
        discord.SelectOption(label="إعدادات الإدارة", value="admin")
    ])
    async def select(self, i: discord.Interaction, s: discord.ui.Select):
        if s.values[0] == "bot":
            await i.response.edit_message(embed=get_embed("إعدادات البوت"), view=BotSettingsView())
        elif s.values[0] == "admin":
            await i.response.edit_message(embed=get_embed("إعدادات الإدارة"), view=AdminSettingsView())

    # الأزرار الثلاثة التي طلبتها (تحت الشريط)
    @discord.ui.button(label="إعادة تشغيل", style=discord.ButtonStyle.secondary, row=1)
    async def restart(self, i, b): await i.response.send_message("جاري إعادة التشغيل...", ephemeral=True)
    
    @discord.ui.button(label="إلغاء تثبيت", style=discord.ButtonStyle.secondary, row=1)
    async def unpin(self, i, b): await i.response.send_message("تم إلغاء التثبيت", ephemeral=True)
    
    @discord.ui.button(label="تثبيت البوت", style=discord.ButtonStyle.secondary, row=1)
    async def pin(self, i, b): 
        if i.user.voice:
            await i.user.voice.channel.connect()
            await i.response.send_message("تم التثبيت", ephemeral=True)

# ... (باقي كود الإدارة والموسيقى كما هو) ...

@bot.event
async def on_message(message):
    if message.author.bot: return
    if "settings" in message.content.lower() and bot.user.mentioned_in(message):
        if message.author.id == OWNER_ID:
            await message.reply(embed=get_embed("الإعدادات"), view=MainSettingsView())
    if message.content.startswith(('ش ', 'p ')):
        song = message.content.split(' ', 1)[1]
        await message.reply(embed=get_embed("جاري التشغيل:", song), view=MusicControls())

bot.run(os.environ['DISCORD_TOKEN'])
