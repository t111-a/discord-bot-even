import discord
import asyncio
import os
from discord.ext import commands

OWNER_ID = 1327923220329926677
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="", intents=bot_intents)

# --- دالة التحقق الذكي (البوت + المستخدم في نفس الروم) ---
async def check_voice(interaction_or_message):
    if isinstance(interaction_or_message, discord.Message):
        user_vc = interaction_or_message.author.voice
        bot_vc = interaction_or_message.guild.voice_client
    else:
        user_vc = interaction_or_message.user.voice
        bot_vc = interaction_or_message.guild.voice_client

    if not user_vc: return False, "❌ لازم تدخل روم صوتي أولاً!"
    if bot_vc and user_vc.channel != bot_vc.channel: return False, "❌ لازم تكون معي في نفس الروم!"
    return True, user_vc.channel

# --- القائمة الرئيسية مع الأزرار الثلاثة (صف واحد) ---
class MainSettingsView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    
    @discord.ui.select(placeholder="قائمة التحكم", options=[
        discord.SelectOption(label="إعدادات البوت", value="bot"),
        discord.SelectOption(label="إعدادات عامة", value="general"),
        discord.SelectOption(label="إعدادات أخرى", description="تفعيل / تعطيل الثمنيل في الردود", value="other")
    ])
    async def select(self, i: discord.Interaction, s: discord.ui.Select):
        # ... (نفس منطق الانتقال للقوائم)
        pass

    @discord.ui.button(label="إعادة تشغيل", style=discord.ButtonStyle.secondary, row=1)
    async def restart(self, i, b): await i.response.send_message("🔄 جاري إعادة التشغيل...", ephemeral=True)
    
    @discord.ui.button(label="إلغاء تثبيت", style=discord.ButtonStyle.secondary, row=1)
    async def unpin(self, i, b): 
        if i.guild.voice_client: await i.guild.voice_client.disconnect()
        await i.response.send_message("🚫 تم إلغاء التثبيت", ephemeral=True)
    
    @discord.ui.button(label="تثبيت البوت", style=discord.ButtonStyle.secondary, row=1)
    async def pin(self, i, b):
        can_use, channel = await check_voice(i)
        if not can_use: await i.response.send_message(channel, ephemeral=True); return
        await channel.connect(self_deaf=True)
        await i.response.send_message("✅ تم تثبيت البوت معك في الروم", ephemeral=True)

# --- نظام التشغيل (مع الشرط الجديد) ---
@bot.event
async def on_message(message):
    if message.author.bot: return
    
    if message.content.startswith(('ش ', 'p ')):
        can_use, result = await check_voice(message)
        if not can_use: await message.reply(result); return
        
        # إذا البوت مو في الروم، يدخل تلقائياً مع المستخدم
        if not message.guild.voice_client:
            await result.connect(self_deaf=True)
            
        song = message.content.split(' ', 1)[1]
        await message.reply(embed=get_embed("يشتغل الحين:", song), view=MusicControls())
