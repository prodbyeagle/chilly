import datetime
import functools
import json
import asyncio
import locale
import os
import string
import requests
import random
import time
import re
import nextcord
from nextcord import Member
from nextcord.ext import commands
from nextcord.ui import View
from typing import List

intents = nextcord.Intents.all()
intents.typing = True
intents.presences = True
bot = commands.Bot(command_prefix='!', intents=intents)

TOKEN = "DISCORD TOKEN"

GUILD_ID =                # Server ID
CHANNEL_ID =              # Channel ID
DEBUG_CHANNEL_ID =        # Debugging Channel ID
BANS_CHANNEL_ID =         # Ban Logs Channel ID
log_channel_id =          # Command Logs Server ID
APPEAL_CHANNEL_ID =       # Unban Appeal Channel ID
UPDATE_CHANNEL_ID =       # Update Blog Channel ID
ANNOUNCEMENT_CHANNEL_ID = # Announcements Channel ID
WELCOME_CHANNEL_ID =      # Welcome Channel ID
afk_channel_id =          # Afk Voice Call
staff_role_id =           # Staff Role ID (Admin, Mod, ...)

DEBUG_MODE = False
update_active = False
pic_link = 'https://yt3.ggpht.com/k8l2-DSZPRrM0jFGkdh9icXdI_WN-Fc4Ic3LICmeplAklpv32ouQ4zCXoN66zmofNmMYqbYaDA=s88-c-k-c0x00ffffff-no-rj-mo'
RPC_DEFAULT_STATE = '✅ | Online! | 🦅'
RPC_UPDATE_STATE = '⚙️ | Updating.. | 🦅'
CONFIG_FILE = 'chilly_config.json'
MUTED_DATA_FILE = 'chilly_muteddata.json'
REPORTS_FILE = 'chilly_reportdata.json'
COOWNER_ID = # Co. Owner ID falls gibt
OWNER_ID = # OWNER ID
api_key = # Get the api key here: https://openweathermap.org/api

# ANFANG

# ➖➖➖➖➖➖➖➖➖
# 𝓓𝓔𝓕𝓘𝓝𝓘𝓣𝓘𝓞𝓝𝓢

# Config
def load_config():
    try:
        with open(CONFIG_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
    
def save_config(config):
    with open(CONFIG_FILE, 'w') as file:
        json.dump(config, file, indent=4)

# User Activity
def load_user_activity_data():
    global user_activity_data
    try:
        with open("chilly_minutesinvcdata.json", "r", encoding="utf-8") as file:
            user_activity_data = json.load(file)
    except FileNotFoundError:
        user_activity_data = {}

# Achievements Earned
def load_achievements_earned():
    try:
        with open('chilly_achievementsearned.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
    
def save_achievements_earned(data):
    with open('chilly_achievementsearned.json', 'w') as file:
        json.dump(data, file, indent=4)

# Achievements Names
def load_achievement_names():
    with open('chilly.namesanddescachievements.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data.get('names', []), data.get('descriptions', {})

def save_achievement_names(names, descriptions):
    formatted_descriptions = {name: description if description.startswith('**') and description.endswith('**') else f"**{description}**" for name, description in descriptions.items()}
    data = {
        "names": names,
        "descriptions": formatted_descriptions
    }
    with open('chilly.namesanddescachievements.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4)

# Achievements   
def load_achievements():
    with open("chilly_achievements.json", "r", encoding="utf-8") as achievements_file:
        achievements = json.load(achievements_file)

# Muted Data
def load_muted_data():
    try:
        with open('chilly_muteddata.json', 'r') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        return {}
    
def save_muted_data():
    with open('chilly_muteddata.json', 'w') as file:
        json.dump(muted_members, file)

# Reports
def load_reports():
    try:
        with open(REPORTS_FILE, 'r') as file:
            data = json.load(file)
            if isinstance(data, list):
                return data
            else:
                return []
    except FileNotFoundError:
        return []

def save_reports():
    with open(REPORTS_FILE, 'w') as file:
        json.dump(reports, file, indent=4)

# ➖➖➖➖➖➖➖➖➖

# |\|/|\|\|/|\/|\|/|\/|\|/|\|\|/|\|/|\|\|      

# ➖➖➖➖➖➖➖➖➖
# 𝓑𝓞𝓣 𝓔𝓥𝓔𝓝𝓣𝓢

# Error Event

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, nextcord.ext.commands.CommandNotFound):
        embed = nextcord.Embed(
            title="❌ Error",
            description="Attention! Commands have been converted to Slash Commands. (/achievements)",
            color=nextcord.Color.red()
        )
        message = await ctx.send(embed=embed)
        await asyncio.sleep(10)
        await message.delete()
    elif isinstance(error, nextcord.ext.commands.MissingRequiredArgument):
        embed = nextcord.Embed(
            title="❌ Error",
            description="You did not provide all the required arguments.",
            color=nextcord.Color.red(),
        )
        await ctx.send(embed=embed)
        await asyncio.sleep(2)
        await message.delete()
    else:
        pass


def add_missing_members_to_config(guild, config):
    for member in guild.members:
        if not member.bot:
            user_name = member.name.lower()
            if user_name not in config:
                config[user_name] = {
                    "banned_status": False,
                    "ban_reason": "",
                    "warnings": 0,
                    "trivia_points": 0,
                    "messages_sent": 0,
                    "lvlup_noti": True,
                    "achievement_noti": True,
                    "rob_activated": True,
                    "xp": 0,
                    "money": 0
                }

# Message Event
xp_multiplier = 1  
money_multiplier = 1
multiplier_type = None

async def create_role(guild, role_name, color):
    try:
        role = await guild.create_role(name=role_name, color=color)
        return role
    except nextcord.Forbidden:
        return None

async def send_dm_to_admin(guild, admin_id, content):
    admin = await guild.fetch_member(admin_id)
    if admin:
        try:
            await admin.send(content)
        except nextcord.Forbidden:
            pass

@bot.event
async def on_message(message):
    if message.author == bot.user or message.author.bot or message.guild is None:
        return
    
    user_name = message.author.name.lower()
    chilly_config = load_config()

    if chilly_config is None or not chilly_config:
        return

    if user_name in chilly_config:
        user_data = chilly_config[user_name]
    else:
        user_data = {
            "banned_status": False,
            "ban_reason": "",
            "warnings": 0,
            "trivia_points": 0,
            "messages_sent": 0,
            "lvlup_noti": True,
            "achievement_noti": True,
            "rob_activated": True
        }
        chilly_config[user_name] = user_data

    if 'xp' not in user_data:
        user_data['xp'] = 0
    if 'money' not in user_data:
        user_data['money'] = 0
    if 'messages_sent' not in user_data:
        user_data['messages_sent'] = 0

    xp_earned = 25 * xp_multiplier
    money_earned = 30 * money_multiplier

    user_data['xp'] += xp_earned
    user_data['money'] += money_earned
    user_data['messages_sent'] += 1

    level = 0
    required_xp = 100 + (user_data.get('level', 0) * 100)

    while user_data['xp'] >= required_xp:
        level += 1
        required_xp = 100 + (level * 100)
    if level > user_data.get('level', 0):
        level_up = True
        user_data['level'] = level
        user_data['xp'] = 0
    else:
        level_up = False

    save_config(chilly_config)

    if level_up and user_data.get('xp_notification', True):
        embed = nextcord.Embed(
            title=f"🆙 Congratulations {message.author.name}!",
            description=f"You've reached Level **{level}**!",
            color=nextcord.Color.green()
        )
        embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
        await message.author.send(embed=embed)
    
    try:
        if isinstance(message, nextcord.Message) and not message.author.bot:
            achievements_earned_file = "chilly_achievementsearned.json"
            with open(achievements_earned_file, 'r', encoding='utf-8') as achievements_earned_json:
                achievements_earned = json.load(achievements_earned_json)
            achievements_file = "chilly_achievements.json"

            with open(achievements_file, 'r', encoding='utf-8') as achievements_json:
                achievements = json.load(achievements_json)

            user_name = message.author.name.lower()
            if 'xp' not in user_data:
                user_data['xp'] = 0

            for achievement_name, achievement_data in achievements.items():
                if achievement_name not in achievements_earned.get(user_name, []):
                    criteria = achievement_data.get("criteria", {})
                    message_count = user_data.get('messages_sent', 0)
                    trivia_points = user_data.get('trivia_points', 0)

                    if "message_count" in criteria and criteria["message_count"] <= message_count:
                        achievements_earned.setdefault(user_name, []).append(achievement_name)
                        save_achievements_earned(achievements_earned)

                        achievement_embed = nextcord.Embed(
                            title=f"🎊 ACHIEVEMENT UNLOCKED",
                            description=f"<@{message.author.id}>, you've achieved the `{achievement_data['name']}` ACHIEVEMENT!",
                            color=nextcord.Color.gold()
                        )
                        achievement_embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
                        await message.author.send(embed=achievement_embed)

                        role_name = achievement_data['name']
                        role_color = nextcord.Color(achievement_data.get('color', 0))

                        role = nextcord.utils.get(message.guild.roles, name=role_name)

                        if not role:
                            role = await create_role(message.guild, role_name, role_color)
                            if role:
                                await send_dm_to_admin(message.guild, message.guild.owner_id,
                                    f"A new role '{role_name}' has been created for the achievement '{achievement_name}'.")

                        if role:
                            member = message.author.guild.get_member(message.author.id)
                            await member.add_roles(role)

                    if "trivia_points" in criteria and criteria["trivia_points"] <= trivia_points:
                        achievements_earned[user_name].append(achievement_name)
                        save_achievements_earned(achievements_earned)
                  
                        achievement_embed = nextcord.Embed(
                            title=f"🎊 ACHIEVEMENT UNLOCKED",
                            description=f"<@{message.author.id}>, you've achieved the `{achievement_data['name']}` ACHIEVEMENT!",
                            color=nextcord.Color.gold()
                        )
                        achievement_embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
                        await message.author.send(embed=achievement_embed)
            
                        role_name = achievement_data['name']
                        role_color = nextcord.Color(achievement_data.get('color', 0))
            
                        role = nextcord.utils.get(message.guild.roles, name=role_name)
            
                        if not role:
                            role = await create_role(message.guild, role_name, role_color)
                            if role:
                                await send_dm_to_admin(message.guild, message.guild.owner_id,
                                f"A new role '{role_name}' has been created for the achievement '{achievement_name}'.")
            
                        if role:
                            member = message.author.guild.get_member(message.author.id)
                            await member.add_roles(role)

    except nextcord.errors.HTTPException as e:
        if e.status == 400 and e.code == 50033:
            pass
        else:
            pass

    await bot.process_commands(message)


# On Ready Event

config = load_config()

@bot.event
async def on_ready():
    global xp_multipliers
    print(f'✅ Online as 🌶️  {bot.user.name}')
    print('---------------------------------------------------------')
    await set_rich_presence(RPC_DEFAULT_STATE)
    for guild in bot.guilds:
        add_missing_members_to_config(guild, config)
    save_config(config)

async def set_rich_presence(state):
    activity = nextcord.Activity(type=nextcord.ActivityType.playing, name=state)
    await bot.change_presence(activity=activity)



async def log_to_channel(message, message_link):
    log_channel = bot.get_channel(log_channel_id)
    log_message = f"{message}\n**`Message:`** {message_link}"
    await log_channel.send(log_message)

def get_message_link(ctx):
    return f"https://discord.com/channels/{ctx.guild.id}/{ctx.channel.id}/{ctx.id}"

def log_command(command_name):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(ctx, *args, **kwargs):
            try:
                if ctx.guild is not None:
                    command_author = ctx.user.name
                    timestamp = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
                    message_link = f"https://discord.com/channels/{ctx.guild.id}/{ctx.channel.id}/{ctx.id}"
                    log_message = f"**`[{timestamp}]`**  |  **`{command_name}`**  |  **`{command_author}`**"
                    await log_to_channel(log_message, message_link)
                return await func(ctx, *args, **kwargs)
            except Exception as e:
                await ctx.send(f"❌ An error occurred: {str(e)}", ephemeral=True)
        return wrapper
    return decorator

# Server Join Event

@bot.event
async def on_member_join(member):
    welcome_channel = member.guild.get_channel(WELCOME_CHANNEL_ID)
    if welcome_channel:
        embed = nextcord.Embed(
            title=f'Welcome {member.name} to our server!',
            description='Chill Lounge by @prodbyeagle',
            color=nextcord.Color.green()
        )
        embed.set_thumbnail(url=member.avatar.url)
        embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)
        await welcome_channel.send(embed=embed)


# Server Leave Event

@bot.event
async def on_member_remove(member):
    goodbye_channel = member.guild.get_channel(WELCOME_CHANNEL_ID)
    if goodbye_channel:
        embed = nextcord.Embed(
            title=f'Goodbye, {member.name}!',
            color=nextcord.Color.red()
        )
        embed.set_thumbnail(url=member.avatar.url)
        embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)
        await goodbye_channel.send(embed=embed)

# VC Event

user_activity_data = {}

@bot.event
async def on_voice_state_update(member, before, after):
    user_name = str(member.name)

    has_andi_role = any(role.name == "🐂 Andi" for role in member.roles)
    has_noah_role = any(role.name == "🦅 Eagle" for role in member.roles)

    if before.channel != after.channel and after.channel is not None and not (has_noah_role or has_andi_role):
        if not has_noah_role:
            await handle_achievement(member, achievement_name="user_id_meeting_owner")
        if not has_andi_role:
            await handle_achievement(member, achievement_name="user_id_meeting_coowner")

        if before.channel != after.channel:
            if after.channel is not None:
                user_activity_data.setdefault(user_name, {}).setdefault('vc_start_time', time.time())
                print(f"{member.display_name} joined the Voice-Channel {after.channel.name}.")
    
            if before.channel is not None:
                if user_name in user_activity_data and 'vc_start_time' in user_activity_data[user_name]:
                    vc_start_time = user_activity_data[user_name]['vc_start_time']
                    vc_minutes = user_activity_data[user_name].get('vc_minutes', 0)
                    
                    if before.channel.id != afk_channel_id:
                        vc_minutes += int(time.time() - vc_start_time) // 60
                        user_activity_data[user_name]['vc_minutes'] = vc_minutes
                        del user_activity_data[user_name]['vc_start_time']
                        print(f"{member.display_name} left the Voice-Channel {before.channel.name} and spent a total of {vc_minutes} minutes.")
            
                        with open("chilly_minutesinvcdata.json", "w") as file:
                            json.dump(user_activity_data, file, indent=4)
    
        if after.channel and after.channel.id == afk_channel_id:
            if staff_role_id in [role.id for role in member.roles]:
        
                if before.channel:
                    await member.move_to(before.channel)
                    print(f"Moved {member.name} back to: {before.channel.name} | ADMIN POWER | :eagle:")
                
async def handle_achievement(member, achievement_name):
    with open('chilly_achievementsearned.json', 'r') as earned_file:
        achievements_earned = json.load(earned_file)

    if str(member.name) not in achievements_earned:
        achievements_earned[str(member.name)] = []

    if achievement_name not in achievements_earned[str(member.name)]:
        achievements_earned[str(member.name)].append(achievement_name)

        with open('chilly_achievementsearned.json', 'w') as earned_file:
            json.dump(achievements_earned, earned_file, indent=4)

            achievement_data = load_achievements[achievement_name]

            achievement_embed = nextcord.Embed(
                title=f"🎊 ACHIEVEMENT UNLOCKED ",
                description=f"<@{member.name}>, you've achieved the `{achievement_data['name']}` ACHIEVEMENT!",
                color=nextcord.Color.gold()
            )
            achievement_embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)

            await member.send(embed=achievement_embed)

            role_name = achievement_data['name']
            role = nextcord.utils.get(member.guild.roles, name=role_name)
            if member is not None:
                await member.add_roles(role)
            else:
                print("Member is None.")

