import discord
from discord import app_commands
from discord.ext import commands
import random
import asyncio
import os  # سطر مهم جداً لسحب التوكن من السيرفر

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=discord.Intents.all())
    
    async def setup_hook(self):
        # مزامنة أوامر السلاش تلقائياً
        await self.tree.sync()
        print("تمت مزامنة أوامر السلاش بنجاح!")

bot = MyBot()

# قواعد بيانات مؤقتة في الذاكرة
server_settings = {}  
bank_data = {}        
roulette_games = {}   

# دالة للتحقق من صلاحية الشات والرول
def is_allowed(interaction: discord.Interaction):
    guild_id = interaction.guild_id
    if not guild_id:
        return False
    
    if guild_id not in server_settings:
        return True
        
    settings = server_settings[guild_id]
    
    # تحقق من الروم
    if settings.get('channels') and interaction.channel_id not in settings['channels']:
        return False
        
    # تحقق من الرول
    if interaction.user.guild_permissions.administrator:
        return True
        
    if settings.get('roles'):
        user_roles = [role.id for role in interaction.user.roles]
        if not any(role_id in user_roles for role_id in settings['roles']):
            return False
            
    return True

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    print("البوت شغال ومتصل ب ديسكورد بنجاح!")

# ==================== أوامر التحكم والبرمجة داخل السيرفر ====================

@bot.tree.command(name="تفعيل_شات", description="تحديد الشات المسموح بلعب الروليت واستخدام البنك فيها")
@app_commands.describe(الشات="الشات المراد تفعيل البوت فيها")
@app_commands.checks.has_permissions(administrator=True)
async def setup_channel(interaction: discord.Interaction, الشات: discord.TextChannel):
    guild_id = interaction.guild_id
    if guild_id not in server_settings:
        server_settings[guild_id] = {'channels': [], 'roles': [], 'difficulty': 'سهل'}
    
    if الشات.id not in server_settings[guild_id]['channels']:
        server_settings[guild_id]['channels'].append(الشات.id)
    
    await interaction.response.send_message(f"✅ تم تفعيل البوت في روم: {الشات.mention}", ephemeral=True)

@bot.tree.command(name="تفعيل_رول", description="تحديد الرول المسموح له باستخدام أوامر البوت والفعالية")
@app_commands.describe(الرول="الرول المسموح له باللعب")
@app_commands.checks.has_permissions(administrator=True)
async def setup_role(interaction: discord.Interaction, الرول: discord.Role):
    guild_id = interaction.guild_id
    if guild_id not in server_settings:
        server_settings[guild_id] = {'channels': [], 'roles': [], 'difficulty': 'سهل'}
    
    if الرول.id not in server_settings[guild_id]['roles']:
        server_settings[guild_id]['roles'].append(الرول.id)
        
    await interaction.response.send_message(f"✅ تم السماح لرول: {الرول.name} باستخدام البوت.", ephemeral=True)

@bot.tree.command(name="صعوبة_البنك", description="تعديل صعوبة الحصول على الفلوس في البنك")
@app_commands.choices(الصعوبة=[
    app_commands.Choice(name="سهل (أرباح عالية)", value="سهل"),
    app_commands.Choice(name="متوسط", value="متوسط"),
    app_commands.Choice(name="صعب (تحدي قوي)", value="صعب")
])
@app_commands.checks.has_permissions(administrator=True)
async def set_difficulty(interaction: discord.Interaction, الصعوبة: app_commands.Choice[str]):
    guild_id = interaction.guild_id
    if guild_id not in server_settings:
        server_settings[guild_id] = {'channels': [], 'roles': [], 'difficulty': 'سهل'}
        
    server_settings[guild_id]['difficulty'] = الصعوبة.value
    await interaction.response.send_message(f"⚙️ تم تغيير صعوبة البنك إلى: **{الصعوبة.name}**", ephemeral=True)


# ==================== نظام الروليت ====================

@bot.tree.command(name="روليت_انشاء", description="بدء جيم روليت روسي جديد في السيرفر")
@app_commands.describe(الحد_الاقصى="أكبر عدد مسموح له بالدخول", عند_كم_تبدأ="تبدأ اللعبة تلقائياً عند وصول هذا العدد")
async def create_roulette(interaction: discord.Interaction, الحد_الاقصى: int = 10, عند_كم_تبدأ: int = 4):
    if not is_allowed(interaction):
        return await interaction.response.send_message("❌ هذا الشات أو الرول غير مسموح له باستخدام البوت حالياً!", ephemeral=True)
        
    channel_id = interaction.channel_id
    if channel_id in roulette_games:
        return await interaction.response.send_message("❌ يوجد جيم روليت شغال حالياً في هذه الشات!", ephemeral=True)
        
    roulette_games[channel_id] = {
        'owner': interaction.user,
        'players': [],
        'max_players': الحد_الاقصى,
        'min_start': عند_كم_تبدأ,
        'status': 'انتظار',
        'mode': 'عادي' 
    }
    
    embed = discord.Embed(title="🎯 روليت الفعاليات الجديد!", description=f"قام {interaction.user.mention} بإنشاء قيم روليت حماسي!\n\n**الحد الأقصى:** {الحد_الاقصى} لاعبين\n**تبدأ عند:** {عند_كم_تبدأ} لاعبين\n\nللدخول اكتب الأمر: `/روليت_دخول`", color=discord.Color.blurple())
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="روليت_عكسي", description="تحويل نظام الروليت الحالي لعكسي")
async def toggle_roulette_mode(interaction: discord.Interaction):
    if not is_allowed(interaction): return
    channel_id = interaction.channel_id
    if channel_id not in roulette_games:
        return await interaction.response.send_message("❌ لا يوجد قيم روليت شغال لتعديله!", ephemeral=True)
        
    game = roulette_games[channel_id]
    if game['owner'] != interaction.user and not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("❌ فقط صاحب الجيم أو الإدارة يقدر يغير النمط!", ephemeral=True)
        
    game['mode'] = 'عكسي' if game['mode'] == 'عادي' else 'عادي'
    await interaction.response.send_message(f"🔄 تم تحويل نمط الروليت إلى: **{ 'العكسي (اللي تجي عليه يفوز ويرتاح)' if game['mode'] == 'عكسي' else 'العادي (اللي تجي عليه يطرد)' }**!")

