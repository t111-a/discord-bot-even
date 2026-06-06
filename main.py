import discord
from discord.ext import commands
import random
import asyncio
import os

class MyBot(commands.Bot):
    def __init__(self):
        # هنا خليت الاختصار هو علامة الناقص -
        super().__init__(command_prefix="-", intents=discord.Intents.all())
    
    async def setup_hook(self):
        await self.tree.sync()

bot = MyBot()

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    print("البوت شغال الحين بعلامة الناقص (-) وجاهز للعب!")

# ==================== أمر الروليت السريع المباشر ====================

@bot.command(name="روليت")
async def quick_roulette(ctx):
    # 1. يجيب كل الأعضاء المتفاعلين أو اللي أونلاين في الروم حالياً عشان ما يختار بوتات أو ناس أوفلاين
    all_members = [m for m in ctx.channel.members if not m.bot]
    
    if len(all_members) < 2:
        return await ctx.send("❌ يبي لها فزعة! لازم يكون فيه شخصين على الأقل في الروم عشان تدور الروليت.")
    
    # 2. يرسل رسالة حماسية إن الروليت بدأت
    msg = await ctx.send("🔄 **الروليت جالس تدور الحين بين الموجودين بالروم... قمطواااا!** 🎯")
    await asyncio.sleep(2)
    
    # التأثير البصري للدوران
    await msg.edit(content="🔮 *جاري سحب الضحية...*")
    await asyncio.sleep(2)
    
    # 3. يختار شخص عشوائي تماماً من الروم
    loser = random.choice(all_members)
    
    # 4. يعلن النتيجة في الشات بـ إمبيد فخم
    embed = discord.Embed(
        title="💥 بـوووووم! طارت الجبهة 💥",
        description=f"الروليت وقفت وجت في نص جبهة:\n👑 {loser.mention} 👑\n\nتعيش وتاكل غيرها يا وحش! 💀😂",
        color=discord.Color.red()
    )
    embed.set_thumbnail(url=loser.display_avatar.url)
    
    await ctx.send(embed=embed)

bot.run(os.getenv("DISCORD_TOKEN"))