# ➖➖➖➖➖➖➖➖➖

# |\|/|\|\|/|\/|\|/|\/|\|/|\|\|/|\|/|\|\|             

# ➖➖➖➖➖➖➖➖➖
# 𝓐𝓓𝓜𝓘𝓝 𝓒𝓞𝓜𝓜𝓐𝓝𝓓𝓢

# ✅ /addachievement

@bot.slash_command(
    name='addachievement',
    description='ADMIN ONLY! | Adds an achievement.'
)
@log_command('addachievement')
async def add_achievement(ctx, emoji: str, name: str, description: str):
    try:        
        if ctx.guild is None:
            embed = nextcord.Embed(
                title="⛔ Command Error",
                description="This command can only be used in Chill Lounge text channels.",
                color=0xFF5733
            )
            await ctx.send(embed=embed, ephemeral=True)
            return
                       
        allowed_roles = ['⚙️ Developer']

        user_roles = [role.name for role in ctx.user.roles]
        if any(role_name in allowed_roles for role_name in user_roles):
            achievement_names, achievement_descriptions = load_achievements()

            if name in achievement_names:
                embed = nextcord.Embed(
                    title=f'⚠️ STOP!',
                    description=f'The **Achievement** {emoji} **{name}** already exists.',
                    color=nextcord.Color.yellow()
                )
                await ctx.send(embed=embed, ephemeral=True)
            else:
                achievement_names.append(f"{emoji} {name}")
                achievement_descriptions[f"{emoji} {name}"] = f"**{description}**"
                save_achievement_names(achievement_names, achievement_descriptions)

                role_name = f"{emoji} {name}"
                role = await ctx.guild.create_role(name=role_name)

                await ctx.user.add_roles(role)

                embed = nextcord.Embed(
                    title=f'✅ Successfully Created!',
                    description=f'Achievement {emoji} **{name}** has been **created.**',
                    color=nextcord.Color.green()
                )
                await ctx.send(embed=embed, ephemeral=True)
        else:
            error_embed = nextcord.Embed(
                title="❌ Error",
                description="You don't have permission to use this command.",
                color=nextcord.Color.red()
            )
            await ctx.send(embed=error_embed, ephemeral=True)
    except Exception as e:
        await ctx.send(f"❌ An error occurred: **{str(e)}**")

# ✅ /announcement

@bot.slash_command(
    name='announcement',
    description='ADMIN ONLY! | Sends an announcement to a specific channel.'
)
@log_command('announcement')
async def announcement(ctx, message: str):
    try:
        if ctx.guild is None:
            embed = nextcord.Embed(
                title="⛔ Command Error",
                description="This command can only be used in Chill Lounge text channels.",
                color=0xFF5733
            )
            await ctx.send(embed=embed, ephemeral=True)
            return

        allowed_roles = ['⚙️ Developer']

        if any(role.name in allowed_roles for role in ctx.user.roles):
            guild = ctx.guild
            announcement_channel = guild.get_channel(ANNOUNCEMENT_CHANNEL_ID)

            if announcement_channel is None:
                announcement_error = nextcord.Embed(
                    title="❌ Error",
                    description="Announcement channel not found! The channel must be in the same server.",
                    color=nextcord.Color.red()
                )
                await ctx.send(embed=announcement_error, ephemeral=True)
            else:
                embed = nextcord.Embed(title="⚠️ Server Announcement", description=message, color=nextcord.Color.yellow())
                embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)
                await announcement_channel.send(embed=embed)
                await ctx.send("✅ Server announcement sent!", ephemeral=True)

        else:
            error_embed = nextcord.Embed(
                title="❌ Error",
                description="You do not have permission for this command.",
                color=nextcord.Color.red()
            )
            await ctx.send(embed=error_embed, ephemeral=True)

    except Exception as e:
        await ctx.send(f"❌ An error occurred: {str(e)}", ephemeral=True)

# ✅ /ban

@bot.slash_command(
    name='ban',
    description='Ban a user'
)
@log_command('ban')
async def ban(ctx, user: nextcord.User, *, reason: str = "No Reason!"):
    try:
        if ctx.guild is None:
            embed = nextcord.Embed(
                title="⛔ Command Error",
                description="This command can only be used in Chill Lounge text channels.",
                color=0xFF5733
            )
            await ctx.send(embed=embed, ephemeral=True)
            return
           
                       
        global config
        allowed_roles = ['⚙️ Developer']

        if any(role.name in allowed_roles for role in ctx.user.roles):
            user_name = user.name.lower()
            if user_name in config:
                if config[user_name]['banned_status']:
                    warning_embed = nextcord.Embed(title="⚠️ Warning", description="Player is already banned!", color=nextcord.Color.yellow())
                    await ctx.send(embed=warning_embed, ephemeral=True)
                else:
                    config[user_name]['banned_status'] = True
                    config[user_name]['ban_reason'] = reason
                    save_config(config)

                    embed = nextcord.Embed(title="🔒 You have been banned!", color=nextcord.Color.red())
                    embed.add_field(name="👤 User", value=user.mention)
                    embed.add_field(name="ℹ️ Status", value="Banned")
                    embed.add_field(name="🗯️ Reason", value=reason)
                    embed.set_footer(text="DM the Admins if you got No Reason! Maybe they can help you!| Made by @prodbyeagle", icon_url=pic_link)

                    await user.send(embed=embed)
                    bans_channel = bot.get_channel(BANS_CHANNEL_ID)
                    if bans_channel:
                        await bans_channel.send(embed=embed)

                    confirmation_embed = nextcord.Embed(description="🔒 Player banned!", color=nextcord.Color.red())
                    confirmation_msg = await ctx.send(embed=confirmation_embed)
                    await asyncio.sleep(2)
                    await confirmation_msg.delete()
            else:
                await ctx.send(f"⚠️ {user.name} is not registered.")
        else:
            error_embed = nextcord.Embed(
                title="❌ ERROR",
                description="HAHA doesn't work. Only Chilly Devs.",
                color=nextcord.Color.red()
            )
            await ctx.send(embed=error_embed, ephemeral=True)
    except Exception as e:
        await ctx.send(f"❌ An error occurred: {str(e)}")

# ✅ /clearchannel

