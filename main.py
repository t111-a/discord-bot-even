import discord
from discord.ext import commands
import os

# 1. إعدادات الصلاحيات (Intents) لضمان قراءة الرسائل وتفعيل الأوامر
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True

# 2. بناء البوت مع تحديد علامة البداية "-" وإلغاء أمر help التلقائي لمنع الكراش
bot = commands.Bot(command_prefix="-", intents=intents, help_command=None)

# 3. حدث التشغيل الأول: طباعة رسالة في الكونسول عند عمل البوت بنجاح
@bot.event
async def on_ready():
    print(f"✅ تم تشغيل البوت بنجاح باسم: {bot.user}")
    print("جرب اكتب -help في الديسكورد.")

# ====================================================================
# 🎡 واجهة القائمة التفاعلية لأمر الـ Help (Select Menu)
# ====================================================================
class SettingsSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="🎡 Roulette Setup", description="إعداد الرومات وخلفية العجلة", emoji=discord.PartialEmoji(name="🎡")),
            discord.SelectOption(label="⚔️ Game Mechanics", description="التحكم في القوانين والخصائص التكتيكية", emoji=discord.PartialEmoji(name="⚔️")),
            discord.SelectOption(label="📶 System & Ping", description="فحص سرعة استجابة البوت (البنك)", emoji=discord.PartialEmoji(name="📶"))
        ]
        super().__init__(placeholder="🎡 Select a category to configure...", options=options)

    async def callback(self, interaction: discord.Interaction):
        # 🎡 قسم إعدادات الروليت
        if self.values[0] == "Roulette Setup":
            embed = discord.Embed(title="🎡 Roulette Setup & Configuration", color=discord.Color.blue())
            embed.description = (
                "**-روم_الاعدادات**\n*🔐 لتثبيت روم الإدارة الحالية (للبرمجة بخصوصية).*\n\n"
                "**-رومات #channel**\n*📢 لتحديد رومات اللعب العامة (المنشن للشات اللي بيلعبون فيه).*\n\n"
                "**-خلفية [URL]**\n*🖼️ لتغيير مظهر العجلة بصورة متحركة من رابط.*"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        # ⚔️ قسم قوانين اللعبة والخصائص
        elif self.values[0] == "Game Mechanics":
            embed = discord.Embed(title="⚔️ Advanced Game Mechanics", color=discord.Color.green())
            embed.description = (
                "**-خصائص [on/off]**\n*🎭 لتفعيل أو تعطيل المهارات التكتيكية (الحماية/الارتداد).*\n\n"
                "**-احتمال [1-100]**\n*🛡️ لتعديل نسبة حظ تفعيل المهارات الدفاعية.*\n\n"
                "**-قنبلة [on/off]**\n*💣 لتفعيل أو حظر خيار طرد عضوين معاً.*"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

        # 📶 قسم النظام والبنك
        elif self.values[0] == "System & Ping":
            embed = discord.Embed(title="📶 System Status & Latency", color=discord.Color.dark_gray())
            embed.description = (
                "**-بنك**\n*📡 لقياس وفحص سرعة اتصال البوت الحالية.*\n\n"
                "**-نسخ [نوع] [نص]**\n*📝 لإعادة صياغة رسائل الإقصاء التلقائي.*"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

class HelpView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(SettingsSelect())

# ====================================================================
# ⚙️ الأوامر الرئيسية للبوت
# ====================================================================

# أمر الـ help المنسق والمحمي من الكراش
@bot.command(name="help")
async def custom_help(ctx):
    embed = discord.Embed(
        title="🤖 Roulette Pro Control Panel",
        description="Welcome to the advanced control panel. Please choose a category from the menu below to view setup details and commands.",
        color=discord.Color.from_rgb(47, 49, 54) # لون الدارك متاح تلقائياً
    )
    embed.set_footer(text="Developed for Horizon RP [7K] | Powered by Railway")
    await ctx.send(embed=embed, view=HelpView())

# أمر البنك (رسالة عادية سريعة)
@bot.command(name="بنك")
async def ping_command(ctx):
    # قياس سرعة الاتصال بالملي ثانية
    start_time = time.monotonic()
    msg = await ctx.send("جاري فحص سرعة الاستجابة...")
    end_time = time.monotonic()
    latency = round((end_time - start_time) * 1000)
    bot_ping = round(bot.latency * 1000)
    
    # تنسيق رسالة البنك بسيطة وجميلة
    await msg.edit(content=f"📡 سرعة النظام: **{bot_ping}ms** | ⚡ سرعة الشات: **{latency}ms**")

# ====================================================================
# 🛡️ تشغيل البوت (أمان التوكن من الـ Environment Variables)
# ====================================================================
# هذا السطر يسحب التوكن من Variables في Railway لضمان أمانه.
bot.run(os.getenv("DISCORD_TOKEN"))
