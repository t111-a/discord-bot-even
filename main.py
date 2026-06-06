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
# ⚙️ 1. لوحة التحكم بالإعدادات المتقدمة (مثل السيرفرات الكبيرة)
# ====================================================================
# 👑 حط هنا الـ ID حَق الرتب المسموح لها تشغل الأمر (تقبل المنشن أو النسخ)
# 💡 كيف تجيب الـ ID؟ اكتب في ديسكورد كذا: \@اسم_الرتبة وبيطلع لك رقم طويل انسخه وحطه هنا.
الرتب_المسموح_لها_ID = [
    123456789012345678,  # رتبة الإدارة الأولى (كمثال، استبدله برقم رتبتك)
    987654321098765432   # رتبة المنظمين (كمثال، استبدله برقم رتبتك)
]

# 👥 إعدادات اللاعبين والوقت
الحد_الاقصى = 20       # أقصى عدد لاعبين مسموح يدخلون العجلة (مثل ما طلبت 20)
الحد_الادنى = 2        # الحد الأدنى لبدء اللعبة تلقائياً

وقت_التسجيل = 30      # كم ثانية يظل باب التسجيل مفتوح للأعضاء قبل ما يبدأ الجيم؟
وقت_التصويت = 20      # كم ثانية يعطيها البوت للمنظم عشان يطرد ضحية بالأزرار؟

# ====================================================================
# 💬 2. لوحة التحكم بالرسائل والكلام (عدل الأسلوب والطقطقة هنا)
# ====================================================================
رسالة_منع_الاعضاء = "❌ **معصي!** الفعالية هذي مخصصة فقط لأصحاب الرتب الإدارية والمنظمين. اركع! 🤫"

# 🎬 رابط الـ GIF حق العجلة اللي تلف
ROULETTE_SPIN_GIF = "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExM3Z5N2hxZzVnd3N0N3Z4cnd6dzVwZndvOHV4azN0bnd6bWhyeXFidCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/l41YtZOb9EUABnuqA/giphy.gif"

# عناوين ورسائل الجيم
عنوان_التسجيل = "🎯 نظام فعاليات الروليت الكبرى"
وصف_التسجيل = "🔥 تم فتح باب التسجيل في الروليت الحماسية!\n\n👥 **المنضمين حالياً:**"

رسالة_الالغاء = "❌ تم إلغاء الروليت لعدم دخول العدد الكافي من اللاعبين."
رسالة_بدء_التصفية = "🏁 **انتهى وقت التسجيل! بدأت تصفية العجلة الآن... قمطواااا!**"

عنوان_دوران_العجلة = "🔮 عجلة الموت تدور الحين غصب عن الكل!"
وصف_دوران_العجلة = "🎯 **اللاعبين المتبقين داخل العجلة:**\n{players_list}\n\n⏱️ **لديك {time} ثانية لاختيار لاعب لطرده من الأزرار بالأسفل 👇**"

# طرد الضحايا والفائز النهائي
رسالة_طرد_الضحية = "💥 **بـوووووم!** العجلة وقفت في نص جبهة {victim_mention} وتم إقصاءه! 💀💥"
رسالة_انتهاء_وقت_الطرد = "⏱️ **انتهى الوقت!** دارت العجلة واختارت الضحية تلقائياً."

عنوان_الفائز = "🏆 الناجي الأخير والملك الأسطوري 🏆"
وصف_الفائز = "ثبت على العجلة وطير جبهات الكل وطلع الفائز القادح اليوم:\n👑 {winner_mention} 👑\n\nألف مبرووووك الفوز باللقب والهيبة! 🎉🔥"
# ====================================================================


# 📜 أمر المساعدة المخصص (-help)
@bot.command(name="help")
async def custom_help(ctx):
    roles_text = ", ".join([f"<@&{r_id}>" for r_id = الرتب_المسموح_لها_ID])
    embed = discord.Embed(
        title="📋 لوحة إرشادات بوت الروليت الاحترافي",
        description="أهلاً بك في نظام إدارة الفعاليات المطور! إليك الأوامر المتاحة وكيفية تعديلها:",
        color=discord.Color.blue()
    )
    embed.add_field(
        name="🎮 الأوامر الحالية بالسيرفر:",
        value=(
            "`-روليت` ➔ لفتح بنل التسجيل بالأزرار (مخصص لرتب الفعاليات).\n"
            "`-help` ➔ لعرض هذه اللوحة الإرشادية الفخمة بالكامل."
        ),
        inline=False
    )
    embed.add_field(
        name="⚙️ الإعدادات الحالية للجيم:",
        value=(
            f"👥 **الحد الأقصى:** {الحد_الاقصى} لاعب.\n"
            f"⏱️ **وقت الانتظار للبدء:** {وقت_التسجيل} ثانية.\n"
            f"🔒 **الرتب المسموحة:** {roles_text if الرتب_المسموح_لها_ID else 'لم تحدد بعد'}"
        ),
        inline=False
    )
    embed.set_thumbnail(url=bot.user.display_avatar.url if bot.user.display_avatar else None)
    embed.set_footer(text="نظام احترافي مشفر ومحمي بالكامل 🚀")
    await ctx.send(embed=embed)


