import discord
from discord.ext import commands
import random
import asyncio
import os
import re
import io
import time
import aiohttp
from PIL import Image, ImageDraw, ImageFont, ImageOps

# إعداد الصلاحيات الكاملة للبوت لضمان قراءة الرسائل وتفعيل الأوامر
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="-", intents=intents, help_command=None)

# ====================================================================
# 💾 قاعدة البيانات وشجرة الإعدادات الكاملة للروليت
# ====================================================================
roulette_config = {
    "max_players": 20,
    "signup_time": 30,
    "settings_channel_id": None, # الأيدي الخاص بروم الإعدادات السرية
    "allowed_channels": [],       # قائمة الأيديهات الخاصة برومات اللعب العامة
    "bg_url": "https://i.ibb.co/V9Xm8Yn/roulette-wheel.gif",
    
    "features_enabled": True,       
    "bomb_enabled": True,           
    "protection_chance": 0.15,      
    "counter_chance": 0.15,         
    
    "msg_timeout": "تم طرد {victim} لعدم الاختيار , سوف تبدأ الجولة القادمة خلال ثواني .",
    "msg_random": "تم طرد {victim} بشكل عشوائي , سوف تبدأ الجولة القادمة خلال ثواني .",
    "msg_normal": "تم طرد {victim} من الجولة"
}

@bot.event
async def on_ready():
    print(f"✅ تم تشغيل البوت بنجاح باسم: {bot.user}")

def parse_digits(user_input: str):
    clean = re.sub(r'[^\d]', '', user_input)
    return int(clean) if clean.isdigit() else None

async def download_image(url: str) -> bytes:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                return await resp.read()
    return None

