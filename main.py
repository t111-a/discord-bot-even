import discord
from discord.ext import commands
import random
import asyncio
import os
import re

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="-", intents=discord.Intents.all(), help_command=None)
    
    async def setup_hook(self):
        await self.tree.sync()

bot = MyBot()

# ====================================================================
# 💾 الذاكرة التخزينية الافتراضية للبوت
# ====================================================================
roulette_config = {
    "max_players": 20,
    "signup_time": 30,
    "bg_url": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExM3Z5N2hxZzVnd3N0N3Z4cnd6dzVwZndvOHV4azN0bnd6bWhyeXFidCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/l41YtZOb9EUABnuqA/giphy.gif",
    "embed_color": discord.Color.red()
}

COLORS_MAP = {
    "red": discord.Color.red(), "blue": discord.Color.blue(), "green": discord.Color.green(),
    "gold": discord.Color.gold(), "purple": discord.Color.purple(), "black": discord.Color.dark_embed(),
    "احمر": discord.Color.red(), "ازرق": discord.Color.blue(), "اخضر": discord.Color.green(),
    "ذهبي": discord.Color.gold(), "بنفسجي": discord.Color.purple()
}

رسالة_منع_الاعضاء = "❌ **معصي!** الفعالية هذي مخصصة فقط لأصحاب الرتبة المحددة للعبة. 🤫"
رسالة_الالغاء = "❌ تم إلغاء الروليت لعدم دخول العدد الكافي من اللاعبين."
رسالة_بدء_التصفية = "🏁 **انتهى وقت التسجيل! بدأت تصفية العجلة الآن... قمطواااا!**"

# دالة ذكية لتنظيف الوقت وفهم الأرقام لو العضو كتب حرف s أو ثانية
def parse_time_input(user_input: str):
    clean_input = re.sub(r'[^\d]', '', user_input) # يستخرج الأرقام فقط ويمسح الحروف مثل s
    if clean_input.isdigit():
        return int(clean_input)
    return None

# ====================================================================
# 🛠️ أوامر التحكم التفاعلية الذكية (تسألك وأنت تجاوبها)
# ====================================================================

@bot.command(name="وقت")
@commands.has_permissions(administrator=True)
async def set_signup_time(ctx):
    await ctx.send("⏱️ **كم ثانية تبي وقت انتظار التسجيل للروليت؟** (مثال: `20s` أو `30`)")
    
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        msg = await bot.wait_for('message', check=check, timeout=30.0)
        seconds = parse_time_input(msg.content)
        if seconds is None or seconds <= 0:
            return await ctx.send("❌ القيمة غير صحيحة، يرجى كتابة أرقام فقط!")
        
        roulette_config["signup_time"] = seconds
        await ctx.send(f"✅ تم تعديل وقت انتظار بدء الروليت إلى: **{seconds} ثانية** بنجاح!")
    except asyncio.TimeoutError:
        await ctx.send("⏱️ انتهى وقت الاستجابة، يرجى كتابة الأمر من جديد.")

@bot.command(name="عدد")
@commands.has_permissions(administrator=True)
async def set_max_players(ctx):
    await ctx.send("👥 **كم الحد الأقصى للاعبين اللي تبيهم يدخلون العجلة؟** (اكتب الرقم في الشات)")
    
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        msg = await bot.wait_for('message', check=check, timeout=30.0)
        num = parse_time_input(msg.content)
        if num is None or num <= 1:
            return await ctx.send("❌ القيمة غير صحيحة، يرجى إدخال رقم لاعبين أكبر من 1!")
        
        roulette_config["max_players"] = num
        await ctx.send(f"✅ تم تعديل حد اللاعبين الأقصى إلى: **{num} لاعب** بنجاح!")
    except asyncio.TimeoutError:
        await ctx.send("⏱️ انتهى وقت الاستجابة، يرجى كتابة الأمر من جديد.")

@bot.command(name="خلفية")
@commands.has_permissions(administrator=True)
async def set_background(ctx):
    await ctx.send("🖼️ **أرسل رابط الـ GIF أو الصورة اللي تبيها كخلفية للعجلة الحين:**")
    
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        msg = await bot.wait_for('message', check=check, timeout=45.0)
        url = msg.content.strip()
        if not url.startswith("http"):
            return await ctx.send("❌ الرابط غير صحيح! تأكد من إرسال رابط يبدأ بـ http")
            
        roulette_config["bg_url"] = url
        await ctx.send("✅ تم تغيير خلفية العجلة المتحركة بنجاح!")
    except asyncio.TimeoutError:
        await ctx.send("⏱️ انتهى وقت الاستجابة، يرجى كتابة الأمر من جديد.")

