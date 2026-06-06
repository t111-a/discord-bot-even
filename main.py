import discord
from discord.ext import commands
import random
import asyncio
import os
import re

# إعداد البوت والبادئة وتفعيل كافة الصلاحيات وإلغاء أمر المساعدة الافتراضي
class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="-", intents=discord.Intents.all(), help_command=None)
    
    async def setup_hook(self):
        await self.tree.sync()

bot = MyBot()

# ====================================================================
# 💾 قاعدة البيانات والإعدادات الافتراضية للنظام (بدون إمبيد - شات عادي)
# ====================================================================
roulette_config = {
    "max_players": 20,              # الحد الأقصى الافتراضي للاعبين
    "signup_time": 30,              # وقت الانتظار لدخول اللاعبين
    "allowed_channels": [],         # قائمة الرومات المسموح باللعب فيها (تتعدل عبر أمر -رومات)
    # رابط صورة عجلة الروليت الدائرية الافتراضية المعتمدة بناء على image_76.png
    "bg_url": "https://i.ibb.co/V9Xm8Yn/roulette-wheel.gif" 
}

# دالة لتنظيف واستخراج الأرقام فقط من الرسائل
def parse_digits(user_input: str):
    clean = re.sub(r'[^\d]', '', user_input)
    return int(clean) if clean.isdigit() else None

# ====================================================================
# ⚙️ أوامر التحكم وتعديل الإعدادات (للإدارة والمسؤولين فقط)
# ====================================================================

# 1. أمر تحديد رومات اللعب عبر المنشن (تشتغل على طول في الرومات المحددة)
@bot.command(name="رومات")
@commands.has_permissions(administrator=True)
async def set_channels(ctx):
    # التحقق من وجود رومات ممهشنة في الرسالة
    if not ctx.message.channel_mentions:
        await ctx.send("يرجى كتابة الأمر ومنشنة الرومات المسموحة، مثال: `-رومات #شات-الألعاب #الشات-العام`")
        return
    
    # تخزين آي دي الرومات الممنشنة بالكامل في القائمة
    roulette_config["allowed_channels"] = [ch.id for ch in ctx.message.channel_mentions]
    mentions_str = ", ".join([ch.mention for ch in ctx.message.channel_mentions])
    await ctx.send(f"تم اعتماد الرومات التالية لتشغيل الروليت فوراً: {mentions_str}")

# 2. أمر تعديل وقت التسجيل
@bot.command(name="وقت")
@commands.has_permissions(administrator=True)
async def set_time(ctx):
    await ctx.send("قائمة وقت الروليت\nيرجى إرسال الوقت المطلوب بالثواني:")
    def check(m): return m.author == ctx.author and m.channel == ctx.channel
    try:
        msg = await bot.wait_for('message', check=check, timeout=30.0)
        seconds = parse_digits(msg.content)
        if seconds:
            roulette_config["signup_time"] = seconds
            await ctx.send(f"تم اعتماد وقت التسجيل الجديد: {seconds} ثانية")
    except asyncio.TimeoutError:
        pass

# 3. أمر تعديل عدد اللاعبين الأقصى
@bot.command(name="عدد")
@commands.has_permissions(administrator=True)
async def set_players(ctx):
    await ctx.send("قائمة عدد الاعضاء\nيرجى إرسال الحد الأقصى للاعبين:")
    def check(m): return m.author == ctx.author and m.channel == ctx.channel
    try:
        msg = await bot.wait_for('message', check=check, timeout=30.0)
        num = parse_digits(msg.content)
        if num:
            roulette_config["max_players"] = num
            await ctx.send(f"تم اعتماد حد اللاعبين الأقصى: {num}")
    except asyncio.TimeoutError:
        pass

# 4. أمر تغيير شكل وعجلة الروليت (تغيير رابط الصورة أو الـ GIF المرفق)
@bot.command(name="خلفية")
@commands.has_permissions(administrator=True)
async def set_bg(ctx):
    await ctx.send("قائمة شكل الروليت\nيرجى إرسال رابط صورة العجلة أو الـ GIF الجديد:")
    def check(m): return m.author == ctx.author and m.channel == ctx.channel
    try:
        msg = await bot.wait_for('message', check=check, timeout=30.0)
        url = msg.content.strip()
        if url.startswith("http"):
            roulette_config["bg_url"] = url
            await ctx.send("تم تحديث شكل وعجلة الروليت بنجاح")
    except asyncio.TimeoutError:
        pass

