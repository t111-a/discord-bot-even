import discord
from discord.ext import commands
import random
import asyncio
import os
import re

# تعيين البوت وتحديد رمز البادئة (-) وتفعيل كل الصلاحيات والـ Intents وإلغاء نظام المساعدة الافتراضي لبناء نظام مخصص
class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="-", intents=discord.Intents.all(), help_command=None)
    
    # دالة ربط وسينك الأوامر مع سيرفرات ديسكورد عند التشغيل
    async def setup_hook(self):
        await self.tree.sync()

bot = MyBot()

# ====================================================================
# 💾 قاعدة البيانات والإعدادات الافتراضية للروليت
# ====================================================================
roulette_config = {
    "max_players": 20,              # الحد الأقصى الافتراضي للاعبين في اللعبة
    "signup_time": 30,              # وقت التسجيل الافتراضي بالثواني لدخول الجولة
    "allowed_channel_id": None,     # رقم الروم المخصصة للعب (يتم تعيينه عبر أمر -روم)
    "bg_url": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExM3Z5N2hxZzVnd3N0N3Z4cnd6dzVwZndvOHV4azN0bnd6bWhyeXFidCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/l41YtZOb9EUABnuqA/giphy.gif", # رابط عجلة الروليت الـ GIF
    "embed_color": discord.Color.dark_embed() # لون الإمبيد الافتراضي للرسائل
}

# ====================================================================
# 🛠️ دالة داخلية لتنظيف المدخلات واستخراج الأرقام فقط
# ====================================================================
def parse_digits(user_input: str):
    clean = re.sub(r'[^\d]', '', user_input)
    return int(clean) if clean.isdigit() else None

# ====================================================================
# ⚙️ أوامر إدارة وتعديل إعدادات اللعبة (للإدارة فقط)
# ====================================================================

# أمر تعديل وقت التسجيل في الروليت
@bot.command(name="وقت")
@commands.has_permissions(administrator=True) # يتطلب صلاحية مسؤول
async def set_time(ctx):
    await ctx.send("قائمة وقت الروليت\nيرجى إرسال الوقت المطلوب بالثواني:")
    def check(m): return m.author == ctx.author and m.channel == ctx.channel
    try:
        msg = await bot.wait_for('message', check=check, timeout=30.0)
        seconds = parse_digits(msg.content)
        if seconds:
            roulette_config["signup_time"] = seconds
            await ctx.send(f"تم اعتماد وقت التسجيل: {seconds} ثانية")
    except asyncio.TimeoutError:
        pass

# أمر تعديل الحد الأقصى للاعبين
@bot.command(name="عدد")
@commands.has_permissions(administrator=True) # يتطلب صلاحية مسؤول
async def set_players(ctx):
    await ctx.send("قائمة عدد الاعضاء\nيرجى إرسال الحد الأقصى للاعبين:")
    def check(m): return m.author == ctx.author and m.channel == ctx.channel
    try:
        msg = await bot.wait_for('message', check=check, timeout=30.0)
        num = parse_digits(msg.content)
        if num:
            roulette_config["max_players"] = num
            await ctx.send(f"تم اعتماد حد اللاعبين: {num}")
    except asyncio.TimeoutError:
        pass

# أمر تغيير صورة أو خلفية الروليت المتحركة
@bot.command(name="خلفية")
@commands.has_permissions(administrator=True) # يتطلب صلاحية مسؤول
async def set_bg(ctx):
    await ctx.send("قائمة شكل الروليت\nيرجى إرسال رابط الصورة أو الـ GIF:")
    def check(m): return m.author == ctx.author and m.channel == ctx.channel
    try:
        msg = await bot.wait_for('message', check=check, timeout=30.0)
        url = msg.content.strip()
        if url.startswith("http"):
            roulette_config["bg_url"] = url
            await ctx.send("تم اعتماد الخلفية الجديدة بنجاح")
    except asyncio.TimeoutError:
        pass

# أمر تحديد وتخصيص روم معينة للعب فقط وحظر باقي الرومات
@bot.command(name="روم")
@commands.has_permissions(administrator=True) # يتطلب صلاحية مسؤول
async def set_channel(ctx, channel: discord.TextChannel = None):
    if channel is None:
        roulette_config["allowed_channel_id"] = ctx.channel.id
        await ctx.send(f"تم تخصيص هذه الروم لتشغيل الفعالية: {ctx.channel.mention}")
    else:
        roulette_config["allowed_channel_id"] = channel.id
        await ctx.send(f"تم تخصيص الروم المحددة لتشغيل الفعالية: {channel.mention}")

