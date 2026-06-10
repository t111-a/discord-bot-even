import discord
from discord.ext import commands
import random
import asyncio
import os

# إعدادات البوت
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="-", intents=intents, help_command=None)

# 1. القائمة التفاعلية للألعاب
class MainView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🎡 روليت", style=discord.ButtonStyle.primary, custom_id="roulette_btn")
    async def roulette_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🎡 **جاري بدء جولة الروليت... اكتب `-روليت` في الشات للبدء!**", ephemeral=False)

    @discord.ui.button(label="🎒 الحقيبة", style=discord.ButtonStyle.secondary, custom_id="bag_btn")
    async def bag_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🎒 **حقيبتك:** لا توجد خصائص حالياً.", ephemeral=True)

    @discord.ui.button(label="📊 الإحصائيات", style=discord.ButtonStyle.success, custom_id="stats_btn")
    async def stats_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("📊 **إحصائياتك:** فوز: 0 | خسارة: 0 | نقاط: 100", ephemeral=True)

# 2. أمر الألعاب (القائمة الشاملة)
@bot.command()
async def ألعاب(ctx):
    embed = discord.Embed(title="🎮 قائمة الأوامر الاحترافية", description="اختر ما تريد من القائمة أدناه:", color=discord.Color.dark_purple())
    embed.add_field(name="الألعاب الجماعية", value="روليت، هايد، لغم، مافيا، نرد، كراسي", inline=False)
    embed.add_field(name="الألعاب الفردية", value="اسرع، فكك، عكس، حساب، جماد", inline=False)
    await ctx.send(embed=embed)

# 3. نظام الروليت الاحترافي
class RouletteGameView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.players = []

    @discord.ui.button(label="دخول الجولة", style=discord.ButtonStyle.danger, custom_id="join_game")
    async def join_game(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user not in self.players:
            self.players.append(interaction.user)
            await interaction.response.send_message(f"✅ {interaction.user.name} انضم للجولة!", ephemeral=False)
        else:
            await interaction.response.send_message("⚠️ أنت مشترك بالفعل!", ephemeral=True)

@bot.command()
async def روليت(ctx):
    view = RouletteGameView()
    embed = discord.Embed(title="🎡 جولة الروليت", description="الانتظار لمدة 20 ثانية لدخول اللاعبين...", color=discord.Color.red())
    msg = await ctx.send(embed=embed, view=view)
    await asyncio.sleep(20)
    if len(view.players) < 1:
        await ctx.send("❌ تم إلغاء الجولة لعدم وجود لاعبين.")
    else:
        winner = random.choice(view.players)
        await ctx.send(f"🎉 **الفائز في الروليت هو:** {winner.mention}!")

# 4. أمر الـ Setup (اللوحة)
@bot.command()
@commands.has_permissions(administrator=True)
async def setup(ctx):
    embed = discord.Embed(title="🎮 مركز الألعاب والتحكم", description="أهلاً بك، اختر اللعبة أو تفقد حقيبتك من الأزرار:", color=discord.Color.blue())
    await ctx.send(embed=embed, view=MainView())

# تشغيل البوت
if __name__ == "__main__":
    bot.run(os.environ["DISCORD_TOKEN"])