@bot.tree.command(name="روليت_دخول", description="تسجيل دخول مجاني في قيم الروليت الحالي")
async def join_roulette(interaction: discord.Interaction):
    if not is_allowed(interaction): return
    channel_id = interaction.channel_id
    if channel_id not in roulette_games or roulette_games[channel_id]['status'] != 'انتظار':
        return await interaction.response.send_message("❌ لا يوجد قيم روليت مفتوح للتسجيل حالياً!", ephemeral=True)
        
    game = roulette_games[channel_id]
    if interaction.user in game['players']:
        return await interaction.response.send_message("❌ أنت مسجل في اللعبة بالفعل!", ephemeral=True)
        
    if len(game['players']) >= game['max_players']:
        return await interaction.response.send_message("❌ اللعبة ممتلئة بالكامل حالياً!", ephemeral=True)
        
    game['players'].append(interaction.user)
    current_count = len(game['players'])
    
    await interaction.response.send_message(f"✅ {interaction.user.mention} دخل الروليت! عدد اللاعبين الحاليين ({current_count}/{game['max_players']})")
    
    if current_count >= game['min_start'] and game['status'] == 'انتظار':
        game['status'] = 'شغال'
        await start_roulette_logic(interaction.channel, game)

async def start_roulette_logic(channel, game):
    await channel.send("🔥 **اكتمل العدد المطلوب! بدأت الروليت تدور الآن... قمط الـكل!**")
    await asyncio.sleep(2)
    
    players = game['players'].copy()
    mode = game['mode']
    
    while len(players) > 1:
        await channel.send(f"🔄 الروليت تدور بين اللاعبين المتبقين ({len(players)})...")
        await asyncio.sleep(3)
        
        chosen = random.choice(players)
        players.remove(chosen)
        
        if mode == 'عادي':
            await channel.send(f"💥 **بـوووم!** الروليت جت على {chosen.mention}! **[تم طرده من اللعبة]** 💀")
        else:
            await channel.send(f"✨ **يا حظك!** الروليت جت على {chosen.mention}! **[نجا وفاز وعاش بره الحسبة]** 🎉")
            
        await asyncio.sleep(2)
        
    winner = players[0]
    embed = discord.Embed(title="🏆 نهاية الروليت 🏆", description=f"الناجي الأخير والفائز القادح في هذا الجيم هو:\n👑 {winner.mention} 👑\n\nمبرووووك!", color=discord.Color.gold())
    await channel.send(embed=embed)
    
    if channel.id in roulette_games:
        del roulette_games[channel.id]


# ==================== نظام البنك والاقتصاد ====================

def get_bank(user_id):
    if user_id not in bank_data:
        bank_data[user_id] = {'cash': 500, 'bank': 0}
    return bank_data[user_id]

@bot.tree.command(name="راتب", description="استلام الراتب اليومي حقك")
async def daily_salary(interaction: discord.Interaction):
    if not is_allowed(interaction): return
    user_id = interaction.user.id
    guild_id = interaction.guild_id
    
    difficulty = server_settings.get(guild_id, {}).get('difficulty', 'سهل')
    if difficulty == 'سهل':
        amount = random.randint(1000, 2000)
    elif difficulty == 'متوسط':
        amount = random.randint(500, 1000)
    else:
        amount = random.randint(100, 400)
        
    account = get_bank(user_id)
    account['cash'] += amount
    
    await interaction.response.send_message(f"💰 | {interaction.user.mention} استلمت راتبك بنجاح قيمته: **${amount}** كاش! (نمط الصعوبة: {difficulty})")

@bot.tree.command(name="بنك", description="رؤية رصيدك الحالي في الكاش والبنك")
async def check_balance(interaction: discord.Interaction):
    if not is_allowed(interaction): return
    account = get_bank(interaction.user.id)
    
    embed = discord.Embed(title=f"💳 محفظة {interaction.user.name}", color=discord.Color.green())
    embed.add_field(name="💵 كاش في مخباك:", value=f"${account['cash']}", inline=False)
    embed.add_field(name="🏦 رصيدك بالبنك:", value=f"${account['bank']}", inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="ايداع", description="حفظ الكاش حقك داخل البنك")
async def deposit(interaction: discord.Interaction, المبلغ: int):
    if not is_allowed(interaction): return
    account = get_bank(interaction.user.id)
    if المبلغ <= 0 or account['cash'] < المبلغ:
        return await interaction.response.send_message("❌ ما عندك هذا المبلغ كاش لتودعه!", ephemeral=True)
        
    account['cash'] -= المبلغ
    account['bank'] += المبلغ
    await interaction.response.send_message(f"🏦 تم إيداع **${المبلغ}** في حسابك البنكي بنجاح!")

# الكود يسحب التوكن السري تلقائياً من إعدادات السيرفر البنفسجية
bot.run(os.getenv("DISCORD_TOKEN"))