@bot.command(name="لون")
@commands.has_permissions(administrator=True)
async def set_color(ctx):
    await ctx.send("🎨 **وش اللون اللي تبيه للإمبيد؟**\nالألوان المتوفرة: (احمر، ازرق، اخضر، ذهبي، بنفسجي، red, blue, gold)")
    
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        msg = await bot.wait_for('message', check=check, timeout=30.0)
        color_name = msg.content.strip().lower()
        if color_name in COLORS_MAP:
            roulette_config["embed_color"] = COLORS_MAP[color_name]
            await ctx.send(f"✅ تم تغيير لون إمبيدات الروليت إلى: **{color_name}**")
        else:
            await ctx.send("❌ اللون غير مدعوم! جرب كتابة ألوان أساسية مثل 'احمر' أو 'blue'.")
    except asyncio.TimeoutError:
        await ctx.send("⏱️ انتهى وقت الاستجابة.")


# 📜 أمر المساعدة لعرض الإعدادات الحالية
@bot.command(name="help")
async def custom_help(ctx):
    embed = discord.Embed(
        title="📋 دليل إعدادات بوت الروليت التفاعلي",
        description="البوت صار يسألك وأنت تجاوب عليه بالشات مباشرة! هذي هي الأوامر الحالية:",
        color=roulette_config["embed_color"]
    )
    embed.add_field(
        name="⚙️ أوامر التعديل التفاعلية (للإدارة):",
        value=(
            "`-وقت` ➔ البوت بيطلب منك تحديد وقت التسجيل (يدعم كتابة `20s`).\n"
            "`-عدد` ➔ البوت بيطلب منك إدخال حد اللاعبين الأقصى.\n"
            "`-خلفية` ➔ البوت بيطلب منك رابط الصورة أو الـ GIF الجديد.\n"
            "`-لون` ➔ البوت بيطلب منك اختيار لون ثيم اللعبة."
        ),
        inline=False
    )
    embed.add_field(
        name="🎮 أمر التشغيل الأساسي للفعالية:",
        value="`-روليت @منشن_الرتبة` ➔ لفتح التسجيل للرتبة المحددة للعب.",
        inline=False
    )
    embed.add_field(
        name="📊 الإعدادات الحالية المحفوظة بالبُلُّك:",
        value=(
            f"👥 **الحد الأقصى الحالي:** {roulette_config['max_players']} لاعب.\n"
            f"⏱️ **وقت الانتظار الحالي:** {roulette_config['signup_time']} ثانية.\n"
            f"🖼️ **الخلفية المعتمدة الحالية:** [اضغط هنا لرؤية الرابط الحالي]({roulette_config['bg_url']})"
        ),
        inline=False
    )
    embed.set_image(url=roulette_config["bg_url"])
    embed.set_footer(text="تم التطوير بأعلى تقنية تفاعلية 🚀")
    await ctx.send(embed=embed)


# 🔘 واجهة أزرار التسجيل
class RegistrationView(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=roulette_config["signup_time"])
        self.ctx = ctx
        self.players = [ctx.author]

    @discord.ui.button(label="الإنضمام 📥", style=discord.ButtonStyle.green)
    async def join_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user in self.players:
            return await interaction.response.send_message("❌ أنت منضم للعبة بالفعل!", ephemeral=True)
        if len(self.players) >= roulette_config["max_players"]:
            return await interaction.response.send_message("❌ الروليت ممتلئة بالكامل حالياً!", ephemeral=True)
            
        self.players.append(interaction.user)
        await interaction.response.send_message(f"✅ {interaction.user.mention} انضممت للروليت بنجاح!", ephemeral=True)
        
        embed = interaction.message.embeds[0]
        embed.description = f"🔥 تم فتح باب التسجيل في الروليت الحماسية!\n\n👥 **المنضمين حالياً ({len(self.players)}/{roulette_config['max_players']}):**\n" + "\n".join([f"• {p.mention}" for p in self.players])
        await interaction.message.edit(embed=embed)

    @discord.ui.button(label="الحقيبة 💼", style=discord.ButtonStyle.blurple)
    async def bag_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🎒 حقيبتك فارغة حالياً في هذا الجيم.", ephemeral=True)

    @discord.ui.button(label="احصائيات 📊", style=discord.ButtonStyle.gray)
    async def stats_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("📈 نظام الإحصائيات متصل وجاهز!", ephemeral=True)


