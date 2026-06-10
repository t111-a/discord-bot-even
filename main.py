import discord
from discord.ext import commands
import asyncio
import random

# هذا الكود يوضع داخل ملف main.py الخاص بك

class RouletteView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.players = []

    @discord.ui.button(label="دخول الجولة", style=discord.ButtonStyle.success, custom_id="join_roulette")
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user not in self.players:
            self.players.append(interaction.user)
            await interaction.response.send_message(f"✅ {interaction.user.mention} انضم للجولة! (العدد: {len(self.players)})", ephemeral=False)
        else:
            await interaction.response.send_message("⚠️ أنت موجود بالفعل!", ephemeral=True)

@bot.command()
async def روليت(ctx):
    view = RouletteView()
    embed = discord.Embed(
        title="🎡 روليت - روسي احترافي",
        description="اضغط على 'دخول الجولة' للانضمام.\nستبدأ اللعبة بعد 30 ثانية!",
        color=discord.Color.red()
    )
    msg = await ctx.send(embed=embed, view=view)
    
    # انتظار 30 ثانية لدخول اللاعبين
    await asyncio.sleep(30)
    
    if len(view.players) < 2:
        await ctx.send("❌ تم إلغاء الجولة لعدم اكتمال العدد.")
    else:
        winner = random.choice(view.players)
        await ctx.send(f"🎡 **انتهت الجولة!** الفائز هو: **{winner.mention}** 🎉")
