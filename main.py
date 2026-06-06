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
# 💾 قاعدة البيانات والإعدادات الافتراضية للنظام
# ====================================================================
roulette_config = {
    "max_players": 20,
    "signup_time": 30,
    "allowed_channel_id": None, # يتم تحديده عبر أمر -روم
    "bg_url": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExM3Z5N2hxZzVnd3N0N3Z4cnd6dzVwZndvOHV4azN0bnd6bWhyeXFidCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/l41YtZOb9EUABnuqA/giphy.gif",
    "embed_color": discord.Color.dark_embed()
}

# ====================================================================
# 🛠️ أوامر التعديل التفاعلية الرسمية
# ====================================================================

def parse_digits(user_input: str):
    clean = re.sub(r'[^\d]', '', user_input)
    return int(clean) if clean.isdigit() else None

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
            await ctx.send(f"تم اعتماد وقت التسجيل: {seconds} ثانية")
    except asyncio.TimeoutError:
        pass

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
            await ctx.send(f"تم اعتماد حد اللاعبين: {num}")
    except asyncio.TimeoutError:
        pass

@bot.command(name="خلفية")
@commands.has_permissions(administrator=True)
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

@bot.command(name="روم")
@commands.has_permissions(administrator=True)
async def set_channel(ctx, channel: discord.TextChannel = None):
    if channel is None:
        roulette_config["allowed_channel_id"] = ctx.channel.id
        await ctx.send(f"تم تخصيص هذه الروم لتشغيل الفعالية: {ctx.channel.mention}")
    else:
        roulette_config["allowed_channel_id"] = channel.id
        await ctx.send(f"تم تخصيص الروم المحددة لتشغيل الفعالية: {channel.mention}")


# 📜 قائمة المساعدة الرسمية المتوافقة مع طلبك
@bot.command(name="help")
async def custom_help(ctx):
    if ctx.content.strip() == "-help قائمة":
        pass # لمعالجة صيغة الأمر المركب إذا لزم الأمر
        
    embed = discord.Embed(
        title="قائمة الروليت والتحكم",
        description="الأوامر والخيارات المتاحة لإدارة نظام الفعالية:",
        color=roulette_config["embed_color"]
    )
    embed.add_field(name="-وقت الروليت", value="لتعديل زمن انتظار دخول اللاعبين للجولة", inline=False)
    embed.add_field(name="-لون الخلفيه", value="لتعديل المظهر العام وثيم الرسائل الصادرة", inline=False)
    embed.add_field(name="-الاعضاء والروليت لتشغيل", value="لتحديد الحد الأقصى المسموح به للمشاركين", inline=False)
    embed.add_field(name="-شكل الروليت", value="لتغيير الرابط النشط لعجلة الروليت المتحركة", inline=False)
    embed.add_field(name="-روم", value="لتحديد الروم المخصصة التي يسمح ببدء اللعبة داخلها فقط", inline=False)
    embed.add_field(name="-روليت @الرتبة", value="الأمر الأساسي لبدء الفعالية للرتبة المحددة", inline=False)
    
    current_chan = f"<#{roulette_config['allowed_channel_id']}>" if roulette_config["allowed_channel_id"] else "كل الرومات متاح فيها"
    embed.add_field(
        name="الإعدادات الحالية للروليت", 
        value=f"الوقت: {roulette_config['signup_time']} ثانية | الحد الأقصى: {roulette_config['max_players']} عضو\nالروم المعتمدة: {current_chan}"
    )
    await ctx.send(embed=embed)


# ====================================================================
# 🔘 واجهات الأزرار والتفاعل أثناء اللعب
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
        
        embed = interaction.message.embeds[0]
        embed.description = f"تم فتح باب التسجيل في الروليت\n\nالمتضمين حالياً ({len(self.players)}/{roulette_config['max_players']}):\n" + "\n".join([f"• {p.mention}" for p in self.players])
        await interaction.message.edit(embed=embed)

    @discord.ui.button(label="الحقيبة", style=discord.ButtonStyle.blurple)
    async def bag_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("حقيبتك فارغة حالياً", ephemeral=True)

    @discord.ui.button(label="الاحصائيات", style=discord.ButtonStyle.gray)
    async def stats_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("النظام جاهز ومتصل", ephemeral=True)


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
        # أزرار أسماء اللاعبين
        for player in self.players[:12]:
            btn = discord.ui.Button(label=player.display_name[:15], style=discord.ButtonStyle.secondary, custom_id=f"p_{player.id}")
            btn.callback = self.button_callback
            self.add_item(btn)
            
        # أزرار الخصائص المتقدمة
        actions = [("عشوائي", "action_random"), ("قنبلة", "action_bomb"), ("انسحاب", "action_leave")]
        for label, c_id in actions:
            btn = discord.ui.Button(label=label, style=discord.ButtonStyle.primary, custom_id=c_id)
            btn.callback = self.button_callback
            self.add_item(btn)

    async def button_callback(self, interaction: discord.Interaction):
        if interaction.user != self.ctx.author or self.allowed_role not in interaction.user.roles:
            return await interaction.response.send_message("لا تملك الصلاحية للتحكم بأزرار اللعبة", ephemeral=True)
            
        custom_id = interaction.data['custom_id']
        
        if custom_id == "action_random":
            self.voted_out = random.choice(self.players)
            self.action_type = "random"
        elif custom_id == "action_bomb":
            self.action_type = "bomb"
            self.voted_out = random.sample(self.players, min(2, len(self.players)))
        elif custom_id == "action_leave":
            self.voted_out = interaction.user
            self.action_type = "leave"
        elif custom_id.startswith("p_"):
            p_id = int(custom_id.split("_")[1])
            self.voted_out = next((p for p in self.players if p.id == p_id), None)
            self.action_type = "normal"
            
        self.stop()