# 🔘 واجهة أزرار التصفية داخل الجيم
class GamePlayView(discord.ui.View):
    def __init__(self, ctx, players, allowed_role):
        super().__init__(timeout=20.0)
        self.ctx = ctx
        self.players = players
        self.allowed_role = allowed_role
        self.voted_out = None
        self.create_buttons()

    def create_buttons(self):
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
        if interaction.user != self.ctx.author or self.allowed_role not in interaction.user.roles:
            return await interaction.response.send_message("❌ الصلاحية لمشغل الفعالية الإداري فقط لاختيار الضحية من الأزرار!", ephemeral=True)
            
        custom_id = interaction.data['custom_id']
        if custom_id == "random_select":
            self.voted_out = random.choice(self.players)
        else:
            player_id = int(custom_id)
            self.voted_out = next((p for p in self.players if p.id == player_id), None)
            
        self.stop()


# ==================== 🎮 أمر تشغيل اللعبة الاحترافي ====================

@bot.command(name="روليت")
async def start_roulette(ctx, role: discord.Role = None):
    if role is None:
        return await ctx.send("❌ **خطأ في الاستخدام!** يجب تحديد منشن الرتبة المسموحة. مثال:\n`-روليت @منظم`")

    if role not in ctx.author.roles:
        return await ctx.send(رسالة_منع_الاعضاء)

    embed = discord.Embed(
        title="🎯 نظام فعاليات الروليت الكبرى",
        description=f"🔥 تم فتح باب التسجيل في الروليت الحماسية!\n\n👥 **المنضمين حالياً (1/{roulette_config['max_players']}):**\n• {ctx.author.mention}",
        color=roulette_config["embed_color"]
    )
    embed.set_image(url=roulette_config["bg_url"])
    embed.set_footer(text=f"ينتهي التسجيل تلقائياً بعد {roulette_config['signup_time']} ثانية...")
    
    view = RegistrationView(ctx)
    main_msg = await ctx.send(embed=embed, view=view)
    
    await asyncio.sleep(roulette_config["signup_time"])
    view.stop()
    
    players = view.players
    
    if len(players) < 2:
        return await ctx.send(رسالة_الالغاء)

    await ctx.send(رسالة_بدء_التصفية)
    await asyncio.sleep(2)

    while len(players) > 1:
        p_list = ", ".join([p.mention for p in players])
        game_embed = discord.Embed(
            title="🔮 عجلة الموت تدور الحين غصب عن الكل!",
            description=f"🎯 **اللاعبين المتبقين داخل العجلة:**\n{p_list}\n\n⏱️ **لديك 20 ثانية لاختيار لاعب لطرده من الأزرار بالأسفل 👇**",
            color=roulette_config["embed_color"]
        )
        game_embed.set_image(url=roulette_config["bg_url"])
        
        game_view = GamePlayView(ctx, players, role)
        game_msg = await ctx.send(embed=game_embed, view=game_view)
        
        await asyncio.sleep(20)
        game_view.stop()
        
        if not game_view.voted_out:
            victim = random.choice(players)
            await ctx.send(رسالة_انتهاء_وقت_الطرد)
        else:
            victim = game_view.voted_out
            
        players.remove(victim)
        await ctx.send(f"💥 **بـوووووم!** العجلة وقفت في نص جبهة {victim.mention} وتم إقصاءه! 💀💥")
        await asyncio.sleep(3)
        
    winner = players[0]
    winner_embed = discord.Embed(
        title="🏆 الناجي الأخير والملك الأسطوري 🏆",
        description=f"ثبت على العجلة وطير جبهات الكل وطلع الفائز القادح اليوم:\n👑 {winner.mention} 👑\n\nألف مبرووووك الفوز باللقب والهيبة! 🎉🔥",
        color=discord.Color.gold()
    )
    winner_embed.set_thumbnail(url=winner.display_avatar.url)
    await ctx.send(embed=winner_embed)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ هذا الأمر مخصص فقط لـ الإدارة العليا!")

bot.run(os.getenv("DISCORD_TOKEN"))
