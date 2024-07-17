import discord
from discord.ext import commands, tasks
import datetime
import pytz
import json
import asyncio
from typing import Union

intents = discord.Intents().all()
bot = commands.Bot(command_prefix=',', intents=intents)

# Configuration
staff_role_id = 1230027780352114749
category_ids = [1219674586543685712, 1234007202818162758, 1233661348315926528]

@bot.event
async def on_ready():
    print(f"{bot.user.name} is Ready")

@bot.event
async def on_message(message):
    await bot.process_commands(message)
    for category_id in category_ids:
        category = discord.utils.get(message.guild.categories, id=category_id)
        if category and message.channel.category == category:
            if "@here" in message.content:
                try:
                    with open("pingcount.json", "r") as file:
                        data = json.load(file)
                except FileNotFoundError:
                    data = []

                if not data:
                    dataz = {
                        "channelid": message.channel.id,
                        "time": datetime.datetime.now().strftime("%Y%m%d"),
                        "count": 0,
                        "owner": message.author.id
                    }
                    data.append(dataz)
                    with open("pingcount.json", "w") as file:
                        json.dump(data, file, indent=4)
                        await message.channel.send("1/2")
                        return

                for c in data:
                    if message.channel.id == c["channelid"]:
                        now_date = datetime.datetime.now().strftime("%Y%m%d")
                        slot_date = c["time"]

                        if now_date == slot_date:
                            count = c["count"] + 1
                            if count == 3:
                                channel = bot.get_channel(c["channelid"])
                                owner = message.guild.get_member(c["owner"])
                                await channel.set_permissions(owner, read_messages=False)
                                await channel.set_permissions(message.guild.default_role, send_messages=False)  
                                await channel.edit(name=f"revoked-{channel.name}")
                                embed = discord.Embed(description=f"3/2 Slot Revoked <@&{staff_role_id}>\n**Reason:** 3 here ping", color=0xFF0000)
                                await message.channel.send(embed=embed)

                                mute_role = message.guild.get_role(1232590257925390407)
                                await message.author.add_roles(mute_role)

                                return
                            embed = discord.Embed(description=f"<@{c['owner']}> , you just did {count}/2 | MUST USE MM", color=0xFFFF00) 
                            await message.channel.send(embed=embed)
                            c["count"] = count
                            with open("pingcount.json", "w") as file:
                                json.dump(data, file, indent=4)
                            return
                        else:
                            c["time"] = now_date
                            c["count"] = 1
                            with open("pingcount.json", "w") as file:
                                json.dump(data, file, indent=4)
                            embed = discord.Embed(description=f"<@{c['owner']}> , you just did 1/2 | MUST USE MM", color=0xFFFF00)  
                            await message.channel.send(embed=embed)

                datazx = {
                    "channelid": message.channel.id,
                    "time": datetime.datetime.now().strftime("%Y%m%d"),
                    "count": 1,
                    "owner": message.author.id
                }
                data.append(datazx)
                with open("pingcount.json", "w") as file:
                    json.dump(data, file, indent=4)
                    embed = discord.Embed(description=f"<@{message.author.id}> , you just did 1/2 | MUST USE MM", color=0xFFFF00)  
                    await message.channel.send(embed=embed)
            elif "@everyone" in message.content:
                try:
                    mute_role = message.guild.get_role(1232590257925390407)
                    await message.author.add_roles(mute_role)
                    await message.channel.set_permissions(message.author, read_messages=False)
                    await message.channel.set_permissions(message.guild.default_role, send_messages=False)
                    await message.channel.edit(name=f"revoked-{message.channel.name}")
                    embed = discord.Embed(description="Slot revoked due to @everyone mention. User timed out for 24 hours.", color=0xFF0000)
                    await message.channel.send(embed=embed)
                    return
                except Exception as e:
                    print(f"Error: {e}")

