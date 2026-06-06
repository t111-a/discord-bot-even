import discord
from discord.ext import commands
import random
import asyncio
import os

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="-", intents=discord.Intents.all(), help_command=None)
    
    async def setup_hook(self):
        await self.tree.sync()

bot = MyBot()

# ====================================================================
# ⚙️ لوحة التحكم بالأعداد والعدادات (تعدلها من هنا براحتك بالأرقام)
# ====================================================================
وقت_التسجيل = 20      # كم ثانية يظل زر "الانضمام" شغال للأعضاء؟
الحد_الاقصى = 8        # أقصى عدد لاعبين يظهرون في عجلة الروليت
الحد_الادنى = 2        # أقل عدد لاعبين مطلوب عشان تبدأ اللعبة ولا تلتغي
# ====================================================================

# رابط صورة العجلة بالمنتصف (تقدر تغير الرابط بصورتك لو تبي)
ROULETTE_WHEEL_URL = "https://i.imgur.com/vH9Z6hZ.png" 

# 🔘 1. واجهة أزرار التسجيل (نفس شكل بوت Real)
class RegistrationView(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=وقت_التسجيل)
        self.ctx = ctx
        self.players = [ctx.author] # منشئ الجيم ينضم تلقائياً

    @discord.ui.button(label="الإنضمام 📥", style=discord.ButtonStyle.green)
    async def join_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user in self.players:
            return await interaction.response.send_message("❌ أنت منضم للعبة بالفعل!", ephemeral=True)
        if len(self.players) >= الحد_الاقصى:
            return await interaction.response.send_message("❌ الروليت ممتلئة بالكامل حالياً!", ephemeral=True)
            
        self.players.append(interaction.user)
        await interaction.response.send_message(f"✅ {interaction.user.mention} انضممت للروليت بنجاح!", ephemeral=True)
        
        # تحديث الرسالة لعرض اللاعبين المنضمين فوراً
        embed = interaction.message.embeds[0]
        embed.description = f"🔥 تم فتح باب التسجيل في الروليت!\n\n👥 **المنضمين حالياً ({len(self.players)}/{الحد_الاقصى}):**\n" + "\n".join([f"• {p.mention}" for p in self.players])
        await interaction.message.edit(embed=embed)

    @discord.ui.button(label="الحقيبة 💼", style=discord.ButtonStyle.blurple)
    async def bag_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🎒 حقيبتك فارغة حالياً في هذا الجيم.", ephemeral=True)

    @discord.ui.button(label="احصائيات 📊", style=discord.ButtonStyle.gray)
    async def stats_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("📈 نظام الإحصائيات جاهز ومتصل!", ephemeral=True)


# 🔘 2. واجهة أزرار التصفية داخل الجيم (نفس شكل بوت Veon)
class GamePlayView(discord.ui.View):
    def __init__(self, ctx, players):
        super().__init__(timeout=20.0)
        self.ctx = ctx
        self.players = players
        self.voted_out = None
        self.create_buttons()

    def create_buttons(self):
        # إنشاء زر لكل لاعب مسجل باللعبة (نفس الأزرار المرقمة)
        for index, player in enumerate(self.players, start=1):
            button = discord.ui.Button(
                label=f"{index} {player.display_name}", 
                style=discord.ButtonStyle.secondary,
                custom_id=str(player.id)
            )
            button.callback = self.button_callback
            self.add_item(button)
            
        # زر الاختيار العشوائي
        shuffle_btn = discord.ui.Button(label="عشوائي 🔀", style=discord.ButtonStyle.primary, custom_id="random_select")
        shuffle_btn.callback = self.button_callback
        self.add_item(shuffle_btn)

    async def button_callback(self, interaction: discord.Interaction):
        if interaction.user != self.ctx.author:
            return await interaction.response.send_message("❌ الصلاحية لصاحب الفعالية فقط لاختيار الضحية من الأزرار!", ephemeral=True)
            
        custom_id = interaction.data['custom_id']
        if custom_id == "random_select":
            self.voted_out = random.choice(self.players)
        else:
            player_id = int(custom_id)
            self.voted_out = next((p for p in self.players if p.id == player_id), None)
            
        self.stop()


# ==================== 🎮 الأمر الأساسي المطور ====================

@bot.command(name="روليت")
async def start_roulette(ctx):
    # إرسال بنل التسجيل بالأزرار (نفس Real)
    embed = discord.Embed(
        title="🎮 نظام فعاليات الروليت الكبرى",
        description=f"🔥 تم فتح باب التسجيل في الروليت!\n\n👥 **المنضمين حالياً (1/{الحد_الاقصى}):**\n• {ctx.author.mention}",
        color=discord.Color.dark_grey()
    )
    embed.set_image(url=ROULETTE_WHEEL_URL)
    embed.set_footer(text=f"ينتهي التسجيل تلقائياً بعد {وقت_التسجيل} ثانية...")
    
    view = RegistrationView(ctx)
    main_msg = await ctx.send(embed=embed, view=view)
    
    # انتظار وقت التسجيل ينتهي
    await asyncio.sleep(وقت_التسجيل)
    view.stop()
    
    players = view.players
    
    # إذا ما دخل أحد يتلغى القيم تلقائياً
    if len(players) < الحد_الادنى:
        return await ctx.send(f"❌ تم إلغاء الروليت لعدم دخول العدد الكافي من اللاعبين (المطلوب {الحد_الادنى} على الأقل).")

    await ctx.send("🏁 **انتهى وقت التسجيل! بدأت تصفية العجلة الآن...**")
    await asyncio.sleep(2)

    # مرحلة أزرار التصفية لكل جولة (نفس Veon)
    while len(players) > 1:
        game_embed = discord.Embed(
            title="🔮 عجلة الروليت تدور الآن!",
            description=f"🎯 **اللاعبين داخل العجلة:**\n" + ", ".join([p.mention for p in players]) + f"\n\n⏱️ **لديك 20 ثانية لاختيار لاعب لطرده من الأزرار بالأسفل 👇**",
            color=discord.Color.blue()
        )
        game_embed.set_image(url=ROULETTE_WHEEL_URL)
        
        game_view = GamePlayView(ctx, players)
        game_msg = await ctx.send(embed=game_embed, view=game_view)
        
        await asyncio.sleep(20)
        game_view.stop()
        
        if not game_view.voted_out:
            victim = random.choice(players)
            await ctx.send(f"⏱️ **انتهى الوقت!** تم اختيار الضحية عشوائياً.")
        else:
            victim = game_view.voted_out
            
        players.remove(victim)
        await ctx.send(f"💥 **بـوووووم!** طارت الجبهة وتم إقصاء {victim.mention} من العجلة! 💀💥")
        await asyncio.sleep(3)
        
    # إعلان الناجي الأخير
    winner = players[0]
    winner_embed = discord.Embed(
        title="🏆 نهاية الروليت الأسطورية 🏆",
        description=f"الناجي الأخير والوحش القادح اللي ثبت على العجلة هو:\n👑 {winner.mention} 👑\n\nألف مبرووووك الفوز! 🎉🔥",
        color=discord.Color.gold()
    )
    winner_embed.set_thumbnail(url=winner.display_avatar.url)
    await ctx.send(embed=winner_embed)

bot.run(os.getenv("DISCORD_TOKEN"))
