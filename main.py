import discord
from discord.ext import commands

# إعدادات البوت (تأكد من تفعيل Message Content في الديفلوبر بورتال)
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="-", intents=intents)

# القائمة التفاعلية للاعدادات
class SettingsSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Roulette Setup", description="تعديل إعدادات عجلة الروليت", emoji="🎡"),
            discord.SelectOption(label="Game Mechanics", description="التحكم في قوانين اللعبة والخصائص", emoji="⚔️"),
            discord.SelectOption(label="System & Ping", description="فحص سرعة استجابة البوت", emoji="📶")
        ]
        super().__init__(placeholder="Select a category to configure...", options=options)

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "Roulette Setup":
            embed = discord.Embed(title="🎡 Roulette Setup", color=discord.Color.blue())
            embed.description = (
                "**-روم_الاعدادات**\n*تحديد الروم المخصصة لإدارة إعدادات البوت.*\n\n"
                "**-رومات #channel**\n*تحديد الروم التي سيتم اللعب فيها.*\n\n"
                "**-خلفية [URL]**\n*تغيير خلفية العجلة بصورة من رابط.*"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        elif self.values[0] == "Game Mechanics":
            embed = discord.Embed(title="⚔️ Game Mechanics", color=discord.Color.green())
            embed.description = (
                "**-خصائص [on/off]**\n*تفعيل أو تعطيل المهارات (حماية/ارتداد).*\n\n"
                "**-احتمال [1-100]**\n*نسبة نجاح المهارات الدفاعية.*\n\n"
                "**-قنبلة [on/off]**\n*تفعيل زر القنبلة لطرد عضوين.*"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

class HelpView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(SettingsSelect())

# أمر الـ Help الرئيسي
@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="Roulette Pro Control Panel",
        description="Welcome to the advanced control panel. Choose a category from the menu below to view setup details.",
        color=discord.Color.dark_gray()
    )
    await ctx.send(embed=embed, view=HelpView())

# أمر البنك (رسالة عادية)
@bot.command()
async def ping(ctx):
    await ctx.send(f"🏓 Pong! Bot Latency: {round(bot.latency * 1000)}ms")

bot.run("")
