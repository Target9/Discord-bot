import asyncio
import discord
from discord.ext import commands, tasks
import sqlite3
import random
import datetime

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Remove the default help command
bot.help_command = None  # <-- This is the line you should add.

# Loading the database
connection = sqlite3.connect("economy_bot.db")
cursor = connection.cursor()

admin_commands_list = ['checkdb', 'adjust', 'banuser', 'unbanuser', 'reloadbot']

failed_attempts = {}


@bot.command(name='help')
async def _help(ctx, category=None):
    if category == "admin":
        embed = discord.Embed(title="Admin Commands", description="List of all the admin commands.", color=discord.Color.blue())
        for command_name in admin_commands_list:
            cmd = bot.get_command(command_name)
            embed.add_field(name=cmd.name, value=cmd.help, inline=False)
        await ctx.send(embed=embed)
    else:
        # For all commands
        embed = discord.Embed(title="Commands", description="List of all commands.", color=discord.Color.green())
        
        # Here we will add all commands except the ones in admin_commands_list
        for command in bot.commands:
            if command.name not in admin_commands_list and command.name != "help":
                embed.add_field(name=command.name, value=command.help, inline=False)
        
        await ctx.send(embed=embed)


@bot.event
async def on_ready():
    print(f"Bot is ready!")
    give_daily_spam.start()  # Start the daily spam giving task

@tasks.loop(hours=24)  # This will run every 24 hours
async def give_daily_spam():
    # Give every user 5 spam every day
    cursor.execute("UPDATE users SET spam = spam + 50")
    connection.commit()

@bot.command()
async def register(ctx):
    """Register the user in the database."""
    cursor.execute("INSERT OR IGNORE INTO users (id, doubloons, spam, factories, diamond_spam) VALUES (?, 0, 0, 0, 0)", (ctx.author.id,))
    connection.commit()
    await ctx.send(f"Registered {ctx.author.mention}!")

@bot.command()
async def inventory(ctx, member: discord.Member = None):
    """Check the inventory of a specified user or your own"""
    
    # If no member is provided, show the inventory of the author
    if not member:
        member = ctx.author

    cursor.execute("SELECT doubloons, spam, factories, diamond_spam FROM users WHERE id = ?", (member.id,))
    user = cursor.fetchone()
    
    if user:
        doubloons, spam, factories, diamond_spam = user
        await ctx.send(f"**Inventory of {member.mention}:**\nDoubloons: {doubloons}\nSpam: {spam}\nFactories: {factories}\nDiamond Spam: {diamond_spam}")
    else:
        await ctx.send(f"{member.mention}, you're not registered! Use `!register` to register.")

@bot.command()
async def buyfactory(ctx):
    """Buy a spam factory for 100 doubloons."""
    cursor.execute("SELECT doubloons FROM users WHERE id = ?", (ctx.author.id,))
    doubloons = cursor.fetchone()[0]
    if doubloons < 100:
        await ctx.send(f"{ctx.author.mention}, you don't have enough doubloons to buy a factory!")
    else:
        cursor.execute("UPDATE users SET doubloons = doubloons - 100, factories = factories + 1 WHERE id = ?", (ctx.author.id,))
        connection.commit()
        await ctx.send(f"{ctx.author.mention}, you've bought a factory! It'll produce 3 spam every day.")

@bot.command()
async def sellspam(ctx, amount: int):
    """Sell your spam for doubloons. Every 10 spam is 1 doubloon."""
    
    # Ensure amount is a minimum of 10 and a multiple of 10
    if amount < 10 or amount % 10 != 0:
        await ctx.send(f"{ctx.author.mention}, you can only sell spam in multiples of 10 and a minimum of 10!")
        return

    # Check if the user has enough spam to sell
    cursor.execute("SELECT spam FROM users WHERE id = ?", (ctx.author.id,))
    user_spam = cursor.fetchone()[0]
    if user_spam < amount:
        await ctx.send(f"{ctx.author.mention}, you don't have enough spam to sell!")
        return

    # Convert the amount of spam to doubloons
    earned_doubloons = amount // 10

    cursor.execute("UPDATE users SET doubloons = doubloons + ?, spam = spam - ? WHERE id = ?", (earned_doubloons, amount, ctx.author.id))
    connection.commit()
    await ctx.send(f"{ctx.author.mention}, you sold {amount} spam for {earned_doubloons} doubloons!")

@bot.command()
async def buydiamondspam(ctx):
    """Buy diamond spam for 1000 doubloons."""
    cursor.execute("SELECT doubloons FROM users WHERE id = ?", (ctx.author.id,))
    doubloons = cursor.fetchone()[0]
    if doubloons < 1000:
        await ctx.send(f"{ctx.author.mention}, you don't have enough doubloons to buy a diamond spam!")
    else:
        cursor.execute("UPDATE users SET doubloons = doubloons - 1000, diamond_spam = diamond_spam + 1 WHERE id = ?", (ctx.author.id,))
        connection.commit()
        await ctx.send(f"{ctx.author.mention}, you've bought a diamond spam!")

