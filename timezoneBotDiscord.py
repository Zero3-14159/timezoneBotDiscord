import discord
from discord.ext import commands
import pytz
import json
import os
import datetime


intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    print("Bot is ready to receive commands.")

@bot.command()
async def findId(ctx, channel: discord.TextChannel = None):
    if channel is None:
        channel = ctx.channel
    await ctx.send(f"Channel ID: {channel.id}\nChannel Name: {channel.name}")

@bot.command()  # Test command to show all timezones
@commands.has_permissions(administrator=True)
async def timezones(ctx):
    try:
        timezones = pytz.all_timezones
        chunk_size = 50  # number of timezones per message
        for i in range(0, len(timezones), chunk_size):
            chunk = timezones[i:i+chunk_size]
            message = '\n'.join(chunk)
            await ctx.send(message)
    except Exception as e:
        await ctx.send(f"Error fetching timezones: {e}")

@bot.command()
async def set_timezone(ctx, timezone: str):
    if ctx.channel.id != 1376916275900715070:  # Replace with your timezone channel ID
        await ctx.send("Please set your timezone in the #timezones channel.")
        return

    user_id = str(ctx.author.id)

    if timezone in pytz.all_timezones:
        try:
            # Load existing data
            if os.path.exists("timezones.json"):
                with open("timezones.json", "r") as f:
                    user_timezones = json.load(f)
            else:
                user_timezones = {}

            # Update and save
            user_timezones[user_id] = timezone
            with open("timezones.json", "w") as f:
                json.dump(user_timezones, f, indent=4)

            await ctx.send(f"Timezone set to `{timezone}` for {ctx.author.name}.")
        except Exception as e:
            await ctx.send(f"Error setting timezone: {e}")
    else:
        await ctx.send(f"Invalid timezone. Please refer to the list pinned in #timezones.")

@bot.command()
async def get_timezone(ctx, member: discord.Member = None):
    # Ensure the command is used in the correct channel
    if ctx.channel.id != 1376916275900715070:
        await ctx.send("Please check your timezone in the #timezones channel.")
        return

    now_utc = datetime.datetime.now(datetime.timezone.utc)

    # If no member is provided, use the command invoker
    if member is None:
        member = ctx.author

    user_id = str(member.id)

    # Load the timezones if the file exists
    if os.path.exists("timezones.json"):
        try:
            with open("timezones.json", "r") as f:
                user_timezones = json.load(f)

            timezone = user_timezones.get(user_id, None)

            if timezone:
                # Convert UTC to the user's timezone
                user_timezone = pytz.timezone(timezone)
                user_time = now_utc.astimezone(user_timezone)
                formatted_time = user_time.strftime('%Y-%m-%d %H:%M:%S %Z%z')

                # Create the embed
                embed = discord.Embed(
                    title=f"Timezone Info for {member.name}",
                    description=f"Here is {member.name}'s local time in their set timezone.",
                    color=discord.Color.blue()  # You can customize the color
                )
                embed.add_field(name="Timezone", value=timezone, inline=False)
                embed.add_field(name="Local Time", value=formatted_time, inline=False)
                embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar.url)
                
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"{member.name} has not set a timezone.")
        except Exception as e:
            await ctx.send(f"Error fetching timezone: {e}")
    else:
        await ctx.send("No timezones have been set yet.")

# Token should be stored in an environment variable or a separate config file
bot.run('MTM3MzAwNDEzNzcyOTQ5NTA3MA.G1ahWn.erCpjH8mUMpdZIithpHlc9hlogc0J4HZV9Gcxg')