class ConfirmationView(View):
    def __init__(self):
        super().__init__()
        
    @nextcord.ui.button(label="`‼️ Im 100% Confident`", style=nextcord.ButtonStyle.red)
    async def confirm(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.send_message(
            content="`**♻️ Deletion Started!**`",
            ephemeral=True
        )
        channel = interaction.channel
        await channel.purge()
        await asyncio.sleep(5)
        
        embed = nextcord.Embed(
            title="`🚮 Channel Cleared!`",
            description="`All messages in this channel have been cleared.`",
            color=nextcord.Color.blue()
        )
        
        confirmation_message = await channel.send(embed=embed)
        
        await asyncio.sleep(3)
        
        await confirmation_message.delete()

    @nextcord.ui.button(label="😑 Nevermind.", style=nextcord.ButtonStyle.green)
    async def cancel(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.send_message("`⛔ Deletion Stopped! Takes 1 Minute to Delete All Messages`", ephemeral=True)

blacklisted_channels = [893762440196677646, 1112296580431757392, 1149028692916453456,]

@bot.slash_command(
    name='clearchannel',
    description='ADMIN ONLY! | Deletes all messages in this channel.'
)
@log_command('clearchannel')
async def clearchannel_command(ctx):
    try:
        if ctx.guild is None:
            embed = nextcord.Embed(
                title="`⛔ Command Error`",
                description="`This command can only be used in Chill Lounge text channels.`",
                color=0xFF5733
            )
            await ctx.send(embed=embed, ephemeral=True)
            return

        allowed_roles = ['⚙️ Developer']

        if any(role.name in allowed_roles for role in ctx.user.roles):
            if isinstance(ctx.channel, nextcord.TextChannel):
                if ctx.channel.id not in blacklisted_channels:
                    view = ConfirmationView()
                    embed = nextcord.Embed(
                        title="`⚠️ Clear Channel Confirmation`",
                        description="`⁉️ Are you sure you want to delete ALL messages in this channel?`",
                        color=0xFF5733
                    )
                    await ctx.send(embed=embed, view=view, ephemeral=True)
                else:
                    blacklist_embed = nextcord.Embed(
                        title="`⛔ BLACKLISTED`",
                        description="`This channel cannot be cleared.`",
                        color=0xFF5733
                    )
                    await ctx.send(embed=blacklist_embed, ephemeral=True)
            else:
                embed = nextcord.Embed(
                    title="`⛔ Command Error`",
                    description="`This command can only be used in Chill Lounge text channels.`",
                    color=0xFF5733
                )
                await ctx.send(embed=embed, ephemeral=True)
        else:
            error_embed = nextcord.Embed(
                title="`❌ Error`",
                description="`You do not have permission for this command.`",
                color=nextcord.Color.red()
            )
            await ctx.send(embed=error_embed, ephemeral=True)

    except Exception as e:
        embed = nextcord.Embed(
            title="`❌ ERROR DM @prodbyeagle`",
            description=f"`An error occurred: {str(e)}`",
            color=0xFF5733
        )
        await ctx.send(embed=embed, ephemeral=True)

# ✅ /debug

@bot.slash_command(
    name='debug',
    description='ADMIN ONLY! | Toggle debug mode.'
)
@log_command('debug')
async def debug(ctx):
    try:
        if ctx.guild is None:
            embed = nextcord.Embed(
                title="⛔ Command Error",
                description="This command can only be used in Chill Lounge text channels.",
                color=0xFF5733
            )
            await ctx.send(embed=embed, ephemeral=True)
            return

        allowed_roles = ['⚙️ Developer']

        if any(role.name in allowed_roles for role in ctx.user.roles):
            global DEBUG_MODE
            DEBUG_MODE = not DEBUG_MODE
            await ctx.send(f"Debug mode is now {'enabled ✅' if DEBUG_MODE else 'disabled ❌'}.")

            if DEBUG_MODE:
                await ctx.send("🌶️ **Currently, nothing is associated with the Debug mode!**")
        else:
            error_embed = nextcord.Embed(
                title="❌ Error",
                description="You do not have permission for this command.",
                color=nextcord.Color.red()
            )
            await ctx.send(embed=error_embed, ephemeral=True)

    except Exception as e:
        await ctx.send(f"❌ An error occurred: {str(e)}")

# ✅ /event

allowed_role_name = "⚙️ Developer"

event_multiplier = 1.0
event_duration_seconds = 3600

def parse_duration(duration_str):
    match = re.match(r'(\d+)([smh])', duration_str)
    if match:
        value = int(match.group(1))
        unit = match.group(2)
        if unit == 's':
            return value
        elif unit == 'm':
            return value * 60
        elif unit == 'h':
            return value * 3600
    return None

async def event_expired_notification(ctx):
    await asyncio.sleep(event_duration_seconds)

    global xp_multiplier, money_multiplier
    xp_multiplier = 1.0  
    money_multiplier = 1.0

    embed = nextcord.Embed(
        title="Event abgelaufen",
        description="**Das Event ist abgelaufen!**",
        color=nextcord.Color.red()
    )

    await ctx.send(embed=embed)

@bot.slash_command(
    name='event',
    description='ADMIN ONLY! | Start an Event'
)
@log_command('event')
async def set_event(ctx, multipliertype: str, multiplier: float, duration: str):
    global xp_multiplier, money_multiplier, event_duration_seconds, multiplier_type

    user = ctx.user
    allowed_role = nextcord.utils.get(user.roles, name=allowed_role_name)

    if allowed_role:

        parsed_duration = parse_duration(duration)

        if parsed_duration is not None:
            multipliertype = multipliertype.lower()

            if multipliertype == 'xp':
                xp_multiplier = multiplier
                money_multiplier = 1.0
            elif multipliertype == 'money':
                money_multiplier = multiplier
                xp_multiplier = 1.0
            else:
                await ctx.send("Invalid multiplier type. Use 'xp' or 'money'.")
                return

            event_duration_seconds = parsed_duration

            embed_event = nextcord.Embed(
                title="Event",
                description=f"**▪︎ Multiplier Type:** **`{multipliertype}`**\n **▪︎ Multiplier:** **`{multiplier}x`**\n **▪︎ Duration:** **`{parsed_duration} seconds`**",
                color=nextcord.Color.green()
            )
            await ctx.send(embed=embed_event)

            bot.loop.create_task(event_expired_notification(ctx))
    else:
        error_embed = nextcord.Embed(
            title="❌ ERROR",
            description="**You don't have permisson to use this command!**",
            color=nextcord.Color.red()
            )
        await ctx.send(embed=error_embed, ephemeral=True)

# ✅ /endupdate

@bot.slash_command(
    name='endupdate',
    description='ADMIN ONLY! | Ends an update process.'
)
@log_command('endupdate')
async def endupdate(ctx):
    try:
        if ctx.guild is None:
            embed = nextcord.Embed(
                title="⛔ Command Error",
                description="This command can only be used in Chill Lounge text channels.",
                color=0xFF5733
            )
            await ctx.send(embed=embed, ephemeral=True)
            return

        allowed_roles = ['⚙️ Developer']

        if any(role.name in allowed_roles for role in ctx.user.roles):
            global update_active
            if update_active:
                update_active = False

                success_embed = nextcord.Embed(
                    title="⚙️ Update Completed",
                    description="The update has been successfully completed.",
                    color=nextcord.Color.green()
                )
                await set_rich_presence(RPC_DEFAULT_STATE)
                await ctx.send(embed=success_embed, ephemeral=True)
            else:
                no_update_embed = nextcord.Embed(
                    title="⚙️ No Update Running",
                    description="There is no update running that needs to be ended.",
                    color=nextcord.Color.blue()
                )
                await ctx.send(embed=no_update_embed, ephemeral=True)
        else:
            error_embed = nextcord.Embed(
                title="❌ Error",
                description="You do not have permission for this command.",
                color=nextcord.Color.red()
            )
            await ctx.send(embed=error_embed, ephemeral=True)

    except Exception as e:
        error_embed = nextcord.Embed(
            title="❌ Error",
            description=f"An error occurred: {str(e)}",
            color=nextcord.Color.red()
        )
        await ctx.send(embed=error_embed, ephemeral=True)

# ✅ /lock

@bot.slash_command(
    name='lock',
    description='ADMIN ONLY! | Locks a channel.'
)
@log_command('lock')
async def lock(ctx, channel: nextcord.TextChannel = None):
    try:        
        if ctx.guild is None:
            embed = nextcord.Embed(
                title="⛔ Command Error",
                description="This command can only be used in Chill Lounge text channels.",
                color=0xFF5733
            )
            await ctx.send(embed=embed, ephemeral=True)
            return
           
                       
        allowed_roles = ['⚙️ Developer']

        if any(role.name in allowed_roles for role in ctx.user.roles):
            if not channel:
                channel = ctx.channel
            overwrite = nextcord.PermissionOverwrite()
            overwrite.send_messages = False
            await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)

            lock_embed = nextcord.Embed(
                title="🔒 Channel Locked",
                description=f"The channel {channel.mention} has been locked.",
                color=nextcord.Color.red()
            )
            lock_embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)

            await ctx.send(embed=lock_embed, ephemeral=True)
        else:
            error_embed = nextcord.Embed(
                title="❌ Error",
                description="You do not have permission to use this command.",
                color=nextcord.Color.red()
            )
            await ctx.send(embed=error_embed, ephemeral=True)
    except Exception as e:
        await ctx.send(f"❌ An error occurred: {str(e)}")

# ✅ /mute

muted_members = {}



def update_muted_data(user_name, muted_role_id, mute=True):
    muted_data = load_muted_data()
    
    if mute:
        if user_name in muted_data:
            muted_data[user_name][muted_role_id] = None
        else:
            muted_data[user_name] = {muted_role_id: None}
    else:
        if user_name in muted_data and muted_role_id in muted_data[user_name]:
            del muted_data[user_name][muted_role_id]
            if not muted_data[user_name]:
                del muted_data[user_name]
    
    with open(MUTED_DATA_FILE, 'w') as file:
        json.dump(muted_data, file)

muted_members = load_muted_data()

@bot.slash_command(
    name='mute',
    description='ADMIN ONLY! | Mutes a member.'
)
@log_command('mute')
async def mute(ctx, member: nextcord.Member):
    try:        
        allowed_roles = ['⚙️ Developer']

        if any(role.name in allowed_roles for role in ctx.user.roles):
            if ctx.user.guild_permissions.manage_roles:
                mute_role = nextcord.utils.get(ctx.guild.roles, id=893762438007246874)
                
                if mute_role in member.roles:
                    await ctx.send("❌ This member is already Muted.", ephemeral=True)
                else:
                    await member.add_roles(mute_role, reason="Muted by moderator")
                    mute_embed = nextcord.Embed(
                        title="🤫 Member Muted",
                        description=f"{member.mention} has been Muted by {ctx.user.mention}",
                        color=nextcord.Color.orange()
                    )
                    mute_embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)

                    await ctx.send(embed=mute_embed, ephemeral=True)

                    if ctx.guild.id not in muted_members:
                        muted_members[ctx.guild.id] = {}
                    muted_members[ctx.guild.id][member.name] = True
                    save_muted_data()
            else:
                await ctx.send("❌ You do not have permission to Mute members.", ephemeral=True)
        else:
            error_embed = nextcord.Embed(
                title="❌ Error",
                description="You do not have permission for this command.",
                color=nextcord.Color.red()
            )
            await ctx.send(embed=error_embed, ephemeral=True)
    except Exception as e:
        await ctx.send(f"❌ An error occurred: {str(e)}", ephemeral=True)

# ✅ /openreport

@bot.slash_command(
    name='openreport',
    description='ADMIN ONLY! | Opens a reporting channel for moderation.'
)
@log_command('openreport')
async def openreport(ctx, report_index: int):
    try:        
        if ctx.guild is None:
            embed = nextcord.Embed(
                title="⛔ Command Error",
                description="This command can only be used in Chill Lounge text channels.",
                color=0xFF5733
            )
            await ctx.send(embed=embed, ephemeral=True)
            return
           
        allowed_roles = ['⚙️ Developer']

        if any(role.name in allowed_roles for role in ctx.user.roles):
            if 1 <= report_index <= len(reports):
                actual_index = report_index - 1

                report = reports[actual_index]

                category = ctx.guild.get_channel(1106372883518869514)
                channel = await ctx.guild.create_text_channel(
                    f"report-{report_index}",
                    category=category
                )

                options_embed = nextcord.Embed(
                    title="Report Options",
                    description="Please select an option:",
                    color=nextcord.Color.blue()
                )
                options_embed.add_field(name="📫 Report Finished", value="Marks the report as finished and removes it from the file.", inline=False)
                options_embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)

                message = await channel.send(embed=options_embed)

                await message.add_reaction("📫")

                await ctx.send(f"Report **{report_index}** has been opened. Channel: {channel.mention}")

                def check(reaction, user):
                    return user == ctx.user and reaction.message.name == message.name

                try:
                    reaction, user = await bot.wait_for("reaction_add", timeout=60.0, check=check)

                    if str(reaction.emoji) == "📫":
                        reports.pop(actual_index)
                        save_reports()
                        await channel.send("This report channel will self-close. Thank you for reporting!")
                        await asyncio.sleep(2)
                        await channel.delete()
                except asyncio.TimeoutError:
                    pass
            else:
                await ctx.send("❌ Invalid report index. Please choose a valid report.")
        else:
            error_embed = nextcord.Embed(
                title="Error",
                description="❌ You do not have permission to view reports.",
                color=0xFF0000
            )
            await ctx.send(embed=error_embed, ephemeral=True)
    except Exception as e:
        await ctx.send(f"❌ An error occurred: {str(e)}")

# ✅ /unban

@bot.slash_command(
    name='unban',
    description='Unban a user'
)
@log_command('unban')
async def unban(ctx, user: nextcord.User):
    try:        
        if ctx.guild is None:
            embed = nextcord.Embed(
                title="⛔ Command Error",
                description="This command can only be used in Chill Lounge text channels.",
                color=0xFF5733
            )
            await ctx.send(embed=embed, ephemeral=True)
            return
           
        global config

        allowed_roles = ['⚙️ Developer']

        if any(role.name in allowed_roles for role in ctx.user.roles):
            user_name = user.name.lower()
            if user_name in config:
                if not config[user_name]['banned_status']:
                    warning_embed = nextcord.Embed(title="⚠️ Warning", description="Player is already unbanned!", color=nextcord.Color.yellow())
                    await ctx.send(embed=warning_embed, ephemeral=True)
                else:
                    config[user_name]['banned_status'] = False
                    save_config(config)

                    embed = nextcord.Embed(title="✅ You have been unbanned!", color=nextcord.Color.green())
                    embed.add_field(name="👤 User", value=user.mention)
                    embed.add_field(name="ℹ️ Status", value="Unbanned")
                    embed.set_footer(text="Dont make an Mistake again! // Made by @prodbyeagle", icon_url=pic_link)

                    await user.send(embed=embed)

                    bans_channel = bot.get_channel(BANS_CHANNEL_ID)
                    if bans_channel:
                        await bans_channel.send(embed=embed)

                    confirmation_embed = nextcord.Embed(description="🔓 Player unbanned!", color=nextcord.Color.green())
                    confirmation_msg = await ctx.send(embed=confirmation_embed)
                    await asyncio.sleep(2)
                    await confirmation_msg.delete()
            else:
                await ctx.send(f"⚠️ {user.name} is not registered.")
        else:
            error_embed = nextcord.Embed(
                title="❌ Error",
                description="You do not have permission for this command.",
                color=nextcord.Color.red()
            )
            await ctx.send(embed=error_embed, ephemeral=True)
    except Exception as e:
        await ctx.send(f"❌ An error occurred: {str(e)}")