# ==================== 🎮 المحرك الأساسي للعبة الروليت ====================

@bot.command(name="روليت")
async def start_roulette(ctx, role: discord.Role = None):
    if role is None:
        return

    # التحقق من الرتبة (إذا لم تكن لديه الصلاحية، لا يستجيب البوت إطلاقاً)
    if role not in ctx.author.roles:
        return

    # التحقق من الروم المخصصة
    if roulette_config["allowed_channel_id"] and ctx.channel.id != roulette_config["allowed_channel_id"]:
        return await ctx.send("لا يمكن تشغيل الفعالية في هذه الروم، يرجى الانتقال للروم المخصصة", delete_after=5)

    embed = discord.Embed(
        title="نظام فعاليات للروليت الكبرى",
        description=f"تم فتح باب التسجيل في الروليت\n\nالمتضمين حالياً (1/{roulette_config['max_players']}):\n• {ctx.author.mention}",
        color=roulette_config["embed_color"]
    )
    embed.set_image(url=roulette_config["bg_url"])
    
    view = RegistrationView(ctx)
    main_msg = await ctx.send(embed=embed, view=view)
    
    await asyncio.sleep(roulette_config["signup_time"])
    view.stop()
    
    players = view.players
    if len(players) < 2:
        return await ctx.send("تم إلغاء الروليت لعدم دخول العدد الكافي من اللاعبين (المطلوب 2 على الأقل)")

    await ctx.send("بدأت الجولة الآن")
    await asyncio.sleep(2)

    while len(players) > 1:
        p_list = " | ".join([p.mention for p in players])
        
        game_embed = discord.Embed(
            title="جاري سحب الضحية",
            description=f"اللاعبين المتبقين في الجولة:\n{p_list}\n\nلديك 15 ثانية لاختيار لاعب لطردة",
            color=roulette_config["embed_color"]
        )
        game_embed.set_image(url=roulette_config["bg_url"])
        
        game_view = GamePlayView(ctx, players, role)
        game_msg = await ctx.send(embed=game_embed, view=game_view)
        
        await asyncio.sleep(15)
        game_view.stop()
        
        # في حال عدم الاختيار (إقصاء لعدم الاختيار / طرد تلقائي)
        if not game_view.voted_out:
            victim = random.choice(players)
            players.remove(victim)
            await ctx.send(f"تم طرد {victim.mention} لعدم الاختيار , سوف تبدأ الجولة القادمة خلال ثواني")
            await asyncio.sleep(4)
            continue
            
        # معالجة نظام القنبلة
        if game_view.action_type == "bomb":
            victims = game_view.voted_out
            v_mentions = " و ".join([v.mention for v in victims])
            for v in victims:
                if v in players: players.remove(v)
            await ctx.send(f"تم استعمال القنبله وطرد {v_mentions}")
            
        # معالجة الخيارات العادية أو العشوائية مع تطبيق (الحماية / الهجمة المرتدة / الإنعاش)
        else:
            victim = game_view.voted_out
            chance = random.random() # تحديد الاحتمالات العشوائية للخصائص المتقدمة
            
            if chance < 0.15 and len(players) > 2: # احتمال الحماية 15%
                await ctx.send(f"لم يتم طرد {victim.mention} بسبب الحماية , سوف تبدأ الجولة القادمة خلال ثواني")
            elif chance > 0.15 and chance < 0.30 and len(players) > 2: # احتمال الهجمة المرتدة 15%
                attacker = ctx.author
                if attacker in players: players.remove(attacker)
                await ctx.send(f"تم طرد {attacker.mention} بسبب الهجمة المرتده من قبل {victim.mention} , سوف تبدأ الجولة القادمة خلال ثواني")
            elif chance > 0.30 and chance < 0.40: # احتمال الإنعاش 10%
                await ctx.send(f"{victim.mention} , تم انعاشه سيتم بدء الجولة القادمة خلال ثواني")
            else:
                # طرد اعتيادي أو عشوائي بناء على الأزرار
                if victim in players: players.remove(victim)
                if game_view.action_type == "random":
                    if len(players) == 1:
                        await ctx.send(f"تم طرد {victim.mention} بشكل عشوائي , الجولة القادمة هي الاخيرة من تختاره العجلة يفوز باللعبة")
                    else:
                        await ctx.send(f"تم طرد {victim.mention} بشكل عشوائي , سوف تبدأ الجولة القادمة خلال ثواني")
                else:
                    await ctx.send(f"تم طرد {victim.mention} من الجولة")
                    
        await asyncio.sleep(4)
        
    # إعلان الناجي الفائز النهائي
    if len(players) == 1:
        winner = players[0]
        winner_embed = discord.Embed(
            title="نهاية الجولة",
            description=f"الفائز في الروليت:\n{winner.mention}",
            color=discord.Color.gold()
        )
        winner_embed.set_image(url=winner.display_avatar.url)
        await ctx.send(embed=winner_embed)

# تجاهل الأخطاء لعدم إرسال أي ردود غير مصرح بها في الشات
@bot.event
async def on_command_error(ctx, error):
    pass

bot.run(os.getenv("DISCORD_TOKEN"))