# ====================================================================
# 📜 أمر المساعدة المخصص والمصلح بالكامل (-help)
# ====================================================================
@bot.command(name="help")
async def custom_help(ctx):
    embed = discord.Embed(
        title="قائمة الروليت والتحكم",
        description="الأوامر والخيارات المتاحة لإدارة نظام الفعالية:",
        color=roulette_config["embed_color"]
    )
    # إضافة حقول الأوامر وشرحها باللغة العربية داخل رسالة الـ Embed
    embed.add_field(name="-وقت", value="لتعديل زمن انتظار دخول اللاعبين للجولة", inline=False)
    embed.add_field(name="-عدد", value="لتحديد الحد الأقصى المسموح به للمشاركين في اللعبة", inline=False)
    embed.add_field(name="-خلفية", value="لتغيير الرابط النشط لعجلة الروليت المتحركة GIF", inline=False)
    embed.add_field(name="-روم", value="لتحديد الروم المخصصة التي يسمح ببدء اللعبة داخلها فقط", inline=False)
    embed.add_field(name="-روليت @الرتبة", value="الأمر الأساسي لبدء الفعالية لرتبة محددة تمتلكها", inline=False)
    
    # عرض الإعدادات الحالية مباشرة أسفل قائمة الأوامر لمعرفتها
    current_chan = f"<#{roulette_config['allowed_channel_id']}>" if roulette_config["allowed_channel_id"] else "كل الرومات متاح فيها"
    embed.add_field(
        name="الإعدادات الحالية للروليت", 
        value=f"الوقت: {roulette_config['signup_time']} ثانية | الحد الأقصى: {roulette_config['max_players']} عضو\nالروم المعتمدة: {current_chan}"
    )
    await ctx.send(embed=embed)

# ====================================================================
# 🔘 واجهة أزرار انضمام وقائمة اللاعبين عند بدء التسجيل
# ====================================================================
class RegistrationView(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=roulette_config["signup_time"])
        self.ctx = ctx
        self.players = [ctx.author] # صانع الجولة ينضم تلقائياً

    # زر الانضمام إلى قائمة اللاعبين
    @discord.ui.button(label="الإنضمام", style=discord.ButtonStyle.green)
    async def join_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user in self.players:
            return await interaction.response.send_message("أنت منضم للعبة بالفعل", ephemeral=True)
        if len(self.players) >= roulette_config["max_players"]:
            return await interaction.response.send_message("الروليت ممتلئة بالكامل حالياً", ephemeral=True)
            
        self.players.append(interaction.user)
        await interaction.response.send_message(f"تم انضمام {interaction.user.mention} بنجاح", ephemeral=True)
        
        # تحديث قائمة الإمبيد لإظهار أسماء المنضمين بشكل حي ومباشر
        embed = interaction.message.embeds[0]
        embed.description = f"تم فتح باب التسجيل in الروليت\n\nالمتضمين حالياً ({len(self.players)}/{roulette_config['max_players']}):\n" + "\n".join([f"• {p.mention}" for p in self.players])
        await interaction.message.edit(embed=embed)

    # زر الحقيبة (استعراضي ورسمي)
    @discord.ui.button(label="الحقيبة", style=discord.ButtonStyle.blurple)
    async def bag_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("حقيبتك فارغة حالياً", ephemeral=True)

    # زر الإحصائيات للتأكد من حالة اتصال البوت وسرعته
    @discord.ui.button(label="الاحصائيات", style=discord.ButtonStyle.gray)
    async def stats_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("النظام جاهز ومتصل", ephemeral=True)