# ✅ /update

@bot.slash_command(
    name='update',
    description='ADMIN ONLY! | Initiates an update process.'
)
@log_command('update')
async def update(ctx, updatemessage: str = None):
    try:
        if ctx.guild is None:
            embed = nextcord.Embed(
                title="⛔ Command Error",
                description="This command can only be used in Chill Lounge text channels.",
                color=0xFF5733
            )
            await ctx.send(embed=embed, ephemeral=True)
            return

        allowed_roles = ['⚙️ Developer']

        if any(role.name in allowed_roles for role in ctx.user.roles):
            global update_active

            if update_active:
                update_embed = nextcord.Embed(
                    title="⚠️ Update in Progress",
                    description="An update is already in progress. Please wait until it is completed.",
                    color=nextcord.Color.orange()
                )
                await ctx.send(embed=update_embed, ephemeral=True)
                return

            channel = bot.get_channel(UPDATE_CHANNEL_ID)

            if not channel:
                target_not_found_embed = nextcord.Embed(
                    title="❌ Target Channel Not Found",
                    description="Target channel not found. Please configure the target channel ID.",
                    color=nextcord.Color.red()
                )
                await ctx.send(embed=target_not_found_embed, ephemeral=True)
                return

            update_active = True
            await set_rich_presence(RPC_UPDATE_STATE)

            message_parts = []
            if updatemessage is not None:
                message_parts = [updatemessage[i:i + 2000] for i in range(0, len(updatemessage), 2000)]

            for part in message_parts:
                embed = nextcord.Embed(
                    title="🔄 Update",
                    description=part,
                    color=nextcord.Color.yellow()
                )

                embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)

                await channel.send(embed=embed)

            update_started_embed = nextcord.Embed(
                title="⚙️ Update Phase Started",
                description=f"{updatemessage}",
                color=nextcord.Color.green()
            )
            await ctx.send(embed=update_started_embed, ephemeral=True)
        else:
            error_embed = nextcord.Embed(
                title="❌ Error",
                description="You do not have permission for this command.",
                color=nextcord.Color.red()
            )
            await ctx.send(embed=error_embed, ephemeral=True)

    except Exception as e:
        error_message_embed = nextcord.Embed(
            title="❌ Error",
            description=f"An error occurred: {str(e)}",
            color=nextcord.Color.red()
        )
        await ctx.send(embed=error_message_embed, ephemeral=True)

# ✅ /unlock

@bot.slash_command(
    name='unlock',
    description='ADMIN ONLY! | Unlocks a channel.'
)
@log_command('unlock')
async def unlock(ctx, channel: nextcord.TextChannel = None):
    try:        
        if ctx.guild is None:
            embed = nextcord.Embed(
                title="⛔ Command Error",
                description="This command can only be used in Chill Lounge text channels.",
                color=0xFF5733
            )
            await ctx.send(embed=embed, ephemeral=True)
            return
           
                       
        allowed_roles = ['⚙️ Developer']

        if any(role.name in allowed_roles for role in ctx.user.roles):
            if not channel:
                channel = ctx.channel
            overwrite = nextcord.PermissionOverwrite()
            overwrite.send_messages = True
            await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)

            unlock_embed = nextcord.Embed(
                title="🔓 Channel Unlocked",
                description=f"The channel {channel.mention} has been unlocked.",
                color=nextcord.Color.green()
            )
            unlock_embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)

            await ctx.send(embed=unlock_embed, ephemeral=True)
        else:
            error_embed = nextcord.Embed(
                title="❌ Error",
                description="You do not have permission to use this command.",
                color=nextcord.Color.red()
            )
            await ctx.send(embed=error_embed, ephemeral=True)
    except Exception as e:
        await ctx.send(f"❌ An error occurred: {str(e)}")

# ✅ /unmute

@bot.slash_command(
    name='unmute',
    description='ADMIN ONLY! | Unmutes a member.'
)
@log_command('unmute')
async def unmute(ctx, member: nextcord.Member):
    try:        
        if ctx.guild is None:
            embed = nextcord.Embed(
                title="⛔ Command Error",
                description="This command can only be used in Chill Lounge text channels.",
                color=0xFF5733
            )
            await ctx.send(embed=embed, ephemeral=True)
            return
           
                       
        allowed_roles = ['⚙️ Developer']

        if any(role.name in allowed_roles for role in ctx.user.roles):
            if ctx.user.guild_permissions.manage_roles:
                mute_role = nextcord.utils.get(ctx.guild.roles, name="🔇MUTED")
                if mute_role and mute_role in member.roles:
                    await member.remove_roles(mute_role, reason="Unmuted by moderator")
                    unmute_embed = nextcord.Embed(
                        title="🔊 Member Unmuted",
                        description=f"{member.mention} has been unmuted by {ctx.user.mention}",
                        color=nextcord.Color.green()
                    )
                    unmute_embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)
                    await ctx.send(embed=unmute_embed, ephemeral=True)

                    if ctx.guild.id in muted_members and member.name in muted_members[ctx.guild.id]:
                        muted_members[ctx.guild.id][member.name] = False
                        save_muted_data()
                else:
                    await ctx.send("❌ This member is not muted.")
            else:
                await ctx.send("❌ You do not have permission to unmute members.")
        else:
            error_embed = nextcord.Embed(
                title="❌ Error",
                description="You do not have permission for this command.",
                color=nextcord.Color.red()
            )
            await ctx.send(embed=error_embed, ephemeral=True)
    except Exception as e:
        await ctx.send(f"❌ An error occurred: {str(e)}")

# ✅ /viewreports

@bot.slash_command(
    name='viewreports',
    description='ADMIN ONLY! | Displays reports.'
)
@log_command('viewreports')
async def viewreports(ctx):
    try:
        if ctx.guild is None:
            embed = nextcord.Embed(
                title="⛔ Command Error",
                description="This command can only be used in Chill Lounge text channels.",
                color=0xFF5733
            )
            await ctx.send(embed=embed, ephemeral=True)
            return

        allowed_roles = ['⚙️ Developer']

        if any(role.name in allowed_roles for role in ctx.user.roles):
            embed = nextcord.Embed(title="📝 Reports")

            for i, report in enumerate(reports, 1):
                reporter = ctx.guild.get_member(report['reporter'])
                reported_member = ctx.guild.get_member(report['reported_member'])

                if reported_member is not None:
                    id_text = f"**ID:** `{reported_member.name}`"

                    embed.add_field(
                        name=f"Report {i}",
                        value=f"**Reporter:** {reporter.mention}\n**Reported Member:** {reported_member.mention}\n**Reason:** {report['reason']}\n{id_text}",
                        inline=False,
                    )
                else:
                    continue

            embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)

            await ctx.send(embed=embed, ephemeral=True)
        else:
            error_embed = nextcord.Embed(title="Error", description="❌ You don't have permission to view reports.", color=0xFF0000)
            await ctx.send(embed=error_embed, ephemeral=True)
    except Exception as e:
        error_embed = nextcord.Embed(title="Error", description=f"❌ An error occurred: {str(e)}", color=0xFF0000)
        await ctx.send(embed=error_embed, ephemeral=True)

# ✅ /warn

@bot.slash_command(
    name='warn',
    description='ADMIN ONLY! | Warns a user.'
)
@log_command('warn')
async def warn(ctx, user: nextcord.User):
    try:
        if ctx.guild is None:
            embed = nextcord.Embed(
                title="⛔ Command Error",
                description="This command can only be used in Chill Lounge text channels.",
                color=0xFF5733
            )
            await ctx.send(embed=embed, ephemeral=True)
            return

        global config

        allowed_roles = ['⚙️ Developer']

        if any(role.name in allowed_roles for role in ctx.user.roles):
            user_name = user.name.lower()
            if user_name in config:
                if config[user_name]['banned_status']:
                    warning_embed = nextcord.Embed(title="⚠️ Warning", description="The player is already banned!", color=nextcord.Color.yellow())
                    await ctx.send(embed=warning_embed, ephemeral=True)
                else:
                    config[user_name]['warnings'] = config.get(user_name, {}).get('warnings', 0) + 1
                    save_config(config)

                    warn_embed = nextcord.Embed(title="⚠️ Warning", description=f"{user.mention} has been warned!", color=nextcord.Color.orange())
                    warn_embed.add_field(name="Warnings", value=str(config[user_name]['warnings']))
                    warn_embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)
                    await ctx.send(embed=warn_embed, ephemeral=True)
            else:
                await ctx.send(f"⚠️ {user.name} is not registered.")
        else:
            error_embed = nextcord.Embed(
                title="❌ Error",
                description="You do not have permission for this command.",
                color=nextcord.Color.red()
            )
            await ctx.send(embed=error_embed, ephemeral=True)

    except Exception as e:
        await ctx.send(f"❌ An error occurred: {str(e)}")

# ➖➖➖➖➖➖➖➖➖

# |\|/|\|\|/|\/|\|/|\/|\|/|\|\|/|\|/|\|\|

# ➖➖➖➖➖➖➖➖➖
# 𝓤𝓢𝓔𝓡 𝓒𝓞𝓜𝓜𝓐𝓝𝓓𝓢

# ✅ /achievements

achievements_earned = {}


@bot.slash_command(
    name='achievements',
    description='View your achievements.'
)
@log_command('achievements')
async def show_achievements(ctx, member: nextcord.Member = None):
    try:
        if ctx.guild is None:
            embed = nextcord.Embed(
                title="⛔ Command Error",
                description="This command can only be used in Chill Lounge text channels.",
                color=0xFF5733
            )
            await ctx.send(embed=embed, ephemeral=True)
            return
                       
        if member is None:
            member = ctx.user
        
        if update_active:
            update_embed = nextcord.Embed(
                title="🛠️ Update in Progress",
                description="A system update is currently in progress. Please try again later.",
                color=nextcord.Color.orange()
            )
            update_embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)
            await ctx.send(embed=update_embed, ephemeral=True)
            return
        
        if member.name in config and config[member.name]["banned_status"]:
            ban_embed = nextcord.Embed(title="❌ BANNED", description="You are banned! View your reason in your DMs.", color=0xFF0000)
            ban_embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)
            await ctx.send(embed=ban_embed, ephemeral=True)
            return

        user_roles = [role.name for role in member.roles]

        embed = nextcord.Embed(
            title=f"🏆 **Achievements from {member.display_name}**",
            color=nextcord.Color.gold()
        )
        embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)
        achievement_names, achievement_descriptions = load_achievement_names()

        for achievement_name in achievement_names:
            if achievement_name in user_roles:
                description = achievement_descriptions.get(achievement_name, '')
                embed.add_field(
                    name=f"{achievement_name}",
                    value=description,
                    inline=False
                )
        await ctx.send(embed=embed, ephemeral=True)
    except Exception as e:
        error_embed = nextcord.Embed(title="❌ Error", description=f"An error occurred: {str(e)}", color=0xFF0000)
        await ctx.send(embed=error_embed, ephemeral=True)

# ✅ /balance

def user_xp_money_data():
    try:
        with open("chilly_config.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

@bot.slash_command(
    name='balance',
    description='Check your balance.'
)
@log_command('balance')
async def balance(ctx):
    try:
        if ctx.guild is None:
            embed = nextcord.Embed(
                title="⛔ Command Error",
                description="This command can only be used in Chill Lounge text channels.",
                color=0xFF5733
            )
            await ctx.send(embed=embed, ephemeral=True)
            return

        user_name = str(ctx.user.name)
        
        data = user_xp_money_data()

        if user_name in data:
            money = int(data[user_name]['money'])
            formatted_money = '{:,}'.format(money)
            money_text = f'**{formatted_money}**'

            embed = nextcord.Embed(
                title=f'🏧 Balance of {ctx.user.name}',
                color=nextcord.Color.green()
            )
            embed.add_field(name='🪙 Money', value=money_text, inline=False)
            embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)

            await ctx.send(embed=embed, ephemeral=True)
        else:
            embed = nextcord.Embed(
                title="⛔ No Money",
                description=f'❌ **{user_name}**, you have no money.',
                color=nextcord.Color.red()
            )
            await ctx.send(embed=embed, ephemeral=True)
    except Exception as e:
        await ctx.send(f"❌ An error occurred: {str(e)}")

# ✅ /commands