SPAM_COST_TRIVIA = 3
SPAM_COST_GUESSNUMBER = 5

@bot.command()
async def trivia(ctx):
    """Play a trivia game for 3 spam."""
    # Check if the user has enough spam to play
    cursor.execute("SELECT spam FROM users WHERE id = ?", (ctx.author.id,))
    user_spam = cursor.fetchone()[0]
    if user_spam < SPAM_COST_TRIVIA:
        await ctx.send(f"{ctx.author.mention}, you need {SPAM_COST_TRIVIA} spam to play Trivia! You currently have {user_spam} spam.")
        return

    # Deduct the cost of playing from the user's spam
    cursor.execute("UPDATE users SET spam = spam - ? WHERE id = ?", (SPAM_COST_TRIVIA, ctx.author.id,))
    connection.commit()

    questions = {
    "What is the capital of France?": "paris",
    "Which planet is known as the Red Planet?": "mars",
    "What is the largest mammal?": "blue whale",
    "Who wrote 'Romeo and Juliet'?": "william shakespeare",
    "In which year did World War II end?": "1945",
    "What's the biggest animal in the world?": "blue whale",
    "How many players are there in a standard football team?": "11",
    "Which metal is heavier, silver or gold?": "gold",
    "Which planet is closest to the sun?": "mercury",
    "How many bones does the human adult body have?": "206",
    "Which is the smallest prime number?": "2",
    "What is the biggest planet in our solar system?": "jupiter",
    "What's the tallest mountain in the world?": "mount everest",
    "How many elements are there in the periodic table?": "118",
    "What is the symbol for gold in the periodic table?": "au",
    "Which country is known as the Land of the Rising Sun?": "japan",
    "Who painted the Mona Lisa?": "leonardo da vinci",
    "Which mammal is capable of true flight?": "bat",
    "What is the most eaten food in the world?": "rice",
    "Which fruit is known as the king of fruits?": "mango",
    "In which direction does the sunrise?": "east",
    "What is the top color in a rainbow?": "red",
    "Which gas do plants absorb from the atmosphere?": "carbon dioxide",
    "How many continents are there on Earth?": "7",
    "Which organ covers the entire body and protects it?": "skin"
}

    
    question, answer = random.choice(list(questions.items()))
    await ctx.send(f"Trivia Question: {question}\nYou have 15 seconds to answer.")
    
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == answer

    try:
        response = await bot.wait_for('message', timeout=15.0, check=check)
        if response:
            reward = random.randint(5, 10)
            cursor.execute("UPDATE users SET spam = spam + ? WHERE id = ?", (reward, ctx.author.id))
            connection.commit()
            await ctx.send(f"Correct, {ctx.author.mention}! You've earned {reward} spam.")
    except asyncio.TimeoutError:
        await ctx.send(f"Time's up! The correct answer was: {answer}.")

@bot.command()
async def guessnumber(ctx):
    """Play the 'Guess the Number' game for 5 spam."""

    # Check if the user has enough spam to play
    cursor.execute("SELECT spam FROM users WHERE id = ?", (ctx.author.id,))
    user_spam = cursor.fetchone()[0]
    if user_spam < SPAM_COST_GUESSNUMBER:
        await ctx.send(f"{ctx.author.mention}, you need {SPAM_COST_GUESSNUMBER} spam to play 'Guess the Number'! You currently have {user_spam} spam.")
        return

    # Deduct the cost of playing from the user's spam
    cursor.execute("UPDATE users SET spam = spam - ? WHERE id = ?", (SPAM_COST_GUESSNUMBER, ctx.author.id,))
    connection.commit()

    number = random.randint(1, 100)
    await ctx.send(f"{ctx.author.mention}, I'm thinking of a number between 1 and 100. You have 6 attempts to guess it!")
    
    for attempt in range(6):
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel and m.content.isdigit()

        try:
            response = await bot.wait_for('message', timeout=20.0, check=check)
            guess = int(response.content)
            
            if guess == number:
                reward = random.randint(10, 20)
                cursor.execute("UPDATE users SET spam = spam + ? WHERE id = ?", (reward, ctx.author.id))
                connection.commit()
                await ctx.send(f"Congratulations, {ctx.author.mention}! You've guessed the number and earned {reward} spam.")
                return
            elif guess < number:
                await ctx.send("Too low! Try a higher number.")
            else:
                await ctx.send("Too high! Try a lower number.")
        except asyncio.TimeoutError:
            await ctx.send(f"You took too long! You have {4 - attempt} attempts left.")

    await ctx.send(f"Sorry, you're out of attempts! The number was {number}.")

@bot.event
async def on_message(message):
    with open('logs.txt', 'a') as f:
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if message.guild:  # Check if the message is in a guild
            f.write(f"{timestamp} - {message.guild.name} - {message.channel.name} - {message.author.name}: {message.content}\n")
        else:  # Handle DMs
            f.write(f"{timestamp} - DM - {message.author.name}: {message.content}\n")

    # Process the message for commands
    await bot.process_commands(message)