# 📜 أمر المساعدة المصلح بالكامل (-help) يظهر كرسالة شات عادية بدون مربعات سوداء
@bot.command(name="help")
async def custom_help(ctx):
    chans = ", ".join([f"<#{c_id}>" for c_id in roulette_config["allowed_channels"]]) if roulette_config["allowed_channels"] else "كل الرومات متاح فيها"
    
    help_text = (
        "**قائمة أوامر نظام الروليت (شات عادي رسمي):**\n\n"
        "`-رومات @الرومات` -> لتحديد وتفويض الرومات التي تشتغل فيها اللعبة فوراً\n"
        "`-وقت` -> لتعديل زمن انتظار دخول اللاعبين للجولة\n"
        "`-عدد` -> لتحديد الحد الأقصى المسموح به للمشاركين\n"
        "`-خلفية` -> لتغيير رابط عجلة الروليت الدائرية\n"
        "`-روليت @الرتبة` -> لبدء الفعالية للرتبة المحددة داخل الرومات المصرحة\n\n"
        f"**الإعدادات الحالية:**\n"
        f"الوقت المعتمد: {roulette_config['signup_time']} ثانية | الحد الأقصى: {roulette_config['max_players']} لاعب\n"
        f"الرومات المفعلة حالياً: {chans}"
    )
    await ctx.send(help_text)

# ====================================================================
# 🔘 واجهة أزرار انضمام اللاعبين (شات عادي متناسق مع صورة العجلة)
# ====================================================================
class RegistrationView(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=roulette_config["signup_time"])
        self.ctx = ctx
        self.players = [ctx.author]

    @discord.ui.button(label="الإنضمام", style=discord.ButtonStyle.green)
    async def join_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user in self.players:
            return await interaction.response.send_message("أنت منضم للعبة بالفعل", ephemeral=True)
        if len(self.players) >= roulette_config["max_players"]:
            return await interaction.response.send_message("الروليت ممتلئة بالكامل حالياً", ephemeral=True)
            
        self.players.append(interaction.user)
        await interaction.response.send_message(f"تم انضمام {interaction.user.mention} بنجاح", ephemeral=True)
        
        # تحديث نص الشات العادي مباشرة بقائمة الأسماء المحدثة
        mentions_str = " | ".join([p.mention for p in self.players])
        new_content = (
            f"تم فتح باب التسجيل في الروليت\n\n"
            f"المتضمين حالياً ({len(self.players)}/{roulette_config['max_players']}):\n{mentions_str}\n\n"
            f"{roulette_config['bg_url']}"
        )
        await interaction.message.edit(content=new_content)

    @discord.ui.button(label="الحقيبة", style=discord.ButtonStyle.blurple)
    async def bag_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("حقيبتك فارغة حالياً", ephemeral=True)

    @discord.ui.button(label="الاحصائيات", style=discord.ButtonStyle.gray)
    async def stats_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("النظام جاهز ومتصل وعامل بكفاءة عالية", ephemeral=True)

# ====================================================================
# 🎮 واجهة أزرار التفاعل واستهداف اللاعبين داخل الجولة (شات عادي)
# ====================================================================
class GamePlayView(discord.ui.View):
    def __init__(self, ctx, players, allowed_role):
        super().__init__(timeout=15.0)
        self.ctx = ctx
        self.players = players
        self.allowed_role = allowed_role
        self.voted_out = None
        self.action_type = "normal"
        self.create_buttons()

    def create_buttons(self):
        # توليد الأزرار المرقمة بأسماء اللاعبين المتبقين بالجولة تماماً كما يظهر في image_76.png
        for i, player in enumerate(self.players[:12], start=1):
            btn = discord.ui.Button(label=f"{i} {player.display_name[:12]}", style=discord.ButtonStyle.secondary, custom_id=f"p_{player.id}")
            btn.callback = self.button_callback
            self.add_item(btn)
            
        # أزرار الخصائص المتقدمة والانسحاب أسفل اللاعبين
        btn_revive = discord.ui.Button(label="انعاش", style=discord.ButtonStyle.success, custom_id="action_revive")
        btn_revive.callback = self.button_callback
        self.add_item(btn_revive)

        btn_rand = discord.ui.Button(label="عشوائي", style=discord.ButtonStyle.primary, custom_id="action_random")
        btn_rand.callback = self.button_callback
        self.add_item(btn_rand)

        btn_leave = discord.ui.Button(label="انسحاب", style=discord.ButtonStyle.danger, custom_id="action_leave")
        btn_leave.callback = self.button_callback
        self.add_item(btn_leave)

    async def button_callback(self, interaction: discord.Interaction):
        # التحقق من أن الضاغط يملك الرتبة المصرح لها بالتحكم
        if self.allowed_role not in interaction.user.roles:
            return await interaction.response.send_message("لا تملك الصلاحية للتحكم بأزرار اللعبة", ephemeral=True)
            
        custom_id = interaction.data['custom_id']
        
        if custom_id == "action_random":
            self.voted_out = random.choice(self.players)
            self.action_type = "random"
        elif custom_id == "action_leave":
            self.voted_out = interaction.user
            self.action_type = "leave"
        elif custom_id == "action_revive":
            self.action_type = "revive_power"
            self.voted_out = random.choice(self.players)
        elif custom_id.startswith("p_"):
            p_id = int(custom_id.split("_")[1])
            self.voted_out = next((p for p in self.players if p.id == p_id), None)
            self.action_type = "normal"
            
        self.stop()