@bot.slash_command(
    name='commands',
    description='Displays a list of available commands.'
)
@log_command('commands')
async def slash_commands(interaction: nextcord.Interaction):
    try:
        if interaction.guild is None:
            embed = nextcord.Embed(
                title="⛔ Command Error",
                description="This command can only be used in Chill Lounge text channels.",
                color=0xFF5733
            )
            await interaction.send(embed=embed, ephemeral=True)
            return

        if update_active:
            update_embed = nextcord.Embed(
                title="🛠️ Update in Progress",
                description="A system update is currently in progress. Please try again later.",
                color=nextcord.Color.orange()
            )
            update_embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)
            await interaction.response.send_message(embed=update_embed, ephemeral=True)

        user = interaction.user

        if user.name in config and config[user.name]["banned_status"]:
            ban_embed = nextcord.Embed(title="❌ BANNED", description="You are banned! View your Reason in your DM's", color=0xFF0000)
            ban_embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)
            await interaction.response.send_message(embed=ban_embed, ephemeral=True)
            return

        embed = nextcord.Embed(title="**🌶️ Commands**")
        embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)
        embed.add_field(name="**🔨 Commands**", value=""" 
        :medal: **`/achievements`** - View your achievements.
        :moneybag: **`/balance`** - Check your balance.
        :scroll: **`/commands`** - Displays This list.                
        :level_slider: **`/level`** - Check your level.
        :level_slider: **`/lvlleaderboard`** - View the level leaderboard.
        :moneybag: **`/moneyleaderboard`** - View the cash leaderboard.
        :speech_balloon: **`/msgleaderboard`** - View the MSG leaderboard.
        :alarm_clock: **`/remindme`** - Set a reminder.
        :exclamation: **`/report`** - Report someone.
        :bulb: **`/suggesttochilly`** - Suggest an Idea to the Developers.
        :gear: **`/usersettings`** - Edit your settings.
        :bar_chart: **`/userstats`** - View user stats.
        :trophy: **`/vcleaderboard`** - View the voice chat leaderboard.
        :desktop: **`/website`** - Look at the Website to see some Extras.
        :cloud: **`/weather`** - Get the weather forecast for a location.
        """, inline=False)

        required_role = nextcord.utils.get(user.roles, name='⚙️ Developer')
        if required_role is not None:
            embed.add_field(name="**⚙️ Dev Commands**", value=""" 
        :medal: **`/addachievements`** - Add achievements.
        :speech_balloon: **`/announcement`** - Make the bot say a message.
        :hammer: **`/ban`** - Bans a player.
        :wastebasket: **`/clearchannel`** - Deletes all messages in the current channel.
        :bug: **`/debug`** - Start debug.             
        :gear: **`/endupdate`** - Put the Bot back to Normal Mode.
        :sparkles: **`/event`** - Start an Event.
        :lock: **`/lock`** - Lock the current channel.
        :mute: **`/mute`** - Mute a player.
        """, inline=False)
        
        required_role = nextcord.utils.get(user.roles, name='⚙️ Developer')
        if required_role is not None:
            embed.add_field(name="**⚙️ Dev Commands**", value=""" 
        :unlock: **`/openreport`** - Open a specific report.
        :unlock: **`/unban`** - Unbans a player.
        :gear: **`/update`** - Put the Bot in Update Mode
        :unlock: **`/unlock`** - Unlock the current channel.
        :speaker: **`/unmute`** - Unmute a player.
        :mag_right: **`/viewreports`** - View reports with pagination.
        :warning: **`/warn`** - Warns a player.
        """, inline=False)

        embed.add_field(name="**🎮 Gaming**", value=""" 
        :man_tone1: **`/dadjoke`** - Get a random dadjoke.
        :smile: **`/joke`** - Get a random joke.
        :moneybag: **`/rob`** - Attempt to steal coins from another user.
        :video_game: **`/tic`** - Start a TicTacToe game.
        :question: **`/trivia`** - Start a trivia game.
        """, inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ An error occurred: {str(e)}")

# ✅ /level

@bot.slash_command(
    name='level',
    description='Check your level and experience needed for the next level.'
)
@log_command('level')
async def level(ctx):
    try:
        if ctx.guild is None:
            embed = nextcord.Embed(
                title="⛔ Command Error",
                description="This command can only be used in Chill Lounge text channels.",
                color=0xFF5733
            )
            await ctx.send(embed=embed, ephemeral=True)
            return
        
        user_name = ctx.user.name        
        chilly_config = load_config()
        user_data = chilly_config[user_name]
        user = ctx.user

        if update_active:
            update_embed = nextcord.Embed(
                title="🛠️ Update in Progress",
                description="A system update is currently in progress. Please try again later.",
                color=nextcord.Color.orange()
            )
            update_embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)
            await ctx.send(embed=update_embed, ephemeral=True)
            return
        
        if user.name in config and config[user.name]["banned_status"]:
            ban_embed = nextcord.Embed(title="❌ BANNED", description="You are banned! View your Reason in your DM's", color=0xFF0000)
            ban_embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)
            await ctx.send(embed=ban_embed, ephemeral=True)
            return
        
        if user_name in user_xp_money_data():
            xp = user_xp_money_data()[user_name]['xp']
            level = user_xp_money_data()[user_name]['level']
            required_xp = 100 + (user_data.get('level', 0) * 100)

            while xp >= required_xp:
                level += 1
                required_xp = int(required_xp * 1.2)

            xp_needed = required_xp - xp

            xp_needed = round(xp_needed)

            embed = nextcord.Embed(
                title=f'**🆙 Level of {user.name}**',
                color=nextcord.Color.blue()
            )
            embed.add_field(name='**Level**', value=level, inline=False)
            embed.add_field(name='XP till **Next** Level!', value=xp_needed, inline=False)
            embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)

            await ctx.send(embed=embed, ephemeral=True)
        else:
            embed = nextcord.Embed(
                title="⛔ No Level",
                description=f'❌ **{user.name}**, you have no level.',
                color=nextcord.Color.red()
            )
            await ctx.send(embed=embed, ephemeral=True)
    except Exception as e:
        await ctx.send(f"❌ An error occurred: {str(e)}")

# ✅ /lvlleaderboard

with open("chilly_config.json", "r") as file:
    xp_data = json.load(file)

@bot.slash_command(
    name='lvlleaderboard',
    description='View the Level leaderboard.'
)
@log_command('lvlleaderboard')
async def lvlleaderboard(ctx):
    user = ctx.user
    try:
        if ctx.guild is None:
            embed = nextcord.Embed(
                title="⛔ Command Error",
                description="This command can only be used in Chill Lounge text channels.",
                color=0xFF5733
            )
            await ctx.send(embed=embed, ephemeral=True)
            return

        if update_active:
            update_embed = nextcord.Embed(
                title="🛠️ Update in Progress",
                description="A system update is currently in progress. Please try again later.",
                color=nextcord.Color.orange()
            )
            update_embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)
            await ctx.send(embed=update_embed, ephemeral=True)
            return

        if user.name in config and config[user.name]["banned_status"]:
            ban_embed = nextcord.Embed(title="❌ BANNED", description="You are banned! View your reason in your DMs.", color=0xFF0000)
            ban_embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)
            await ctx.send(embed=ban_embed, ephemeral=True)
            return

        with open("chilly_config.json", "r") as file:
            xp_data = json.load(file)

        sorted_users = sorted(xp_data.items(), key=lambda x: x[1].get("level", 0), reverse=True)

        leaderboard_embed = nextcord.Embed(title="📀 Level Leaderboard", color=nextcord.Color.blue())

        for idx, (user_name, data) in enumerate(sorted_users[:10], start=1):
            xp = data.get("level", 0)
            if xp > 0:
                rounded_xp = round(xp)
                user = ctx.guild.get_member_named(user_name)
                if user:
                    if idx < 4:
                        medal = ["🥇", "🥈", "🥉"][idx - 1]
                    else:
                        medal = "🏅"
                    formatted_name = f"{medal} {user.display_name}"
                    leaderboard_embed.add_field(name=" ", value=f"**{formatted_name}**\n**{rounded_xp} Level**", inline=False)

        await ctx.send(embed=leaderboard_embed, ephemeral=True)
    except Exception as e:
        await ctx.send(f"❌ An error occurred: {str(e)}")

# ✅ /moneyleaderboard

with open("chilly_config.json", "r") as file:
    cash_data = json.load(file)

locale.setlocale(locale.LC_ALL, "")

@bot.slash_command(
    name='moneyleaderboard',
    description='View the Cash leaderboard.'
)
@log_command('cashleaderboard')
async def cashleaderboard(ctx):
    user = ctx.user
    try:
        if ctx.guild is None:
            embed = nextcord.Embed(
                title="⛔ Command Error",
                description="This command can only be used in Chill Lounge text channels.",
                color=0xFF5733
            )
            await ctx.send(embed=embed, ephemeral=True)
            return

        if update_active:
            update_embed = nextcord.Embed(
                title="🛠️ Update in Progress",
                description="A system update is currently in progress. Please try again later.",
                color=nextcord.Color.orange()
            )
            update_embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)
            await ctx.send(embed=update_embed, ephemeral=True)
            return

        if user.name in config and config[user.name]["banned_status"]:
            ban_embed = nextcord.Embed(title="❌ BANNED", description="You are banned! View your reason in your DMs.", color=0xFF0000)
            ban_embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)
            await ctx.send(embed=ban_embed, ephemeral=True)
            return

        with open("chilly_config.json", "r") as file:
            money_data = json.load(file)

        sorted_users = sorted(money_data.items(), key=lambda x: x[1].get("money", 0), reverse=True)

        leaderboard_embed = nextcord.Embed(title="🪙 Money Leaderboard", color=nextcord.Color.blue())

        for idx, (user_name, data) in enumerate(sorted_users[:10], start=1):
            money = data.get("money", 0)
            if money > 0:

                rounded_money = round(money)
                user = ctx.guild.get_member_named(user_name)
                if user:
                    if idx < 4:
                        medal = ["🥇", "🥈", "🥉"][idx - 1]
                    else:
                        medal = "🏅"
                    formatted_name = f"{medal} {user.display_name}"
                    leaderboard_embed.add_field(name=" ", value=f"**{formatted_name}**\n**{rounded_money} Coins**", inline=False)

        await ctx.send(embed=leaderboard_embed, ephemeral=True)
    except Exception as e:
        await ctx.send(f"❌ An error occurred: {str(e)}")



# ✅ /msgleaderboard

@bot.slash_command(
    name='msgleaderboard',
    description='View the message leaderboard.'
)
@log_command('msgleaderboard')
async def msgleaderboard(ctx):
    user = ctx.user
    try:
        if ctx.guild is None:
            embed = nextcord.Embed(
                title="⛔ Command Error",
                description="This command can only be used in Chill Lounge text channels.",
                color=0xFF5733
            )
            await ctx.send(embed=embed, ephemeral=True)
            return
        
        if update_active:
            update_embed = nextcord.Embed(
                title="🛠️ Update in Progress",
                description="A system update is currently in progress. Please try again later.",
                color=nextcord.Color.orange()
            )
            update_embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)
            await ctx.send(embed=update_embed, ephemeral=True)
            return

        with open("chilly_config.json", "r") as file:
            config_data = json.load(file)

        if user.name in config and config[user.name]["banned_status"]:
            ban_embed = nextcord.Embed(title="❌ BANNED", description="You are banned! View your reason in your DMs.", color=0xFF0000)
            ban_embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)
            await ctx.send(embed=ban_embed, ephemeral=True)
            return

        sorted_users = sorted(config_data.items(), key=lambda x: x[1].get("messages_sent", 0), reverse=True)

        leaderboard_embed = nextcord.Embed(title="📧 Message Leaderboard", color=nextcord.Color.blue())

        for idx, (user_name, data) in enumerate(sorted_users[:10], start=1):
            messages_sent = data.get("messages_sent", 0)
            if messages_sent > 0:
                user = ctx.guild.get_member_named(user_name)
                if user:
                    if idx < 4:
                        medal = ["🥇", "🥈", "🥉"][idx - 1]
                    else:
                        medal = "🏅"
                    formatted_name = f"{medal} {user.display_name}"
                    leaderboard_embed.add_field(name=" ", value=f"**{formatted_name}**\n**{messages_sent} Messages**", inline=False)

        await ctx.send(embed=leaderboard_embed, ephemeral=True)
    except Exception as e:
        await ctx.send(f"❌ An error occurred: {str(e)}")

# ✅ /remindme