ADMIN_CODE = "monkey123"

async def ask_for_admin_code(ctx):
    user_id = ctx.author.id
    # Check for existing failed attempts and lockout
    if user_id in failed_attempts:
        last_failed, attempts = failed_attempts[user_id]
        if attempts >= 5:
            # Check if the lockout period has passed
            if datetime.datetime.now() - last_failed < datetime.timedelta(minutes=5):
                await ctx.author.send("Too many failed attempts. Please wait for 5 minutes before trying again.")
                return False
            else:
                # Remove the user from failed attempts after the lockout period
                del failed_attempts[user_id]

    def check(m):
        return m.author == ctx.author and isinstance(m.channel, discord.DMChannel)

    try:
        prompt = await ctx.author.send("Please provide the admin code for verification:")
        response = await bot.wait_for('message', check=check, timeout=60)
        if response.content == ADMIN_CODE:
            return True
        else:
            # Increase the failed attempt count and notify the user
            failed_attempts[user_id] = (datetime.datetime.now(), failed_attempts.get(user_id, (datetime.datetime.now(), 0))[1] + 1)
            await ctx.author.send("Incorrect code. Please try writing the command again.")
            # Check for too many failed attempts and notify if needed
            if failed_attempts[user_id][1] >= 5:
                await ctx.author.send("Too many failed attempts. You are locked out for 5 minutes.")
            return False
    except asyncio.TimeoutError:
        await ctx.author.send("You took too long to provide the code.")
        return False

@bot.command()
async def checkdb(ctx, *members: discord.Member):
    """[Admin Tool] Check the database entry of any user or all users."""
    if not await ask_for_admin_code(ctx):
        return

    column_names = ["ID", "Doubloons", "Spam", "Factories", "Diamond_Spam"]

    if not members:  # No members specified, fetch entire DB
        cursor.execute("SELECT * FROM users")
        all_users = cursor.fetchall()
        if all_users:
            msg = "Full Database Entries:\n"
            await ctx.send(msg)  # Sending the initial message
            msg = ""  # Reset the msg variable for further use

            for user in all_users:
                member_mention = f"ID {user[0]} (Not in server or DM)"
                if ctx.guild:
                    member = ctx.guild.get_member(user[0])  # Fetching member object for the user ID
                    if member:  # If member is found in the guild
                        member_mention = member.mention
                
                user_details = ", ".join([f"{col}: {val}" for col, val in zip(column_names, user)])
                msg += f"{member_mention}: {user_details}\n"

                if len(msg) > 1900:  # Discord message length limit precaution
                    await ctx.send(msg)
                    msg = ""
            if msg:
                await ctx.send(msg)
        else:
            await ctx.send("No entries in the database.")
    else:  # If specific members are mentioned
        for member in members:
            cursor.execute("SELECT * FROM users WHERE id = ?", (member.id,))
            user = cursor.fetchone()
            if user:
                user_details = ", ".join([f"{col}: {val}" for col, val in zip(column_names, user)])
                await ctx.send(f"Database entry for {member.mention}: {user_details}")
            else:
                await ctx.send(f"{member.mention} is not registered in the database.")

@bot.command()
async def adjust(ctx, member: discord.Member, column: str, value: int):
    """[Admin Tool] Manually adjust the database values of any user."""
    if not await ask_for_admin_code(ctx):
        return
    if column not in ['doubloons', 'spam', 'factories', 'diamond_spam']:
        await ctx.send("Invalid column name.")
        return
    cursor.execute(f"UPDATE users SET {column} = ? WHERE id = ?", (value, member.id))
    connection.commit()
    await ctx.send(f"Updated {column} for {member.mention} to {value}.")

@bot.command()
async def banuser(ctx, member: discord.Member):
    """[Admin Tool] Ban a user from using the bot."""
    if not await ask_for_admin_code(ctx):
        return
    await member.add_roles(discord.utils.get(ctx.guild.roles, name="BannedFromBot"))
    await ctx.send(f"{member.mention} has been banned from using the bot.")

@bot.command()
async def unbanuser(ctx, member: discord.Member):
    """[Admin Tool] Unban a user from using the bot."""
    if not await ask_for_admin_code(ctx):
        return
    await member.remove_roles(discord.utils.get(ctx.guild.roles, name="BannedFromBot"))
    await ctx.send(f"{member.mention} has been unbanned from using the bot.")

@bot.command()
async def reloadbot(ctx):
    """[Admin Tool] Reloads the bot to incorporate on-the-fly changes."""
    if not await ask_for_admin_code(ctx):
        return
    await ctx.send("Reloading the bot...")
    await bot.close()

@bot.event
async def on_command_error(ctx, error):
    """A global error handler."""
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("You're missing a required argument for this command.")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send(f"The command '{ctx.message.content.split()[0][1:]}' was not found.")
    else:
        await ctx.send(f"An unexpected error occurred: {error}")

bot.run("***************************") #Your discord token here
