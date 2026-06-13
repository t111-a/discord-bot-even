import discord
from discord.ext import commands
import os

bot = commands.Bot(command_prefix="", intents=discord.Intents.all())

# --- نظام الـ Modal (لإدخال البيانات مثل المنشن أو الأسماء) ---
class InputModal(discord.ui.Modal, title='تعديل البيانات'):
    answer = discord.ui.TextInput(label='اكتب هنا:', style=discord.TextStyle.short, required=True)
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"✅ تم التنفيذ بنجاح: {self.answer}", ephemeral=True)

# --- القائمة الرئيسية ---
class MainSettingsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.select(placeholder="اختر قائمة الإعدادات...", options=[
        discord.SelectOption(label="إعدادات البوت", value="bot", emoji="🤖"),
        discord.SelectOption(label="إعدادات الإدارة", value="admin", emoji="🛡️"),
        discord.SelectOption(label="إعدادات عامة", value="general", emoji="⚙️")
    ])
    async def select(self, interaction: discord.Interaction, select: discord.ui.Select):
        if select.values[0] == "bot":
            await interaction.response.edit_message(embed=discord.Embed(title="إعدادات البوت", description="تغيير الخصائص الأساسية:"), view=BotSettingsView())
        elif select.values[0] == "admin":
            await interaction.response.edit_message(embed=discord.Embed(title="إعدادات الإدارة", description="إضافة/إزالة مسؤولين:"), view=AdminSettingsView())
        elif select.values[0] == "general":
            await interaction.response.edit_message(embed=discord.Embed(title="إعدادات عامة", description="تحكم بالرومات والمنصة:"), view=GeneralSettingsView())

# --- إعدادات البوت ---
class BotSettingsView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="تثبيت البوت", style=discord.ButtonStyle.secondary)
    async def pin(self, interaction, button): await interaction.response.send_message("تم التثبيت!", ephemeral=True)
    @discord.ui.button(label="رجوع", style=discord.ButtonStyle.danger)
    async def back(self, interaction, button): await interaction.response.edit_message(embed=discord.Embed(title="الإعدادات", description="الرئيسية"), view=MainSettingsView())

# --- إعدادات الإدارة (المسؤولين) ---
class AdminSettingsView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="إضافة مسؤول", style=discord.ButtonStyle.primary)
    async def add_admin(self, interaction, button): await interaction.response.send_modal(InputModal())
    @discord.ui.button(label="رجوع", style=discord.ButtonStyle.danger)
    async def back(self, interaction, button): await interaction.response.edit_message(embed=discord.Embed(title="الإعدادات", description="الرئيسية"), view=MainSettingsView())

# --- إعدادات عامة ---
class GeneralSettingsView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="رجوع", style=discord.ButtonStyle.danger)
    async def back(self, interaction, button): await interaction.response.edit_message(embed=discord.Embed(title="الإعدادات", description="الرئيسية"), view=MainSettingsView())

# --- الأحداث والأوامر ---
@bot.event
async def on_message(message):
    if message.author.bot: return
    
    # 1. نظام الـ Settings (المنشن)
    if "settings" in message.content.lower() and bot.user.mentioned_in(message):
        await message.reply(embed=discord.Embed(title="الإعدادات", description="اختر من القائمة:"), view=MainSettingsView())

    # 2. التشغيل (ش)
    if message.content.startswith(('ش ', 'p ')):
        song = message.content.split(' ', 1)[1]
        await message.reply(f"🎵 جاري تشغيل: {song}")

bot.run(os.environ['DISCORD_TOKEN'])