@bot.slash_command(
    name='remindme',
    description='Set a reminder for a specified time.'
)
@log_command('remindme')
async def remindme(ctx, time: str, message: str):
    try:
        user_name = ctx.user.name.lower()
        if user_name in config and config[user_name]["banned_status"]:
            ban_embed = nextcord.Embed(title="❌ BANNED", description="You are banned! View your Reason in your DM's", color=0xFF0000)
            ban_embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)
            await ctx.send(embed=ban_embed, ephemeral=True)
            return

        time = convert_time(time)
        if time is None:
            await ctx.send("❌ Invalid time format. Example: /remindme 1h30m Sentence")
            return

        if update_active:
            update_embed = nextcord.Embed(
                title="🛠️ Update in Progress",
                description="A system update is currently in progress. Please try again later.",
                color=nextcord.Color.orange()
            )
            update_embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)
            await ctx.send(embed=update_embed, ephemeral=True)
            return
        
        remind_embed = nextcord.Embed(
            title="Remind",
            description=f"✅ I will remind you in {time}!",
            color=nextcord.Color.green()
        )
        remind_embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=remind_embed, ephemeral=True)

        await asyncio.sleep(time)

        user = ctx.user
        await user.send(f"{user.mention}, your reminder is due!: **{message}**")
    except Exception as e:
        await ctx.send(f"❌ An error occurred: {str(e)}")

def convert_time(time):
    hours = 0
    minutes = 0
    seconds = 0

    time = time.lower()
    if 'h' in time:
        hours_str, time = time.split('h', 1)
        hours = int(hours_str)
    if 'm' in time:
        minutes_str, time = time.split('m', 1)
        minutes = int(minutes_str)
    if 's' in time:
        seconds_str, time = time.split('s', 1)
        seconds = int(seconds_str)

    time = hours * 3600 + minutes * 60 + seconds

    return time

async def set_rich_presence(state):
    activity = nextcord.Activity(type=nextcord.ActivityType.playing, name=state)
    await bot.change_presence(activity=activity)

# ✅ /report

reports = load_reports()

@bot.slash_command(
    name='report',
    description='Report a member for a specific reason.'
)
@log_command('report')
async def report(ctx, member: nextcord.Member, reason: str):
    try:
        if ctx.guild is None:
            embed = nextcord.Embed(
                title="⛔ Command Error",
                description="This command can only be used in Chill Lounge text channels.",
                color=0xFF5733
            )
            await ctx.send(embed=embed, ephemeral=True)
            return

        user_name = ctx.user.name.lower()
        if user_name in config and config[user_name]["banned_status"]:
            ban_embed = nextcord.Embed(title="❌ BANNED", description="You are banned! View your Reason in your DM's", color=0xFF0000)
            ban_embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)
            await ctx.send(embed=ban_embed, ephemeral=True)
            return

        user = ctx.user

        if update_active:
            update_embed = nextcord.Embed(
                title="🛠️ Update in Progress",
                description="A system update is currently in progress. Please try again later.",
                color=nextcord.Color.orange()
            )
            update_embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)
            await ctx.send(embed=update_embed, ephemeral=True)
            return

        report = {
            "reporter": user.name,
            "reported_member": member.name,
            "reason": reason,
        }
        reports.append(report)

        await ctx.send(f"✅ {user.mention}. The Report was sent!")

        save_reports()
    except Exception as e:
        await ctx.send(f"❌ An error occurred: {str(e)}")

# ✅ /suggesttochilly

user_name = None

@bot.slash_command(
    name='suggesttochilly',
    description='Send a suggestion to the bot developer.'
)
@log_command('suggest')
async def suggest(ctx, suggestion):
    global user_name
    user_name = ctx.user.name
    channel = bot.get_channel(893762440196677646)
    if user_name in config and config[user_name]["banned_status"]:
        ban_embed = nextcord.Embed(title="❌ BANNED", description="You are banned! View your Reason in your DM's", color=0xFF0000)
        ban_embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=ban_embed, ephemeral=True)
        return
    if channel is not None:
        embed = nextcord.Embed(
            title=f'🦅 Suggestion from {user_name}',
            description=f'\n**`{suggestion}`**',
            color=nextcord.Colour.red()
        )
        embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)
        await channel.send(embed=embed)

        embed = nextcord.Embed(
            title='✅ Suggestion Sent',
            description='Your suggestion has been sent to the bot developer.',
            color=nextcord.Colour.green()
        )
        embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=embed, ephemeral=True)
    else:
        embed = nextcord.Embed(
            title='❌ Error',
            description='The channel where suggestions are sent to could not be found.',
            color=nextcord.Colour.red()
        )
        embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=embed, ephemeral=True)

# ✅ /usersettings

def generate_confirmation_code():
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(8))

class SettingsView(nextcord.ui.View):
    def __init__(self, user_name, guild, bot):
        super().__init__()
        self.user_name = user_name
        self.bot = bot
        self.guild = guild

    @nextcord.ui.button(label="Toggle Robs", style=nextcord.ButtonStyle.green)
    async def toggle_xp_notifications(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        user_data = load_config()
        user_data[self.user_name]['rob_activated'] = not user_data[self.user_name].get('rob_activated', True)
        save_config(user_data)

        button.style = nextcord.ButtonStyle.green if user_data[self.user_name]['rob_activated'] else nextcord.ButtonStyle.red

        notification_status = "Activated" if user_data[self.user_name]['rob_activated'] else "Deactivated"

        embed = nextcord.Embed(
            title="Robs Toggle",
            description=f"Robs are now {notification_status}!",
            color=nextcord.Color.red() if user_data[self.user_name]['rob_activated'] else nextcord.Color.green()
        )

        await interaction.response.edit_message(embed=embed, view=self)

    @nextcord.ui.button(label="Reset Messages Sent", style=nextcord.ButtonStyle.red)
    async def reset_messages_sent(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        user_data = load_config()
        user_name = self.user_name
        embed = None

        if user_data[user_name]['messages_sent'] == 0:
            embed = nextcord.Embed(
                title="🔃 Reset Messages Sent",
                description="You have already 0 Sent Messages!",
                color=nextcord.Color.red()
            )
    
        if embed is not None:
            try:
                await interaction.response.edit_message(embed=embed, view=self)
            except nextcord.errors.InteractionResponded:
                pass

        user_data[user_name]['messages_sent'] = 0

        achievements_earned = load_achievements_earned()

        if user_name in achievements_earned:
            for achievement_id in achievements_earned[user_name]:
                if achievement_id.startswith("message_count_"):
                    achievements_earned[user_name] = [a_id for a_id in achievements_earned[user_name] if a_id != achievement_id]

            roles_to_remove = []
            for role_id in ["🚀 ULTIMATE CHATTER", "💫 Mythical Chatter", "🌟 Chat Master", "💬 Mega Chatter", "💬 Big Chatter", "🗨️ Chatter"]:
                role = nextcord.utils.get(interaction.guild.roles, name=role_id)
                if role and role in interaction.user.roles:
                    roles_to_remove.append(role)

            if roles_to_remove:
                await interaction.user.remove_roles(*roles_to_remove)

        save_config(user_data)
        save_achievements_earned(achievements_earned)

        embed = nextcord.Embed(
            title="🔃 Reset Messages Sent",
            description="Messages Sent has been reset to 0!",
            color=nextcord.Color.red()
        )
    
        try:
            await interaction.response.edit_message(embed=embed, view=self)
        except nextcord.errors.InteractionResponded:
            pass

    @nextcord.ui.button(label="Reset Trivia Points", style=nextcord.ButtonStyle.red)
    async def reset_trivia_points(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        user_data = load_config()
        user_name = self.user_name
        embed = None
    
        if user_data[user_name]['trivia_points'] == 0:
            embed = nextcord.Embed(
                title="🔃 Reset Trivia Points",
                description="You have already 0 Trivia Points!",
                color=nextcord.Color.red()
            )
    
        if embed is not None:
            try:
                await interaction.response.edit_message(embed=embed, view=self)
            except nextcord.errors.InteractionResponded:
                pass
    
        user_data[user_name]['trivia_points'] = 0
    
        achievements_earned = load_achievements_earned()
    
        if user_name in achievements_earned:
            for achievement_id in achievements_earned[user_name]:
                if achievement_id.startswith("trivia_points_"):
                    achievements_earned[user_name] = [a_id for a_id in achievements_earned[user_name] if a_id != achievement_id]
    
            roles_to_remove = []
            for role_id in ["😱 DO YOU HAVE A LIFE?!", "👨‍💻 Cheater", "🕵️‍♂️ Game Master", "🤴 Pro Player", "💪 Amateur Player", "👨‍🎓 Average Player", "1️⃣ First Point"]:
                role = nextcord.utils.get(interaction.guild.roles, name=role_id)
                if role and role in interaction.user.roles:
                    roles_to_remove.append(role)
    
            if roles_to_remove:
                await interaction.user.remove_roles(*roles_to_remove)
    
        save_config(user_data)
        save_achievements_earned(achievements_earned)
    
        embed = nextcord.Embed(
            title="🔃 Reset Trivia Points",
            description="Trivia Points has been reset to 0!",
            color=nextcord.Color.red()
        )
    
        try:
            await interaction.response.edit_message(embed=embed, view=self)
        except nextcord.errors.InteractionResponded:
            pass
    
    @nextcord.ui.button(label="Reset Money and Level", style=nextcord.ButtonStyle.red)
    async def reset_level(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        xp_cash_data = load_config()
        user_name = self.user_name
        embed = None

        if xp_cash_data[user_name]['level'] == 0:
            embed = nextcord.Embed(
                title="🔃 Reset Money and Level",
                description="You already have no Money and no Level!",
                color=nextcord.Color.red()
            )
    
        if embed is not None:
            try:
                await interaction.response.edit_message(embed=embed, view=self)
            except nextcord.errors.InteractionResponded:
                pass

        if self.user_name in xp_cash_data:
            xp_cash_data[self.user_name]['level'] = 0
            xp_cash_data[self.user_name]['xp'] = 0
            xp_cash_data[self.user_name]['money'] = 0
            save_config(xp_cash_data)

        embed = nextcord.Embed(
            title="🔃 Reset Money and Level",
            description="Level and Money has been reset to 0!",
            color=nextcord.Color.red()
        )
    
        try:
            await interaction.response.edit_message(embed=embed, view=self)
        except nextcord.errors.InteractionResponded:
            pass

@bot.slash_command(
    name='usersettings',
    description='🔢 Clear your Trivia Points/Messages Sent or de/activate Robs'
)
@log_command('settings')
async def settings(ctx):
    user_name = ctx.user.name.lower()
    user_data = load_config().get(user_name, {})
    rob_activated = user_data.get('rob_activated', True)
    guild = ctx.guild

    if not user_data:
        embed = nextcord.Embed(
            title="❌ **`No active profile found!`**",
            color=nextcord.Color.red()
        )
        embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=embed, ephemeral=True)
        return

    view = SettingsView(user_name, guild, bot)
    view.children[0].style = nextcord.ButtonStyle.green if rob_activated else nextcord.ButtonStyle.red

    settings_embed = nextcord.Embed(
        title="⚙️ Settings Menu",
        description=f"Hello, {ctx.user.name}! This is your settings menu.",
        color=nextcord.Color.dark_grey()
    )
    settings_embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
    await ctx.send(embed=settings_embed, view=view, ephemeral=True)

# ✅ /userstats

@bot.slash_command(
    name="userstats",
    description="ADMIN ONLY! | Displays user stats on the server.",
)
@log_command('userstats')
async def userstats(ctx, user: nextcord.User):
    try:
        if ctx.guild is None:
            embed = nextcord.Embed(
                title="⛔ Command Error",
                description="This command can only be used in Chill Lounge text channels.",
                color=0xFF5733
            )
            await ctx.send(embed=embed, ephemeral=True)
            return

        if any:
            config_data = load_config()

            username = user.name
            user_info = config_data.get(username, None)

            if user_info:
                banned_status = user_info.get("banned_status", False)
                ban_reason = user_info.get("ban_reason", "No Reason")
                warnings = user_info.get("warnings", 0)
                trivia_points = user_info.get("trivia_points", 0)

                messages_sent = user_info.get("messages_sent", 0)
                lvlup_noti = user_info.get("lvlup_noti", False)
                achievement_noti = user_info.get("achievement_noti", False)
                rob_activated = user_info.get("rob_activated", False)

                embed = nextcord.Embed(
                    title=f"Userstats for {username}",
                    color=nextcord.Color.green()
                )
                embed.add_field(name=":no_entry_sign: Banned Status", value="✅ Not Banned!" if not banned_status else "❌ Banned!", inline=False)
                embed.add_field(name=":no_entry_sign: Ban Reason", value=ban_reason, inline=False)
                embed.add_field(name=":warning: Warnings", value=str(warnings), inline=False)
                embed.add_field(name=":game_die: Trivia Points", value=str(trivia_points), inline=False)

                embed.add_field(name=":speech_balloon: Messages Sent", value=str(messages_sent), inline=False)
                embed.add_field(name=":arrow_up: Level Up Notifications", value="✅ Enabled" if lvlup_noti else "❌ Disabled", inline=False)
                embed.add_field(name=":trophy: Achievement Notifications", value="✅ Enabled" if achievement_noti else "❌ Disabled", inline=False)
                embed.add_field(name=":moneybag: Rob Activated", value="✅ Activated" if rob_activated else "❌ Deactivated", inline=False)

                await ctx.send(embed=embed, ephemeral=True)
            else:
                await ctx.send(f"User '{username}' not found.", ephemeral=True)
                error_embed = nextcord.Embed(title="Error", description="❌ You do not have permission to view reports.", color=0xFF0000)
                await ctx.send(embed=error_embed, ephemeral=True)
    except Exception as e:
        error_embed = nextcord.Embed(title="Error", description=f"❌ An error occurred: {str(e)}", color=0xFF0000)
        await ctx.send(embed=error_embed, ephemeral=True)

# ✅ /weather

def degrees_to_direction(degrees):
    if 22.5 <= degrees < 67.5:
        return "Northeast"
    elif 67.5 <= degrees < 112.5:
        return "East"
    elif 112.5 <= degrees < 157.5:
        return "Southeast"
    elif 157.5 <= degrees < 202.5:
        return "South"
    elif 202.5 <= degrees < 247.5:
        return "Southwest"
    elif 247.5 <= degrees < 292.5:
        return "West"
    elif 292.5 <= degrees < 337.5:
        return "Northwest"
    else:
        return "North"

@bot.slash_command(
    name='weather',
    description='Get weather information for a city.'
)
@log_command('weather')
async def weather(ctx, city: str):
    user = ctx.user
    try:   
        if ctx.guild is None:
            embed = nextcord.Embed(
                title="⛔ Command Error",
                description="This command can only be used in Chill Lounge text channels.",
                color=0xFF5733
            )
            await ctx.send(embed=embed, ephemeral=True)
            return
        
        if update_active:
            update_embed = nextcord.Embed(
                title="🛠️ Update in Progress",
                description="A system update is currently in progress. Please try again later.",
                color=nextcord.Color.orange()
            )
            update_embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)
            await ctx.send(embed=update_embed, ephemeral=True)
            return
        
        if user.name in config and config[user.name]["banned_status"]:
            ban_embed = nextcord.Embed(title="❌ BANNED", description="You are banned! View your reason in your DMs.", color=0xFF0000)
            ban_embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)
            await ctx.send(embed=ban_embed, ephemeral=True)
            return
        
        formatted_city = city.replace(" ", "+")
        url = f"http://api.openweathermap.org/data/2.5/weather?q={formatted_city}&appid={api_key}"
        response = requests.get(url)
        data = json.loads(response.text)
        if response.status_code == 200:
            temperature_kelvin = data['main']['temp']
            temperature_celsius = temperature_kelvin - 273.15
            humidity = data['main']['humidity']
            weather_description = data['weather'][0]['description']
            wind_speed = data['wind']['speed']
            wind_deg = data['wind']['deg']

            wind_direction = degrees_to_direction(wind_deg)

            embed = nextcord.Embed(
                title=f"📍 Weather in {city}",
                color=nextcord.Color.blue()
            )
            embed.add_field(name="🌡️ Temperature", value=f"**{temperature_celsius:.2f}°C**", inline=True)
            embed.add_field(name="💧 Humidity", value=f"**{humidity}**%", inline=True)
            embed.add_field(name="🌦️ Weather Description", value=weather_description, inline=False)
            embed.add_field(name="🌬️ Wind Speed", value=f"**{wind_speed}** m/s", inline=True)
            embed.add_field(name="🧭 Wind Direction", value=wind_direction, inline=True)
            embed.set_footer(text="Remastered by @prodbyeagle | Original Code by @dwhincandi", icon_url=pic_link)

            await ctx.send(embed=embed, ephemeral=True)
        else:
            error_embed = nextcord.Embed(title="❌ ERROR", description="There was a problem fetching weather data.", color=0xFF0000)
            error_embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)
            await ctx.send(embed=error_embed, ephemeral=True)

    except Exception as e:
        error_embed = nextcord.Embed(
            title="Error",
            description=f"An error occurred: {str(e)}",
            color=nextcord.Color.red()
        )
        await ctx.send(embed=error_embed, ephemeral=True)