# ====================================================================
# 🎮 واجهة أزرار لوحة التحكم باللعب واستهداف الضحايا أثناء الجولة
# ====================================================================
class GamePlayView(discord.ui.View):
    def __init__(self, ctx, players, allowed_role):
        super().__init__(timeout=15.0) # المهلة المحددة للاختيار هي 15 ثانية
        self.ctx = ctx
        self.players = players
        self.allowed_role = allowed_role
        self.voted_out = None           # لتخزين الشخص المستهدف بالطرد
        self.action_type = "normal"     # نوع الإجراء (طرد عادي، عشوائي، قنبلة، انسحاب)
        self.create_buttons()

    # توليد أزرار مخصصة بأسماء اللاعبين وأزرار الخصائص المتقدمة تلقائياً
    def create_buttons(self):
        # إنشاء زر لكل لاعب متواجد داخل الجولة (الحد الأقصى للظهور 12 زر لتفادي تخطي حدود ديسكورد)
        for player in self.players[:12]:
            btn = discord.ui.Button(label=player.display_name[:15], style=discord.ButtonStyle.secondary, custom_id=f"p_{player.id}")
            btn.callback = self.button_callback
            self.add_item(btn)
            
        # إنشاء أزرار القدرات والخصائص الاستراتيجية والانسحاب
        actions = [("عشوائي", "action_random"), ("قنبلة", "action_bomb"), ("انسحاب", "action_leave")]
        for label, c_id in actions:
            btn = discord.ui.Button(label=label, style=discord.ButtonStyle.primary, custom_id=c_id)
            btn.callback = self.button_callback
            self.add_item(btn)

    # معالجة الضغط على أي زر داخل لوحة التحكم بالجولة
    async def button_callback(self, interaction: discord.Interaction):
        # التحقق الصارم من رتبة وصلاحية الشخص الضاغط على الزر (إذا لم يكن هو صانع الجولة وصاحب الرتبة يتم رفضه)
        if interaction.user != self.ctx.author or self.allowed_role not in interaction.user.roles:
            return await interaction.response.send_message("لا تملك الصلاحية للتحكم بأزرار اللعبة", ephemeral=True)
            
        custom_id = interaction.data['custom_id']
        
        # عند اختيار "عشوائي"
        if custom_id == "action_random":
            self.voted_out = random.choice(self.players)
            self.action_type = "random"
        # عند اختيار "قنبلة" لطرد عضوين معاً
        elif custom_id == "action_bomb":
            self.action_type = "bomb"
            self.voted_out = random.sample(self.players, min(2, len(self.players)))
        # عند اختيار "انسحاب" من اللعبة
        elif custom_id == "action_leave":
            self.voted_out = interaction.user
            self.action_type = "leave"
        # عند الضغط على اسم لاعب محدد لطردة بشكل مباشر ومستهدف
        elif custom_id.startswith("p_"):
            p_id = int(custom_id.split("_")[1])
            self.voted_out = next((p for p in self.players if p.id == p_id), None)
            self.action_type = "normal"
            
        self.stop() # إيقاف الانتظار بعد أخذ القرار فوراً