@bot.command()
@commands.has_role(staff_role_id)
async def create(ctx, member: discord.Member=None, category: discord.CategoryChannel=None, duration: str=None):
    if member is None:
        await ctx.reply("User not found.")
        return

    if category is None:
        await ctx.reply("Category not found.")
        return

    if duration is None:
        await ctx.reply("Please provide a duration for the slot (e.g., `30d`).")
        return

    # Convert duration to seconds
    duration_seconds = convert_duration(duration)
    if duration_seconds is None:
        await ctx.reply("Invalid duration format. Please use 'xd', 'xh', or 'xm' (e.g., `1d`, `2h`, `30m`).")
        return

    # Clean member name for channel creation
    channel_name = f"〞ʚ・{member.display_name}".replace(" ", "-")  # Replace spaces with hyphens

    # Create the channel
    overwrites = {
        ctx.guild.default_role: discord.PermissionOverwrite(view_channel=True, send_messages=False),
        member: discord.PermissionOverwrite(view_channel=True, send_messages=True, mention_everyone=True)  # Prevent everyone mention
    }

    channel = await category.create_text_channel(channel_name, overwrites=overwrites)

    # Add role to the user
    role =  ctx.guild.get_role(1251936396076253282)
    await member.add_roles(role)

    # Calculate start and end time in IST
    start_time_ist = datetime.datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%d/%m/%Y - %H:%M:%S IST")
    end_time = datetime.datetime.now() + datetime.timedelta(seconds=duration_seconds)
    end_time_ist = end_time.astimezone(pytz.timezone('Asia/Kolkata')).strftime("%d/%m/%Y - %H:%M:%S IST")

    # Slot rules
    slot_rules = (
        "Slot Rules:\n"
        "√ 2 here pings per day.\n"
        "√ No @everyone ping or role ping.\n"
        "√ No refund on private slot.\n"
        "√ You can't sell or share your slot.\n"
        "√ Any kind of promotion is not allowed.\n"
        "√ Gambling/money doubling not allowed.\n"
        "√ You need 15+ vouches in Shiba to post your autobuy links.\n"
        "√ You can ping @here 2 times per day to your slot. This day is based on Indian time zone (GMT+5.30).\n"
        "»» If you disobey any of these rules, slot will be revoked without refund.\n\n"
    )

    # Send slot rules
    embed = discord.Embed(description=slot_rules, color=0xa102ee)
    embed.set_author(name="Slot Rules")
    await channel.send(embed=embed)

    # Send slot owner, start time, and end time message
    embed = discord.Embed(description=f"**Slot Owner:** {member.mention}\n**Start Time:** {start_time_ist}\n**End Time (IST):** {end_time_ist}", color=0xFFFF00)
    embed.set_footer(text=ctx.guild.name)
    embed.set_author(name=member)
    await channel.send(embed=embed)

    await ctx.reply(f"Successfully created slot for {member.mention} in {category.mention} for {duration}")

    # Timer for slot end notification
    await asyncio.sleep(duration_seconds)
    embed = discord.Embed(description=f"{member.mention} Your slot has ended.", color=0xFF0000)
    await channel.send(embed=embed)
    await channel.set_permissions(member, send_messages=False)

@bot.command()
@commands.has_role(staff_role_id)
async def add(ctx, member: discord.Member = None, channel: discord.TextChannel = None):
    if not member:
        await ctx.reply("Member not found.")
        return

    if not channel:
        await ctx.reply("Channel not found.")
        return

    await channel.set_permissions(member, view_channel=True, send_messages=True, mention_everyone=False)  # Prevent everyone mention
    await ctx.reply("Successfully added.")

@bot.command()
@commands.has_role(staff_role_id)
async def remove(ctx, member: discord.Member = None, channel: discord.TextChannel = None):
    if not member:
        await ctx.reply("Member not found.")
        return

    if not channel:
        await ctx.reply("Channel not found.")
        return

    await channel.set_permissions(member, send_messages=False, mention_everyone=False)  # Prevent everyone mention
    await ctx.reply("Successfully removed.")

@bot.command()
@commands.has_role(staff_role_id)
async def hold(ctx, member: discord.Member = None, channel: discord.TextChannel = None):
    if not member:
        await ctx.reply("Member not found.")
        return

    if not channel:
        await ctx.reply("Channel not found.")
        return

    await channel.set_permissions(member, send_messages=False)
    await ctx.reply("Successfully put the slot on hold.")

@bot.command()
@commands.has_role(staff_role_id)
async def unhold(ctx, member: discord.Member = None, channel: discord.TextChannel = None):
    if not member:
        await ctx.reply("Member not found.")
        return

    if not channel:
        await ctx.reply("Channel not found.")
        return

    await channel.set_permissions(member, send_messages=True, mention_everyone=True)
    await ctx.reply("Successfully removed hold from the slot.")

def convert_duration(duration: str) -> Union[int, None]:
    if duration.endswith("d"):
        try:
            days = int(duration[:-1])
            return days * 24 * 60 * 60
        except ValueError:
            return None
    elif duration.endswith("h"):
        try:
            hours = int(duration[:-1])
            return hours * 60 * 60
        except ValueError:
            return None
    elif duration.endswith("m"):
        try:
            minutes = int(duration[:-1])
            return minutes * 60
        except ValueError:
            return None
    else:
        return None

bot.run("")