# ✅ /website

@bot.slash_command(
    name='website',
    description='Get a link to the website.'
)
@log_command('website')
async def website(ctx):
    user=ctx.user
    try:
        if ctx.guild is None:
            embed = nextcord.Embed(
                title="⛔ Command Error",
                description="This command can only be used in Chill Lounge text channels.",
                color=0xFF5733
            )
            await ctx.send(embed=embed, ephemeral=True)
            return
           
        if update_active:
            update_embed = nextcord.Embed(
                title="🛠️ Update in Progress",
                description="A system update is currently in progress. Please try again later.",
                color=nextcord.Color.orange()
            )
            update_embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)
            await ctx.send(embed=update_embed, ephemeral=True)
            return
        
        if user.name in config and config[user.name]["banned_status"]:
            ban_embed = nextcord.Embed(title="❌ BANNED", description="You are banned! View your reason in your DMs.", color=0xFF0000)
            ban_embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)
            await ctx.send(embed=ban_embed, ephemeral=True)
            return

        embed = nextcord.Embed(
            title="To our LinkTree!",
            url="https://linktr.ee/chilly.bot",
            color=nextcord.Color.magenta()
        )
        embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)

        await ctx.send(embed=embed, ephemeral=True)

    except Exception as e:
        error_embed = nextcord.Embed(
            title="Error",
            description=f"An error occurred: {str(e)}",
            color=nextcord.Color.red()
        )
        await ctx.send(embed=error_embed, ephemeral=True)

# ➖➖➖➖➖➖➖➖➖
        
# |\|/|\|\|/|\/|\|/|\/|\|/|\|\|/|\|/|\|\|

# ➖➖➖➖➖➖➖➖➖
# 𝓕𝓤𝓝 𝓐𝓡𝓔𝓐

# ✅ /dadjoke

ICANHAZDADJOKE_API_URL = 'https://icanhazdadjoke.com/'

@bot.slash_command(
    name='dadjoke',
    description='Get a random dad joke.'
)
@log_command('dadjoke')
async def joke(ctx):
    try:
        if ctx.guild is None:
            embed = nextcord.Embed(
                title="⛔ Command Error",
                description="This command can only be used in Chill Lounge text channels.",
                color=0xFF5733
            )
            await ctx.send(embed=embed, ephemeral=True)
            return
           
                       
        user = ctx.user
        
        if update_active:
            update_embed = nextcord.Embed(
                title="🛠️ Update in Progress",
                description="A system update is currently in progress. Please try again later.",
                color=nextcord.Color.orange()
            )
            update_embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)
            await ctx.send(embed=update_embed, ephemeral=True)
            return
        
        if user.name in config and config[user.name]["banned_status"]:
            ban_embed = nextcord.Embed(title="❌ BANNED", description="You are banned! View your reason in your DMs.", color=0xFF0000)
            ban_embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)
            await ctx.send(embed=ban_embed, ephemeral=True)
            return

        if user.name in cooldown_dict:
            remaining_time = COOLDOWN - (int(time.time()) - cooldown_dict[user.name])

            cooldown_embed = nextcord.Embed(
                title="⌚ **STOP**",
                description=f'Der Bot lacht gerade noch bisschen. Das dauert ca. ** {remaining_time} ** Sekunden.',
                color=nextcord.Color.red()
            )

            await ctx.send(embed=cooldown_embed, ephemeral=True)
            return

        response = requests.get(ICANHAZDADJOKE_API_URL, headers={'Accept': 'application/json'})

        if response.status_code == 200:
            joke_data = response.json()
            joke_text = joke_data['joke']

            joke_embed = nextcord.Embed(
                title="🤣 Dad Joke of the Day",
                description=joke_text,
                color=nextcord.Color.blue()
            )
            joke_embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)
            await ctx.send(embed=joke_embed, ephemeral=True)

            cooldown_dict[user.name] = int(time.time())
            await asyncio.sleep(COOLDOWN)
            del cooldown_dict[user.name]
        else:
            await ctx.send("❌ Failed to fetch a dad joke from the API.")
    except Exception as e:
        await ctx.send(f"❌ An error occurred: {str(e)}")

# ✅ /joke

COOLDOWN = 15
cooldown_dict = {}

@bot.slash_command(
    name='joke',
    description='Get a random joke of the day.'
)
@log_command('joke')
async def joke(ctx):
    try:
        if ctx.guild is None:
            embed = nextcord.Embed(
                title="⛔ Command Error",
                description="This command can only be used in Chill Lounge text channels.",
                color=0xFF5733
            )
            await ctx.send(embed=embed, ephemeral=True)
            return
           
        user = ctx.user
        
        if update_active:
            update_embed = nextcord.Embed(
                title="🛠️ Update in Progress",
                description="A system update is currently in progress. Please try again later.",
                color=nextcord.Color.orange()
            )
            update_embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)
            await ctx.send(embed=update_embed, ephemeral=True)
            return
        
        if user.name in config and config[user.name]["banned_status"]:
            ban_embed = nextcord.Embed(title="❌ BANNED", description="You are banned! View your reason in your DMs.", color=0xFF0000)
            ban_embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)
            await ctx.send(embed=ban_embed, ephemeral=True)
            return

        if user.name in cooldown_dict:
            remaining_time = COOLDOWN - (int(time.time()) - cooldown_dict[user.name])

            cooldown_embed = nextcord.Embed(
                title="⌚ **STOP**",
                description=f'Der Bot lacht gerade noch bisschen. Das dauert ca. ** {remaining_time} ** Sekunden.',
                color=nextcord.Color.red()
            )

            await ctx.send(embed=cooldown_embed, ephemeral=True)
            return

        joke = random.choice([
            '**What is a black person with a stick up their ass? Magnum Classic**',
            '**What is the difference between an Emo and a pizza? The pizza doesn\'t cut itself.**',
            '**A woman goes to the hospital and the doctor drops the baby. The woman says, "Are you crazy or what?" The doctor replies, "April, April! The baby was already dead."**',
            '**Witz 2**',
            '**What is the difference between Jesus and a fuck boy? The facial expression during nailing.**',
            '**What is the connection between parents and a pizza? When it\'s black, there\'s no food.**',
            '**Water was found on Mars. Mars 1:0 Africa**',
            '**Why are there no trains in Africa? Because everyone would ride in black.**',
            '**Why are there no medications in Africa? Because you have to take them with water.**',
            '**What is green and sits on the toilet? A poop bank.**',
            '**Why did the shark eat his sister? Because she turned blue.**',
            '**Why does a kangaroo always hop funny? Because the squirrel stole the spoon.**',
            '**Why does a cowboy always go around his horse? Because it\'s an all-around-the-clock horse.**',
            '**What happens when you mix cola and beer? Colabeer.**',
            '**Why was the pen sad? Because it always drew.**',
            '**What does a clown do in the office? Clown around.**',
            '**What do you call a boomerang that doesn\'t come back? A stick.**',
            '**Why doesn\'t a whale go to the psychiatrist? Because he has a good herring.**',
            '**What does a submarine do on dry land? Dry submarine diving.**',
            '**Why doesn\'t a frog have the internet? Because it\'s tired of the pond.**',
            '**What is written on the tombstone of a mathematician? He didn\'t count on this.**',
            '**What lies on the road and can whistle? A traffic cop.**',
            '**Why doesn\'t a fish drink? Because it always leaks water.**',
            '**Why don\'t skeletons accept challenges? Because they lack the nerves.**',
            '**What does a clown do in the office? Clown around.**',
            '**Why is the calculator sad? Because it has many problems.**',
            '**What do you do with a dog with no legs? Take it for a drag.**',
            '**What sits in the forest and waves? A hoo-hoo.**',
            '**Why don\'t frogs wear underwear? Because the swamp has the best winds.**',
            'https://i.redd.it/yowxj0j6j11b1.jpg'
        ])
        
        joke_embed = nextcord.Embed(
            title="🤣 Witz des Tages",
            description=joke,
            color=nextcord.Color.blue()
        )
        joke_embed.set_footer(text="Remastered by @prodbyeagle | Original Code by @dwhincandi", icon_url=pic_link)
        await ctx.send(embed=joke_embed, ephemeral=True)

        cooldown_dict[user.name] = int(time.time())
        await asyncio.sleep(COOLDOWN)
        del cooldown_dict[user.name]
    except Exception as e:
        await ctx.send(f"❌ An error occurred: {str(e)}")

