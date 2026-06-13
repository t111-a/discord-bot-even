import discord
import asyncio
import os
from discord.ext import commands

bot = commands.Bot(command_prefix="", intents=discord.Intents.all())

# دالة لتصميم الـ Embed الرسمي (بدون إيموجيات وزوايا مرتبة)
def create_embed(title, description):
    embed = discord.Embed(title=title, description=description, color=0x2b2d31)
    embed.set_footer(text="نظام الإدارة المطور")
    return embed

# --- القوائم ---
class MainSettingsView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    
    @discord.ui.select(placeholder="قائمة الإعدادات الرئيسية", options=[
        discord.SelectOption(label="إعدادات البوت", value="bot"),
        discord.SelectOption(label="إعدادات الإدارة", value="admin"),
        discord.SelectOption(label="إعدادات عامة", value="general")
    ])
    async def select(self, interaction: discord.Interaction, select: discord.ui.Select):
        if select.values[0] == "bot":
            await interaction.response.edit_message(embed=create_embed("إعدادات البوت", "تحكم بخصائص البوت"), view=BotSettingsView())
        elif select.values[0] == "admin":
            await interaction.response.edit_message(embed=create_embed("إعدادات الإدارة", "إضافة مسؤولين أو حظرهم"), view=AdminSettingsView())
        elif select.values[0] == "general":
            await interaction.response.edit_message(embed=create_embed("إعدادات عامة", "تعديلات النظام العامة"), view=GeneralSettingsView())

# --- إعدادات البوت مع زر التثبيت المرتب ---
class BotSettingsView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)

    @discord.ui.button(label="تثبيت البوت في الروم", style=discord.ButtonStyle.success)
    async def pin(self, interaction, button):
        if interaction.user.voice:
            await interaction.user.voice.channel.connect()
            await interaction.response.send_message("✅ تم التثبيت في الروم", ephemeral=True)
        else:
            await interaction.response.send_message("❌ يجب دخول الروم أولاً", ephemeral=True)
            
    @discord.ui.button(label="رجوع", style=discord.ButtonStyle.secondary)
    async def back(self, interaction, button):
        await interaction.response.edit_message(embed=create_embed("القائمة الرئيسية", "اختر ما تريد"), view=MainSettingsView())

# --- لوحة التحكم بالموسيقى (التصميم الاحترافي) ---
class MusicControls(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    
    @discord.ui.button(label="إيقاف مؤقت", style=discord.ButtonStyle.primary)
    async def pause(self, i, b): await i.response.send_message("⏸️ تم الإيقاف", ephemeral=True)
    
    @discord.ui.button(label="إنهاء", style=discord.ButtonStyle.danger)
    async def stop(self, i, b): await i.message.delete()

# --- تفعيل الأوامر ---
@bot.event
async def on_message(message):
    if message.author.bot: return
    
    if "settings" in message.content.lower() and bot.user.mentioned_in(message):
        await message.reply(embed=create_embed("لوحة التحكم", "اختر القسم المطلوب"), view=MainSettingsView())
    
    if message.content.startswith(('ش ', 'p ')):
        song = message.content.split(' ', 1)[1]
        embed = discord.Embed(title="🎶 جاري التشغيل الآن", description=f"الأغنية: **{song}**", color=0x2b2d31)
        await message.reply(embed=embed, view=MusicControls())

bot.run(os.environ['DISCORD_TOKEN'])