# ====================================================================
# 🚀 المحرك الأساسي والأمر الرئيسي لبدء تشغيل لعبة الروليت
# ====================================================================
@bot.command(name="روليت")
async def start_roulette(ctx, role: discord.Role = None):
    if role is None:
        return

    # قاعدة عدم الرد نهائياً في الشات إذا لم تكن لدى منفذ الأمر الرتبة المحددة
    if role not in ctx.author.roles:
        return

    # التحقق مما إذا كانت اللعبة تعمل في الروم المخصصة المحددة من الإدارة أم لا
    if roulette_config["allowed_channel_id"] and ctx.channel.id != roulette_config["allowed_channel_id"]:
        return await ctx.send("لا يمكن تشغيل الفعالية في هذه الروم، يرجى الانتقال للروم المخصصة", delete_after=5)

    # إنشاء رسالة الإمبيد الافتتاحية لفتح باب التسجيل
    embed = discord.Embed(
        title="نظام فعاليات للروليت الكبرى",
        description=f"تم فتح باب التسجيل في الروليت\n\nالمتضمين حالياً (1/{roulette_config['max_players']}):\n• {ctx.author.mention}",
        color=roulette_config["embed_color"]
    )
    embed.set_image(url=roulette_config["bg_url"])
    
    view = RegistrationView(ctx)
    main_msg = await ctx.send(embed=embed, view=view)
    
    # الانتظار ريثما ينتهي وقت التسجيل المحدد بالثواني
    await asyncio.sleep(roulette_config["signup_time"])
    view.stop()
    
    players = view.players
    # التحقق من وجود لاعبين على الأقل لبدء الفعالية
    if len(players) < 2:
        return await ctx.send("تم إلغاء الروليت لعدم دخول العدد الكافي من اللاعبين (المطلوب 2 على الأقل)")

    await ctx.send("بدأت الجولة الآن")
    await asyncio.sleep(2)

    # حلقة التكرار المستمرة لإقصاء اللاعبين واحداً تلو الآخر حتى يتبقى فائز واحد
    while len(players) > 1:
        p_list = " | ".join([p.mention for p in players])
        
        # إمبيد عرض لوحة التحكم وإحصائيات الجولة الجارية
        game_embed = discord.Embed(
            title="جاري سحب الضحية",
            description=f"اللاعبين المتبقين في الجولة:\n{p_list}\n\nلديك 15 ثانية لاختيار لاعب لطردة",
            color=roulette_config["embed_color"]
        )
        game_embed.set_image(url=roulette_config["bg_url"])
        
        game_view = GamePlayView(ctx, players, role)
        game_msg = await ctx.send(embed=game_embed, view=game_view)
        
        # انتظار 15 ثانية لاتخاذ القرار من الأزرار
        await asyncio.sleep(15)
        game_view.stop()
        
        # [حالة الإقصاء التلقائي]: عند انتهاء الوقت دون الضغط على أي زر
        if not game_view.voted_out:
            victim = random.choice(players)
            players.remove(victim)
            await ctx.send(f"تم طرد {victim.mention} لعدم الاختيار , سوف تبدأ الجولة القادمة خلال ثواني")
            await asyncio.sleep(4)
            continue
            
        # [حالة استخدام القنبلة]: طرد عضوين معاً من الجولة
        if game_view.action_type == "bomb":
            victims = game_view.voted_out
            v_mentions = " و ".join([v.mention for v in victims])
            for v in victims:
                if v in players: players.remove(v)
            await ctx.send(f"تم استعمال القنبله وطرد {v_mentions}")
            
        # [حالة الطرد العادي أو العشوائي المستهدف]: مع تفعيل احتمالات القدرات المتقدمة
        else:
            victim = game_view.voted_out
            chance = random.random() # توليد نسبة عشوائية بين 0 و 1 لتحديد تفعيل الخصائص
            
            # 1. تفعيل خاصية الحماية بنسبة 15%
            if chance < 0.15 and len(players) > 2: 
                await ctx.send(f"لم يتم طرد {victim.mention} بسبب الحماية , سوف تبدأ الجولة القادمة خلال ثواني")
            # 2. تفعيل خاصية الهجمة المرتدة بنسبة 15% (يرتد الطرد على من فجر الجولة)
            elif chance > 0.15 and chance < 0.30 and len(players) > 2: 
                attacker = ctx.author
                if attacker in players: players.remove(attacker)
                await ctx.send(f"تم طرد {attacker.mention} بسبب الهجمة المرتده من قبل {victim.mention} , سوف تبدأ الجولة القادمة خلال ثواني")
            # 3. تفعيل خاصية الإنعاش بنسبة 10% لإنقاذ الضحية وإعادته فورا
            elif chance > 0.30 and chance < 0.40: 
                await ctx.send(f"{victim.mention} , تم انعاشه سيتم بدء الجولة القادمة خلال ثواني")
            # 4. تنفيذ الطرد الفعلي الرسمي عند عدم تفعيل أي قدرة دفاعية
            else:
                if victim in players: players.remove(victim)
                # صيغة نص الطرد العشوائي المعتمدة بالسيرفرات الكبرى عند استخدام زر عشوائي
                if game_view.action_type == "random":
                    if len(players) == 1:
                        await ctx.send(f"تم طرد {victim.mention} بشكل عشوائي , الجولة القادمة هي الاخيرة من تختاره العجلة يفوز باللعبة")
                    else:
                        await ctx.send(f"تم طرد {victim.mention} بشكل عشوائي , سوف تبدأ الجولة القادمة خلال ثواني")
                # صيغة نص الطرد المستهدف العادي
                else:
                    await ctx.send(f"تم طرد {victim.mention} من الجولة")
                    
        await asyncio.sleep(4) # انتظار 4 ثواني فاصلة ومريحة بين الجولات لتهيئة الشات
        
    # ====================================================================
    # 🏆 إعلان الفائز النهائي بالروليت عند بقاء آخر ناجي
    # ====================================================================
    if len(players) == 1:
        winner = players[0]
        winner_embed = discord.Embed(
            title="نهاية الجولة",
            description=f"الفائز في الروليت:\n{winner.mention}",
            color=discord.Color.gold()
        )
        winner_embed.set_image(url=winner.display_avatar.url)
        await ctx.send(embed=winner_embed)

# كتم وتجاهل الأخطاء لضمان عدم رد البوت بأي رسائل خطأ إنجليزية مشوهة في الشات العام
@bot.event
async def on_command_error(ctx, error):
    pass

# تشغيل البوت باستخدام التوكن المخزن بملف البيئة الخاص بك
bot.run(os.getenv("DISCORD_TOKEN"))
