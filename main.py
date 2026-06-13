import discord
from discord.ext import commands

bot = commands.Bot(command_prefix="", intents=discord.Intents.all())

class MusicView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    # القائمة (Select Menu)
    @discord.ui.select(placeholder="اختر خياراً...", options=[
        discord.SelectOption(label="تثبيت الأغنية", value="pin"),
        discord.SelectOption(label="إلغاء التشغيل", value="stop"),
        discord.SelectOption(label="تحديث", value="refresh"),
        discord.SelectOption(label="إعادة تعيين", value="reset")
    ])
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        await interaction.response.send_message(f"تم اختيار: {select.values[0]}", ephemeral=True)

    # الأزرار (Buttons) تحت القائمة
    @discord.ui.button(label="رجوع", style=discord.ButtonStyle.danger)
    async def back_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("تم الرجوع.", ephemeral=True)

@bot.event
async def on_message(message):
    if message.author.bot: return
    
    # أوامر البوت (بدون بادئة)
    content = message.content.lower()
    
    # 1. التشغيل (ش أو p)
    if content.startswith(('ش ', 'p ')):
        song = content.split(' ', 1)[1]
        await message.channel.send(f"🎵 جاري تشغيل: {song}")
        
    # 2. الوقف
    if content == "وقف":
        if message.guild.voice_client:
            await message.guild.voice_client.disconnect()
            await message.channel.send("🛑 تم الإيقاف.")

    # 3. الـ Settings (بالمنشن)
    if "settings" in content and bot.user.mentioned_in(message):
        embed = discord.Embed(
            title="الإعدادات والمشغل",
            description="اختر إعداداً من القائمة أو استخدم الأزرار السريعة.",
            color=0x2f3136
        )
        await message.channel.send(embed=embed, view=MusicView())

    # 4. الـ Help
    if content == "help":
        await message.channel.send("الأوامر: \nش [اسم الأغنية] \np [اسم الأغنية] \nوقف \n@البوت settings")

bot.run('')