# ====================================================================
# 🎨 محرك تصميم صورة الفائز
# ====================================================================
async def generate_winner_image(avatar_url: str, name: str) -> io.BytesIO:
    avatar_bytes = await download_image(avatar_url)
    if not avatar_bytes:
        return None
    avatar_img = Image.open(io.BytesIO(avatar_bytes)).convert("RGBA")
    
    base_w, base_h = 800, 500
    base_img = Image.new("RGBA", (base_w, base_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(base_img)
    
    draw.chord([50, 150, 350, 350], 160, 340, fill=(169, 169, 169, 255))
    draw.chord([80, 180, 350, 320], 160, 340, fill=(105, 105, 105, 255))
    draw.chord([450, 150, 750, 350], 200, 20, fill=(169, 169, 169, 255))
    draw.chord([450, 180, 720, 320], 200, 20, fill=(105, 105, 105, 255))
    
    avatar_size = 220
    avatar_img = avatar_img.resize((avatar_size, avatar_size), Image.Resampling.LANCZOS)
    mask = Image.new("L", (avatar_size, avatar_size), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse((0, 0, avatar_size, avatar_size), fill=255)
    
    circular_avatar = ImageOps.fit(avatar_img, (avatar_size, avatar_size), centering=(0.5, 0.5))
    circular_avatar.putalpha(mask)
    
    circle_x = (base_w - avatar_size) // 2
    circle_y = 100
    draw.ellipse([circle_x - 10, circle_y - 10, circle_x + avatar_size + 10, circle_y + avatar_size + 10], outline=(192, 192, 192, 255), width=8)
    base_img.paste(circular_avatar, (circle_x, circle_y), circular_avatar)
    
    rect_w, rect_h = 320, 55
    rect_x = (base_w - rect_w) // 2
    rect_y = 360
    draw.rounded_rectangle([rect_x, rect_y, rect_x + rect_w, rect_y + rect_h], radius=15, fill=(128, 128, 128, 255))
    
    try:
        font = ImageFont.load_default()
    except:
        font = ImageFont.load_default()
        
    text_w = draw.textlength(name, font=font)
    draw.text((rect_x + (rect_w - text_w) // 2, rect_y + 15), name, fill=(255, 255, 255, 255), font=font)
    
    output = io.BytesIO()
    base_img.save(output, format="PNG")
    output.seek(0)
    return output

# ====================================================================
# ⚙️ أوامر التحكم والبرمجة مع نظام العزل الذكي للرومات
# ====================================================================
@bot.command(name="help")
async def custom_help(ctx):
    # التحقق: إذا تم تحديد روم إعدادات، لا يعمل الأمر إلا بداخلها
    if roulette_config["settings_channel_id"] and ctx.channel.id != roulette_config["settings_channel_id"]:
        return await ctx.send(f"❌ هذا الأمر مخصص فقط داخل روم الإعدادات: <#{roulette_config['settings_channel_id']}>", delete_after=5)
        
    chans = ", ".join([f"<#{c_id}>" for c_id in roulette_config["allowed_channels"]])
    help_text = (
        "**لوحة تحكم وبرمجة نظام الروليت الشاملة:**\n\n"
        "`-روم_الاعدادات` -> لتثبيت روم الإدارة والتحكم الحالية (تضبط الإعدادات هنا بخصوصية)\n"
        "`-رومات @روم` -> لتحديد رومات اللعب العامة (المنشن للشات العام اللي بيلعبون فيه)\n"
        "`-وقت` / `-عدد` / `-خلفية` -> لتعديل الوقت، السعة، ومظهر العجلة\n"
        "`-خصائص تشغيل/ايقاف` -> للتحكم بالقدرات الاستراتيجية والتكتيكية\n"
        "`-احتمال النسبة` -> لتعديل حظ تفعيل الحماية والمرتدة (مثال: -احتمال 15)\n"
        "`-قنبلة تشغيل/ايقاف` -> لتفعيل أو حظر زر طرد عضوين معاً\n"
        "`-نسخ وضع النص` -> لإعادة صياغة وبرمجة رسائل الطرد التلقائي\n"
        "`-بنك` -> لقياس وفحص سرعة اتصال البوت الحالية\n\n"
        f"**الوضعية الحالية للبرمجة:**\n"
        f"الخصائص المتقدمة: {'مفعلة' if roulette_config['features_enabled'] else 'معطلة'} | القنبلة: {'مفعلة' if roulette_config['bomb_enabled'] else 'معطلة'} | نسبة الحظ: {int(roulette_config['protection_chance']*100)}%\n"
        f"رومات الفعاليات العامّة النشطة: {chans if chans else 'لم تحدد بعد (متاح في كل السيرفر)'}"
    )
    await ctx.send(help_text)

@bot.command(name="روم_الاعدادات")
@commands.has_permissions(administrator=True)
async def set_settings_channel(ctx):
    roulette_config["settings_channel_id"] = ctx.channel.id
    await ctx.send(f"🔒 تم اعتماد هذه الروم كمنصة حصرية وسريّة لإعدادات وبرمجة الروليت: {ctx.channel.mention}")

@bot.command(name="رومات")
@commands.has_permissions(administrator=True)
async def set_channels(ctx):
    if roulette_config["settings_channel_id"] and ctx.channel.id != roulette_config["settings_channel_id"]: 
        return await ctx.send(f"❌ اذهب إلى روم الإعدادات لتنفيذ هذا الأمر: <#{roulette_config['settings_channel_id']}>")
    if not ctx.message.channel_mentions: 
        return await ctx.send("يرجى منشنة الروم العامّة اللتي ترغب باللعب فيها! مثال: `-رومات #شات-الألعاب`")
    roulette_config["allowed_channels"] = [ch.id for ch in ctx.message.channel_mentions]
    await ctx.send("📢 تم اعتماد وتحديد رومات اللعب العامة بنجاح.")

@bot.command(name="خصائص")
@commands.has_permissions(administrator=True)
async def toggle_features(ctx, status: str = None):
    if roulette_config["settings_channel_id"] and ctx.channel.id != roulette_config["settings_channel_id"]: return
    if status in ["تشغيل", "on", "true"]:
        roulette_config["features_enabled"] = True
        await ctx.send("تم تفعيل الخصائص المتقدمة في الجولات.")
    elif status in ["ايقاف", "off", "false"]:
        roulette_config["features_enabled"] = False
        await ctx.send("تم إيقاف الخصائص كلياً؛ الطرد الآن مباشر واعتيادي.")

@bot.command(name="احتمال")
@commands.has_permissions(administrator=True)
async def set_chances(ctx, percent: int = None):
    if roulette_config["settings_channel_id"] and ctx.channel.id != roulette_config["settings_channel_id"]: return
    if percent is not None and 0 <= percent <= 100:
        val = percent / 100
        roulette_config["protection_chance"] = val
        roulette_config["counter_chance"] = val
        await ctx.send(f"تم تعديل نسب احتمالات القدرات الدفاعية إلى: {percent}%")

@bot.command(name="قنبلة")
@commands.has_permissions(administrator=True)
async def toggle_bomb(ctx, status: str = None):
    if roulette_config["settings_channel_id"] and ctx.channel.id != roulette_config["settings_channel_id"]: return
    if status in ["تشغيل", "on"]:
        roulette_config["bomb_enabled"] = True
        await ctx.send("تم تفعيل ميزة زر القنبلة في الجولة.")
    elif status in ["ايقاف", "off"]:
        roulette_config["bomb_enabled"] = False
        await ctx.send("تم إخفاء زر القنبلة من الجولات.")

@bot.command(name="نسخ")
@commands.has_permissions(administrator=True)
async def change_texts(ctx, mode: str = None, *, new_text: str = None):
    if roulette_config["settings_channel_id"] and ctx.channel.id != roulette_config["settings_channel_id"]: return
    if mode in ["وقت", "عشوائي", "عادي"] and new_text:
        key = "msg_timeout" if mode == "وقت" else ("msg_random" if mode == "عشوائي" else "msg_normal")
        roulette_config[key] = new_text
        await ctx.send(f"تمت إعادة برمجة نص الإقصاء لوضع [{mode}] بنجاح.")

@bot.command(name="بنك")
async def ping_speed(ctx):
    start_time = time.monotonic()
    msg = await ctx.send("جاري فحص سرعة الاستجابة...")
    end_time = time.monotonic()
    latency = round((end_time - start_time) * 1000)
    bot_ping = round(bot.latency * 1000)
    await msg.edit(content=f"سرعة اتصال النظام: {bot_ping}ms | سرعة استجابة الشات: {latency}ms")

@bot.command(name="وقت")
@commands.has_permissions(administrator=True)
async def set_time(ctx):
    if roulette_config["settings_channel_id"] and ctx.channel.id != roulette_config["settings_channel_id"]: return
    await ctx.send("أرسل وقت التسجيل بالثواني:")
    try:
        msg = await bot.wait_for('message', check=lambda m: m.author == ctx.author, timeout=30.0)
        sec = parse_digits(msg.content)
        if sec: roulette_config["signup_time"] = sec; await ctx.send(f"تم الحفظ: {sec} ثانية")
    except: pass

@bot.command(name="عدد")
@commands.has_permissions(administrator=True)
async def set_players(ctx):
    if roulette_config["settings_channel_id"] and ctx.channel.id != roulette_config["settings_channel_id"]: return
    await ctx.send("أرسل الحد الأقصى للأعضاء:")
    try:
        msg = await bot.wait_for('message', check=lambda m: m.author == ctx.author, timeout=30.0)
        num = parse_digits(msg.content)
        if num: roulette_config["max_players"] = num; await ctx.send(f"تم الحفظ: {num} لاعب")
    except: pass

@bot.command(name="خلفية")
@commands.has_permissions(administrator=True)
async def set_bg(ctx):
    if roulette_config["settings_channel_id"] and ctx.channel.id != roulette_config["settings_channel_id"]: return
    await ctx.send("أرسل رابط عجلة الروليت الجديدة:")
    try:
        msg = await bot.wait_for('message', check=lambda m: m.author == ctx.author, timeout=30.0)
        if msg.content.strip().startswith("http"):
            roulette_config["bg_url"] = msg.content.strip()
            await ctx.send("تم تحديث العجلة.")
    except: pass

# ====================================================================
# 🔘 واجهة أزرار التسجيل (تم إصلاح صياغة الإيموجيات برمجياً لمنع الكراش نهائياً)
# ====================================================================
class RegistrationView(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=roulette_config["signup_time"])
        self.ctx = ctx
        self.players = [ctx.author]

    @discord.ui.button(label="دخول", emoji=discord.PartialEmoji(name="📥"), style=discord.ButtonStyle.secondary)
    async def join_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user in self.players: 
            return await interaction.response.send_message("أنت منضم للعبة بالفعل", ephemeral=True)
        if len(self.players) >= roulette_config["max_players"]: 
            return await interaction.response.send_message("الروليت ممتلئة بالكامل حالياً", ephemeral=True)
        self.players.append(interaction.user)
        await interaction.response.send_message(f"تم انضمامك بنجاح للروليت ✅", ephemeral=True)
        mentions_str = " | ".join([p.mention for p in self.players])
        await interaction.message.edit(content=f"تم فتح باب التسجيل في الروليت\n\nالمتضمين حالياً ({len(self.players)}/{roulette_config['max_players']}):\n{mentions_str}", view=self)

    @discord.ui.button(label="متجر الخصائص", emoji=discord.PartialEmoji(name="🎭"), style=discord.ButtonStyle.secondary)
    async def features_shop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🛒 متجر الخصائص مغلق مؤقتاً أثناء إعداد الجولة.", ephemeral=True)

    @discord.ui.button(label="متجر الصور", emoji=discord.PartialEmoji(name="🖼️"), style=discord.ButtonStyle.secondary)
    async def image_shop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🖼️ متجر خلفيات العجلة والصور الشخصية قيد الصيانة.", ephemeral=True)

    @discord.ui.button(label="الحقيبة", emoji=discord.PartialEmoji(name="🎒"), style=discord.ButtonStyle.secondary)
    async def bag_button(self, interaction: discord.Interaction, button: discord.ui.Button): 
        await interaction.response.send_message("🎒 حقيبتك فارغة، لا تملك خصائص حماية أو إنعاش حالياً.", ephemeral=True)

    @discord.ui.button(label="الاحصائيات", emoji=discord.PartialEmoji(name="📊"), style=discord.ButtonStyle.secondary)
    async def stats_button(self, interaction: discord.Interaction, button: discord.ui.Button): 
        await interaction.response.send_message("📊 نظام الروليت متصل ويعمل بكفاءة 100% دون أخطاء.", ephemeral=True)

# ====================================================================
# 🔘 واجهة أزرار التحكم بالجولات والإقصاء
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
        for i, player in enumerate(self.players[:12], start=1):
            btn = discord.ui.Button(label=f"{i} {player.display_name[:12]}", style=discord.ButtonStyle.secondary, custom_id=f"p_{player.id}")
            btn.callback = self.button_callback
            self.add_item(btn)
            
        btn_revive = discord.ui.Button(label="انعاش", emoji=discord.PartialEmoji(name="🩺"), style=discord.ButtonStyle.secondary, custom_id="action_revive")
        btn_revive.callback = self.button_callback
        self.add_item(btn_revive)

        btn_rand = discord.ui.Button(label="عشوائي", emoji=discord.PartialEmoji(name="🔀"), style=discord.ButtonStyle.secondary, custom_id="action_random")
        btn_rand.callback = self.button_callback
        self.add_item(btn_rand)

        if roulette_config["bomb_enabled"]:
            btn_bomb = discord.ui.Button(label="قنبلة", emoji=discord.PartialEmoji(name="💣"), style=discord.ButtonStyle.secondary, custom_id="action_bomb")
            btn_bomb.callback = self.button_callback
            self.add_item(btn_bomb)

        btn_leave = discord.ui.Button(label="انسحاب", emoji=discord.PartialEmoji(name="🚪"), style=discord.ButtonStyle.secondary, custom_id="action_leave")
        btn_leave.callback = self.button_callback
        self.add_item(btn_leave)

    async def button_callback(self, interaction: discord.Interaction):
        if self.allowed_role not in interaction.user.roles: 
            return await interaction.response.send_message("لا تملك الصلاحية للتحكم بالجولة ❌", ephemeral=True)
        
        custom_id = interaction.data['custom_id']
        if custom_id == "action_random":
            self.voted_out = random.choice(self.players); self.action_type = "random"
        elif custom_id == "action_bomb":
            self.action_type = "bomb"; self.voted_out = random.sample(self.players, min(2, len(self.players)))
        elif custom_id == "action_leave":
            self.voted_out = interaction.user; self.action_type = "leave"
        elif custom_id == "action_revive":
            self.action_type = "revive"; self.voted_out = interaction.user
        elif custom_id.startswith("p_"):
            p_id = int(custom_id.split("_")[1])
            self.voted_out = next((p for p in self.players if p.id == p_id), None); self.action_type = "normal"
            
        self.stop()

# ====================================================================
# 🚀 محرك جولات الفعالية
# ====================================================================
@bot.command(name="روليت")
async def start_roulette(ctx, role: discord.Role = None):
    if role is None or role not in ctx.author.roles: 
        return await ctx.send("يرجى تحديد رتبة التحكم وتأكد أنك تمتلكها! مثال: `-روليت @منظم`")
        
    # التحقق: اللعبة لا تبدأ إلا في الشات العام المحدد عبر أمر (-رومات)
    if roulette_config["allowed_channels"] and ctx.channel.id not in roulette_config["allowed_channels"]: 
        allowed_mentions = ", ".join([f"<#{c_id}>" for c_id in roulette_config["allowed_channels"]])
        return await ctx.send(f"❌ أمر اللعب غير مسموح هنا! يرجى التوجه للشات العام المخصص للعب: {allowed_mentions}", delete_after=7)

    wheel_bytes = await download_image(roulette_config["bg_url"])
    init_content = f"تم فتح باب التسجيل في الروليت\n\nالمتضمين حالياً (1/{roulette_config['max_players']}):\n• {ctx.author.mention}"
    view = RegistrationView(ctx)
    file = discord.File(io.BytesIO(wheel_bytes), filename="wheel.gif") if wheel_bytes else None
    await ctx.send(content=init_content, view=view, file=file)
    
    await asyncio.sleep(roulette_config["signup_time"])
    view.stop()
    
    players = view.players
    if len(players) < 2: return await ctx.send("تم إلغاء الروليت لعدم دخول العدد الكافي من اللاعبين.")
    await ctx.send("بدأت الجولة الآن 🏁"); await asyncio.sleep(2)

    while len(players) > 1:
        p_list = " | ".join([p.mention for p in players])
        round_content = f"**جاري سحب الضحية**\nاللاعبين المتبقين في الجولة:\n{p_list}\n\nلديك 15 ثانية لاختيار لاعب لطردة 👇"
        game_view = GamePlayView(ctx, players, role)
        file = discord.File(io.BytesIO(wheel_bytes), filename="wheel.gif") if wheel_bytes else None
        await ctx.send(content=round_content, view=game_view, file=file)
        
        await asyncio.sleep(15); game_view.stop()
        
        if not game_view.voted_out:
            victim = random.choice(players); players.remove(victim)
            await ctx.send(roulette_config["msg_timeout"].format(victim=victim.mention))
            await asyncio.sleep(4); continue
            
        if game_view.action_type == "bomb":
            victims = game_view.voted_out
            for v in victims:
                if v in players: players.remove(v)
            v_mentions = " و ".join([v.mention for v in victims])
            await ctx.send(f"💥 تم استخدام القنبله وطرد {v_mentions} .")
        elif game_view.action_type == "revive":
            victim = game_view.voted_out
            await ctx.send(f"💊 {victim.mention} , تم انعاشه سيتم بدء الجولة القادمة خلال ثواني .")
        else:
            victim = game_view.voted_out
            chance = random.random()
            
            if roulette_config["features_enabled"] and chance < roulette_config["protection_chance"] and len(players) > 2:
                await ctx.send(f"🛡️ لم يتم طرد {victim.mention} بسبب الحماية , سوف تبدأ الجولة القادمة خلال ثواني .")
            elif roulette_config["features_enabled"] and chance > roulette_config["protection_chance"] and chance < (roulette_config["protection_chance"] + roulette_config["counter_chance"]) and len(players) > 2:
                attacker = ctx.author
                if attacker in players: players.remove(attacker)
                await ctx.send(f"⏳ تم طرد {attacker.mention} بسبب الهجمة المرتده من قبل {victim.mention} , سوف تبدأ الجولة القادمة خلال ثواني .")
            else:
                if victim in players: players.remove(victim)
                if game_view.action_type == "random":
                    await ctx.send(roulette_config["msg_random"].format(victim=victim.mention))
                else:
                    await ctx.send(roulette_config["msg_normal"].format(victim=victim.mention))
                    
        await asyncio.sleep(4)
        
    if len(players) == 1:
        winner = players[0]
        await ctx.send(f"🏆 {winner.mention} @here")
        avatar_url = winner.display_avatar.with_format("png").url
        winner_img_stream = await generate_winner_image(avatar_url, winner.display_name)
        if winner_img_stream:
            await ctx.send(file=discord.File(winner_img_stream, filename="winner.png"))

@bot.event
async def on_command_error(ctx, error):
    print(f"❌ خطأ داخلي: {error}")

bot.run(os.getenv("DISCORD_TOKEN"))