# 🔘 واجهة أزرار التسجيل
class RegistrationView(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=وقت_التسجيل)
        self.ctx = ctx
        self.players = [ctx.author]

    @discord.ui.button(label="الإنضمام 📥", style=discord.ButtonStyle.green)
    async def join_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user in self.players:
            return await interaction.response.send_message("❌ أنت منضم للعبة بالفعل!", ephemeral=True)
        if len(self.players) >= الحد_الاقصى:
            return await interaction.response.send_message("❌ الروليت ممتلئة بالكامل حالياً!", ephemeral=True)
            
        self.players.append(interaction.user)
        await interaction.response.send_message(f"✅ {interaction.user.mention} انضممت للروليت بنجاح!", ephemeral=True)
        
        embed = interaction.message.embeds[0]
        embed.description = f"{وصف_التسجيل} ({len(self.players)}/{الحد_الاقصى}):\n" + "\n".join([f"• {p.mention}" for p in self.players])
        await interaction.message.edit(embed=embed)

    @discord.ui.button(label="الحقيبة 💼", style=discord.ButtonStyle.blurple)
    async def bag_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🎒 حقيبتك فارغة حالياً في هذا الجيم.", ephemeral=True)

    @discord.ui.button(label="احصائيات 📊", style=discord.ButtonStyle.gray)
    async def stats_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("📈 نظام الإحصائيات متصل وجاهز!", ephemeral=True)


# 🔘 واجهة أزرار التصفية داخل الجيم
class GamePlayView(discord.ui.View):
    def __init__(self, ctx, players):
        super().__init__(timeout=وقت_التصويت)
        self.ctx = ctx
        self.players = players
        self.voted_out = None
        self.create_buttons()

    def create_buttons(self):
        # عرض أول 20 لاعب كأزرار كحد أقصى (حدود ديسكورد في الصفوف 25 زر)
        for index, player in enumerate(self.players[:20], start=1):
            button = discord.ui.Button(
                label=f"{index} {player.display_name[:15]}", 
                style=discord.ButtonStyle.secondary,
                custom_id=str(player.id)
            )
            button.callback = self.button_callback
            self.add_item(button)
            
        shuffle_btn = discord.ui.Button(label="عشوائي 🔀", style=discord.ButtonStyle.primary, custom_id="random_select")
        shuffle_btn.callback = self.button_callback
        self.add_item(shuffle_btn)

    async def button_callback(self, interaction: discord.Interaction):
        has_role = any(role.id in الرتب_المسموح_لها_ID for role in interaction.user.roles)
        if interaction.user != self.ctx.author or not has_role:
            return await interaction.response.send_message("❌ الصلاحية لمشغل الفعالية الإداري فقط لاختيار الضحية من الأزرار!", ephemeral=True)
            
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
    # 🔒 فحص الصلاحيات بالـ ID حَق الرتب
    has_role = any(role.id in الرتب_المسموح_لها_ID for role in ctx.author.roles)
    if not has_role:
        return await ctx.send(رسالة_منع_الاعضاء)

    embed = discord.Embed(
        title=عنوان_التسجيل,
        description=f"{وصف_التسجيل} (1/{الحد_الاقصى}):\n• {ctx.author.mention}",
        color=discord.Color.red()
    )
    embed.set_image(url=ROULETTE_SPIN_GIF)
    embed.set_footer(text=f"ينتهي التسجيل تلقائياً بعد {وقت_التسجيل} ثانية...")
    
    view = RegistrationView(ctx)
    main_msg = await ctx.send(embed=embed, view=view)
    
    await asyncio.sleep(وقت_التسجيل)
    view.stop()
    
    players = view.players
    
    if len(players) < الحد_الادنى:
        return await ctx.send(رسالة_الالغاء)

    await ctx.send(رسالة_بدء_التصفية)
    await asyncio.sleep(2)

    while len(players) > 1:
        p_list = ", ".join([p.mention for p in players])
        game_embed = discord.Embed(
            title=عنوان_دوران_العجلة,
            description=وصف_دوران_العجلة.format(players_list=p_list, time=وقت_التصويت),
            color=discord.Color.blue()
        )
        game_embed.set_image(url=ROULETTE_SPIN_GIF)
        
        game_view = GamePlayView(ctx, players)
        game_msg = await ctx.send(embed=game_embed, view=game_view)
        
        await asyncio.sleep(وقت_التصويت)
        game_view.stop()
        
        if not game_view.voted_out:
            victim = random.choice(players)
            await ctx.send(رسالة_انتهاء_وقت_الطرد)
        else:
            victim = game_view.voted_out
            
        players.remove(victim)
        await ctx.send(رسالة_طرد_الضحية.format(victim_mention=victim.mention))
        await asyncio.sleep(3)
        
    winner = players[0]
    winner_embed = discord.Embed(
        title=عنوان_الفائز,
        description=وصف_الفائز.format(winner_mention=winner.mention),
        color=discord.Color.gold()
    )
    winner_embed.set_thumbnail(url=winner.display_avatar.url)
    await ctx.send(embed=winner_embed)

bot.run(os.getenv("DISCORD_TOKEN"))