# ====================================================================
# 🚀 المحرك الأساسي لإدارة الجولات وإقصاء الضحايا (بدون مربعات سوداء)
# ====================================================================
@bot.command(name="روليت")
async def start_roulette(ctx, role: discord.Role = None):
    if role is None:
        return

    # إذا لم تكن للرجل الرتبة المحددة، لا يرد البوت إطلاقاً لحفظ الهدوء
    if role not in ctx.author.roles:
        return

    # التحقق من الرومات المسموح بها والمحددة عبر أمر -رومات
    if roulette_config["allowed_channels"] and ctx.channel.id not in roulette_config["allowed_channels"]:
        return

    # إنشاء نص شات عادي لفتح باب التسجيل مرفق معه صورة العجلة مباشرة
    init_content = (
        f"تم فتح باب التسجيل في الروليت\n\n"
        f"المتضمين حالياً (1/{roulette_config['max_players']}):\n• {ctx.author.mention}\n\n"
        f"{roulette_config['bg_url']}"
    )
    
    view = RegistrationView(ctx)
    main_msg = await ctx.send(content=init_content, view=view)
    
    await asyncio.sleep(roulette_config["signup_time"])
    view.stop()
    
    players = view.players
    if len(players) < 2:
        return await ctx.send("تم إلغاء الروليت لعدم دخول العدد الكافي من اللاعبين.")

    await ctx.send("بدأت الجولة الآن")
    await asyncio.sleep(2)

    # بدء حلقة الطارد والتصفيات المستمرة
    while len(players) > 1:
        p_list = " | ".join([p.mention for p in players])
        
        # نص الجولة بصيغة شات عادي متطابق مع السيرفرات الكبرى وعجلة الروليت الدائرية
        round_content = (
            f"**جاري سحب الضحية**\n"
            f"اللاعبين المتبقين في الجولة:\n{p_list}\n\n"
            f"لديك 15 ثانية لاختيار لاعب لطردة\n\n"
            f"{roulette_config['bg_url']}"
        )
        
        game_view = GamePlayView(ctx, players, role)
        game_msg = await ctx.send(content=round_content, view=game_view)
        
        await asyncio.sleep(15)
        game_view.stop()
        
        # حالة عدم الاختيار (طرد تلقائي عشوائي لعدم الاختيار في الوقت المحدد)
        if not game_view.voted_out:
            victim = random.choice(players)
            players.remove(victim)
            await ctx.send(f"تم طرد {victim.mention} لعدم الاختيار , سوف تبدأ الجولة القادمة خلال ثواني")
            await asyncio.sleep(4)
            continue
            
        victim = game_view.voted_out
        
        # معالجة الضغوطات والقدرات المفعلة بالشات
        if game_view.action_type == "revive_power":
            await ctx.send(f"{victim.mention} , تم انعاشه سيتم بدء الجولة القادمة خلال ثواني")
        else:
            chance = random.random()
            
            # نسب تفعيل الحماية والهجمات المرتدة عشوائياً
            if chance < 0.15 and len(players) > 2:
                await ctx.send(f"لم يتم طرد {victim.mention} بسبب الحماية , سوف تبدأ الجولة القادمة خلال ثواني")
            elif chance > 0.15 and chance < 0.30 and len(players) > 2:
                attacker = ctx.author
                if attacker in players: players.remove(attacker)
                await ctx.send(f"تم طرد {attacker.mention} بسبب الهجمة المرتده من قبل {victim.mention} , سوف تبدأ الجولة القادمة خلال ثواني")
            else:
                if victim in players: players.remove(victim)
                if game_view.action_type == "random":
                    if len(players) == 1:
                        await ctx.send(f"تم طرد {victim.mention} بشكل عشوائي , الجولة القادمة هي الاخيرة من تختاره العجلة يفوز باللعبة")
                    else:
                        await ctx.send(f"تم طرد {victim.mention} بشكل عشوائي , سوف تبدأ الجولة القادمة خلال ثواني")
                else:
                    await ctx.send(f"تم طرد {victim.mention} من الجولة")
                    
        await asyncio.sleep(4)
        
    # إعلان اسم الفائز النهائي في الشات العادي وصورته الشخصية
    if len(players) == 1:
        winner = players[0]
        await ctx.send(f"**نهاية الجولة**\nالفائز في الروليت:\n{winner.mention}")
        await ctx.send(winner.display_avatar.url)

# منع إرسال رسائل الخطأ الانجليزية بالشات
@bot.event
async def on_command_error(ctx, error):
    pass

bot.run(os.getenv("DISCORD_TOKEN"))
