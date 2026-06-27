#!/usr/bin/env python3
import discord
from discord.ext import commands
import requests
from Crypto.Cipher import AES
import os

# Bot configuration — load secrets from environment variables ONLY
DISCORD_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
PREFIX = '/'
DEFAULT_JWT = os.getenv('FF_JWT_TOKEN', '')

# FreeFire API Constants
URL = "https://client.ind.freefiremobile.com/CheckDirtyWords"
AES_KEY = b'Yg&tc%DEuh6%Zc^8'
AES_IV = bytes.fromhex('366f795a4472323245337963686a4d25')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=PREFIX, intents=intents)
bot.tree.command_check = None  # Allow commands in DMs

def check_nickname(nickname: str, token: str = None):
    try:
        nickname_bytes = nickname.encode('utf-8')
        if len(nickname_bytes) > 12:
            nickname_bytes = nickname_bytes[:12]
        data = bytearray([0x0A, 0x0A])
        data.extend(nickname_bytes)
        padding_needed = 16 - len(data)
        data.extend([0x04] * padding_needed)
        cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
        payload = cipher.encrypt(bytes(data))

        headers = {
            'Authorization': f'Bearer {token or DEFAULT_JWT}',
            'X-Unity-Version': '2018.4.11f1',
            'X-GA': 'v1 1',
            'ReleaseVersion': 'OB50',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Content-Length': '16',
            'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 9; SM-S901E Build/SP1A.210812.016)',
            'Host': 'client.ind.freefiremobile.com',
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip',
        }
        response = requests.post(URL, data=payload, headers=headers, timeout=10)
        return {
            'status_code': response.status_code,
            'content': response.content.decode('utf-8', errors='ignore'),
            'is_clean': response.status_code == 200 and len(response.content) == 0,
            'is_dirty': response.status_code == 400 and b'BR_CONTENT_DIRTY_WORD' in response.content,
            'raw': response.content
        }
    except Exception as e:
        return {
            'status_code': 0,
            'content': str(e),
            'is_clean': False,
            'is_dirty': False,
            'error': True
        }

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print('Syncing slash commands...')
    await bot.tree.sync()
    print('Slash commands synced!')

@bot.tree.command(name='check', description='Check if a word is considered inappropriate in FreeFire')
async def check_word(interaction: discord.Interaction, word: str):
    await interaction.response.defer()
    processing_msg = await interaction.followup.send(f'🔍 Checking word: **{word}**...')
    result = check_nickname(word)
    embed = discord.Embed(
        title="🛡️ FreeFire Badword Detector",
        color=discord.Color.green() if result['is_clean'] else discord.Color.red()
    )
    embed.add_field(name="Word", value=f"`{word}`", inline=False)
    if result.get('error'):
        embed.color = discord.Color.orange()
        embed.add_field(name="❌ Error", value=f"``````", inline=False)
    elif result['is_dirty']:
        embed.add_field(name="Status", value="🚫 **BAD WORD DETECTED**", inline=False)
        embed.add_field(name="Response", value=f"``````", inline=False)
        embed.set_footer(text="This nickname contains prohibited words")
    elif result['is_clean']:
        embed.add_field(name="Status", value="✅ **CLEAN**", inline=False)
        embed.add_field(name="Response", value="``````", inline=False)
        embed.set_footer(text="This nickname is safe to use")
    else:
        embed.color = discord.Color.orange()
        embed.add_field(name="Status", value="⚠️ **UNKNOWN**", inline=False)
        embed.add_field(name="HTTP Status", value=f"`{result['status_code']}`", inline=False)
    await processing_msg.delete()
    await interaction.followup.send(embed=embed)

@bot.tree.command(name='bulk', description='Check multiple words at once (max 10, separate with spaces)')
async def bulk_check(interaction: discord.Interaction, words: str):
    word_list = words.split()
    if not word_list:
        await interaction.response.send_message('❌ **Usage:** `/bulk words:word1 word2 word3`\n**Example:** `/bulk words:Test Hello World`')
        return
    if len(word_list) > 10:
        await interaction.response.send_message('❌ Maximum 10 words at once!')
        return
    await interaction.response.defer()
    processing_msg = await interaction.followup.send(f'🔍 Checking {len(word_list)} words...')
    results = []
    for word in word_list:
        result = check_nickname(word)
        results.append((word, result))
    embed = discord.Embed(
        title="🛡️ FreeFire Badword Detector - Bulk Check",
        color=discord.Color.blue()
    )
    clean_count = sum(1 for _, r in results if r['is_clean'])
    dirty_count = sum(1 for _, r in results if r['is_dirty'])
    embed.add_field(name="📊 Summary",
                   value=f"✅ Safe words: **{clean_count}**\n🚫 Bad words: **{dirty_count}**",
                   inline=False)
    for word, result in results:
        status = "✅" if result['is_clean'] else "🚫" if result['is_dirty'] else "⚠️"
        embed.add_field(name=f"{status} {word}",
                       value="Safe" if result['is_clean'] else "Bad Word" if result['is_dirty'] else "Unknown",
                       inline=True)
    await processing_msg.delete()
    await interaction.followup.send(embed=embed)

@bot.tree.command(name='help_ff', description='Show help information')
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🛡️ FreeFire Badword Detector",
        description="Check if words are considered inappropriate according to Garena's FreeFire filters",
        color=discord.Color.blue()
    )
    embed.add_field(
        name="/check",
        value="Check a single word\n**Example:** `/check word:Hello`",
        inline=False
    )
    embed.add_field(
        name="/bulk",
        value="Check multiple words (max 10, separated by spaces)\n**Example:** `/bulk words:Hello World Test`",
        inline=False
    )
    embed.add_field(
        name="Response Types",
        value="✅ **Safe** - Word is allowed\n🚫 **Bad Word** - Word is prohibited\n⚠️ **Unknown** - Unexpected response",
        inline=False
    )
    embed.set_footer(text="Made for FreeFire word verification")
    await interaction.response.send_message(embed=embed)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f'❌ Missing required argument. Use `{PREFIX}help_ff` for usage info.')
    elif isinstance(error, commands.CommandNotFound):
        pass
    else:
        await ctx.send(f'❌ An error occurred: {str(error)}')

if __name__ == '__main__':
    if not DISCORD_TOKEN:
        print("❌ Please set your Discord bot token!")
        print("Set environment variable: export DISCORD_BOT_TOKEN='your_token_here'")
        exit(1)
    if not DEFAULT_JWT:
        print("⚠️  Warning: FF_JWT_TOKEN not set. Bad word checking will fail.")
        print("Set environment variable: export FF_JWT_TOKEN='your_jwt_token_here'")
    bot.run(DISCORD_TOKEN)