# ✅ /rob

rob_cooldowns = {}

allowed_roles = ['⚙️ Developer']

@bot.slash_command(
    name='rob',
    description='Attempt to steal coins and xp from another user.'
)
@log_command('rob')
async def rob(ctx: nextcord.Interaction, user: nextcord.Member):
    try:
        if ctx.user == user:
            cannot_rob_self_embed = nextcord.Embed(
                title="❌ Robbery Failed",
                description="You cannot rob yourself!",
                color=nextcord.Color.red()
            )
            await ctx.send(embed=cannot_rob_self_embed, ephemeral=True)
            return

        if ctx.guild is None:
            embed = nextcord.Embed(
                title="⛔ Command Error",
                description="This command can only be used in Chill Lounge text channels.",
                color=0xFF5733
            )
            await ctx.send(embed=embed, ephemeral=True)
            return

        user_name = ctx.user.name.lower()
        if user_name in config and config[user_name]["banned_status"]:
            ban_embed = nextcord.Embed(title="❌ BANNED", description="You are banned! View your Reason in your DM's", color=0xFF0000)
            ban_embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)
            await ctx.send(embed=ban_embed, ephemeral=True)
            return

        user_name = str(user.name)
        if user_name in config and config[user_name]["banned_status"]:
            ban_embed = nextcord.Embed(
                title="❌ BANNED",
                description="This user is banned! View the reason in your DMs.",
                color=0xFF0000
            )
            ban_embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)
            await ctx.send(embed=ban_embed, ephemeral=True)
            return

        if update_active:
            update_embed = nextcord.Embed(
                title="🛠️ Update in Progress",
                description="A system update is currently in progress. Please try again later.",
                color=nextcord.Color.orange()
            )
            update_embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)
            await ctx.send(embed=update_embed, ephemeral=True)
            return

        if ctx.user.name in rob_cooldowns and not any(role.name in allowed_roles for role in ctx.user.roles):
            cooldown_embed = nextcord.Embed(
                title="🕰️ Cooldown",
                description=f'You are on cooldown. Please wait {rob_cooldowns[ctx.user.name]} seconds before trying again.',
                color=nextcord.Color.orange()
            )
            await ctx.send(embed=cooldown_embed, ephemeral=True)
            return

        if not any(role.name in allowed_roles for role in ctx.user.roles):
            rob_cooldowns[ctx.user.name] = 120
            while rob_cooldowns[ctx.user.name] > 0:
                await asyncio.sleep(1)
                rob_cooldowns[ctx.user.name] -= 1

        with open("chilly_config.json", "r") as file:
            config_data = json.load(file)

        user_data = config_data.get(user.name)
        if user_data and user_data.get("rob_activated", False):
            cannot_rob_embed = nextcord.Embed(
                title="❌ Robbery Failed",
                description=f"{user.mention} has activated protection against robberies.",
                color=nextcord.Color.red()
            )
            await ctx.send(embed=cannot_rob_embed, ephemeral=True)
            return

        with open('chilly_config.json', 'r') as file:
            xpcash_data = json.load(file)

        embed = nextcord.Embed()

        original_money = xpcash_data.get(str(user.name), {}).get('money', 0)

        chance = random.random()

        if chance <= 0.0001:
            coins_stolen = original_money
            xpcash_data[str(user.name)]['money'] -= coins_stolen
            xpcash_data[str(ctx.user.name)]['money'] += coins_stolen 

            with open('chilly_config.json', 'w') as file:
                json.dump(xpcash_data, file, indent=4)

            embed.title = f"🎉 JACKPOT"
            embed.description = f"OMG! YOU HAVE STOLEN {user.mention}'s 🪙 {round(coins_stolen)} COINS"
            embed.color = nextcord.Color.green()

        else:
            if random.uniform(0, 100) <= chance:
                max_stolen_percentage = min(25, random.randint(1, 75))
                stolen_coins = (max_stolen_percentage / 100) * original_money
                xpcash_data[str(user.name)]['money'] -= stolen_coins
                xpcash_data[str(ctx.user.name)]['money'] += stolen_coins

                stolen_xp = 0.05 * stolen_coins
                xpcash_data[str(ctx.user.name)]['xp'] += stolen_xp

                with open('chilly_config.json', 'w') as file:
                    json.dump(xpcash_data, file, indent=4)

                embed.title = f"🎉 Successful Robbery"
                embed.description = f"You successfully robbed {user.mention} of {round(stolen_coins)} 🪙 coins and received {round(stolen_xp)} XP!"
                embed.color = nextcord.Color.green()

            else:
                lost_coins_percentage = random.uniform(0.0001, 0.25)  
                lost_coins_amount = original_money * lost_coins_percentage 
                xpcash_data[str(ctx.user.name)]['money'] -= lost_coins_amount

                with open('chilly_config.json', 'w') as file:
                    json.dump(xpcash_data, file, indent=4)

                embed.title = f"❌ Robbery Failed"
                embed.description = f"The robbery at {user.mention} failed, and you lost {round(lost_coins_amount)} 🪙 coins."
                embed.color = nextcord.Color.red()

        await ctx.send(embed=embed, ephemeral=True)

    except Exception as e:
        error_embed = nextcord.Embed(
            title="Error",
            description=f"An error occurred: {str(e)}",
            color=nextcord.Color.red()
        )
        await ctx.send(embed=error_embed, ephemeral=True)
# ✅ /tic

class TicTacToeButton(nextcord.ui.Button["TicTacToe"]):
    def __init__(self, x: int, y: int):
        super().__init__(style=nextcord.ButtonStyle.secondary, label="\u200b", row=y)
        self.x = x
        self.y = y

    async def callback(self, interaction: nextcord.Interaction):
        assert self.view is not None
        view: TicTacToe = self.view
        status = view.board[self.y][self.x]
        if status in (view.X, view.O):
            return

        if view.current_player == view.X:
            self.style = nextcord.ButtonStyle.danger
            self.label = "X"
            self.disabled = True
            view.board[self.y][self.x] = view.X
            view.current_player = view.O
            content = "**It's O's turn now**"
        else:
            self.style = nextcord.ButtonStyle.success
            self.label = "O"
            self.disabled = True
            view.board[self.y][self.x] = view.O
            view.current_player = view.X
            content = "**It's X's turn now**"

        winner = view.check_board_winner()
        if winner is not None:
            if winner == view.X:
                content = "**X wins!**"
            elif winner == view.O:
                content = "**O wins!**"
            else:
                content = "**It's a tie!**"

            for item in view.children:
                item.disabled = True

            view.stop()

        await interaction.response.edit_message(content=content, view=view)

class TicTacToe(nextcord.ui.View):
    children: List[TicTacToeButton]
    X = -1
    O = 1
    Draw = 2

    def __init__(self):
        super().__init__()
        self.current_player = self.X
        self.board = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
        ]

        for x in range(3):
            for y in range(3):
                self.add_item(TicTacToeButton(x, y))

    def check_board_winner(self):
        for row in self.board:
            value = sum(row)
            if value == 3:
                return self.O
            elif value == -3:
                return self.X

        for column in range(3):
            value = self.board[0][column] + self.board[1][column] + self.board[2][column]
            if value == 3:
                return self.O
            elif value == -3:
                return self.X

        diagonal = self.board[0][2] + self.board[1][1] + self.board[2][0]
        if diagonal == 3:
            return self.O
        elif diagonal == -3:
            return self.X

        diagonal = self.board[0][0] + self.board[1][1] + self.board[2][2]
        if diagonal == 3:
            return self.O
        elif diagonal == -3:
            return self.X

        if all(i != 0 for row in self.board for i in row):
            return self.Draw

        return None

@bot.slash_command(
    name="tic",
    description="Starts a game of Tic-Tac-Toe.",
)
async def tictactoe(ctx):
    try:
        if ctx.guild is None:
            embed = nextcord.Embed(
                title="⛔ Command Error",
                description="This command can only be used in Chill Lounge text channels.",
                color=0xFF5733
            )
            await ctx.send(embed=embed, ephemeral=True)
            return
        
        user_name = ctx.user.name.lower()
        if user_name in config and config[user_name]["banned_status"]:
            ban_embed = nextcord.Embed(title="❌ BANNED", description="You are banned! View your Reason in your DM's", color=0xFF0000)
            ban_embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)
            await ctx.send(embed=ban_embed, ephemeral=True)
            return

        if update_active:
            update_embed = nextcord.Embed(
                title="🛠️ Update in Progress",
                description="A system update is currently in progress. Please try again later.",
                color=nextcord.Color.orange()
            )
            update_embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)
            await ctx.send(embed=update_embed, ephemeral=True)
            return

        await ctx.send("Tic Tac Toe: X starts", view=TicTacToe())
    except Exception as e:
        error_embed = nextcord.Embed(title="Error", description=f"❌ An error occurred: {str(e)}", color=0xFF0000)
        await ctx.send(embed=error_embed, ephemeral=True)


# ✅ /trivia
                
if not os.path.exists('chilly_quizdata.json'):
    with open('chilly_quizdata.json', 'w') as file:
        json.dump({}, file)

with open('chilly_quizdata.json', 'r') as file:
    fragen_und_antworten = json.load(file)

trivia_points = {}

@bot.slash_command(
    name='trivia',
    description='Start the Quiz'
)
@log_command('trivia')
async def start_trivia(ctx):   
    try:
        message = None

        if ctx.guild is None:
            embed = nextcord.Embed(
                title="⛔ Command Error",
                description="This command can only be used in Chill Lounge text channels.",
                color=0xFF5733
            )
            await ctx.send(embed=embed, ephemeral=True)
            return

        if update_active:
            update_embed = nextcord.Embed(
                title="🛠️ Update in Progress",
                description="A system update is currently in progress. Please try again later.",
                color=nextcord.Color.orange()
            )
            update_embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)
            await ctx.send(embed=update_embed, ephemeral=True)
            return

        if ctx.user.name in config and config[ctx.user.name]["banned_status"]:
            ban_embed = nextcord.Embed(title="❌ BANNED", description="You are banned! View your reason in your DMs.", color=0xFF0000)
            ban_embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)
            await ctx.send(embed=ban_embed, ephemeral=True)
            return

        user_name = str(ctx.user.name)

        with open('chilly_quizdata.json', 'r', encoding='utf-8') as file:
            questins_and_answers = json.load(file)

            question = random.choice(questins_and_answers)

            if nextcord.utils.get(ctx.user.roles, name='⚙️ Developer'):
                embed = nextcord.Embed(title='❓ Question', description=question["question"])
                embed.set_footer(text=f'Answer: {question["answer"]}')
            else:
                embed = nextcord.Embed(title='❓ Question', description=question["question"])

            message = await ctx.send(embed=embed, ephemeral=True)

            def check_answer(answer):
                return answer.author == ctx.user

            answer_message = await bot.wait_for('message', check=check_answer, timeout=60.0)

            if answer_message.content.lower() == question["answer"].lower():

                with open('chilly_config.json', 'r') as config_file:
                    player_data = json.load(config_file)

                if user_name in player_data:
                    if 'trivia_points' in player_data[user_name]:
                        player_data[user_name]['trivia_points'] += 1
                    else:
                        player_data[user_name]['trivia_points'] = 1
                else:
                    player_data[user_name] = {'trivia_points': 1}

                with open('chilly_config.json', 'w') as config_file:
                    json.dump(player_data, config_file, indent=4)

                new_points = player_data[user_name]['trivia_points']
                embed.title = '✅ Correct!'
                embed.description = f'You provided the correct answer.'
                embed.set_footer(text=f'Points: {new_points}', icon_url=pic_link)

                if message is not None:
                    await message.edit(embed=embed)
            else:
                embed = nextcord.Embed(title='❌ Wrong Answer!', description='The game has been aborted. The correct answer was: ' + question["answer"])
                if message is not None:
                    await message.edit(embed=embed)

    except asyncio.TimeoutError:
        embed = nextcord.Embed(title='🕛 Time Ran Out!', description='The correct answer was: ' + question["answer"])
        if message is not None:
            await message.edit(embed=embed)

    except Exception as e:
        error_embed = nextcord.Embed(title="❌ Error", description=f"An error occurred: {str(e)}", color=0xFF0000)
        if message is not None:
            await message.edit(embed=error_embed, ephemeral=True)

# ➖➖➖➖➖➖➖➖➖

# ENDE


bot.run(TOKEN)   
