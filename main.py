import discord
import json
import os
import asyncio
from discord.ext import commands
from discord.ext.commands import has_permissions

with open('config.json') as e:
    infos = json.load(e)
    TOKEN = infos['token']
    prefixo = infos['prefix']

client = commands.Bot(command_prefix=prefixo, intents=discord.Intents.all())
client.help_command = commands.MinimalHelpCommand()

@client.event
async def on_ready():
    print(f'\n{client.user.name} Online\nPrefix: {prefixo}\nInvite link: https://discord.com/oauth2/authorize?client_id={client.user.id}&scope=bot&permissions=3163144\n')
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=f"{prefixo}help | @{client.user.name}"))

@client.listen()
async def on_message(message):
    if message.content == f'<@!{client.user.id}>' or message.content == f'<@{client.user.id}>':
        await message.channel.send(f'**{message.author.mention} My prefix is: `{prefixo}`**')

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.reply('Cooldown command, try again in **{:.2f}** seconds'.format(error.retry_after), delete_after=5)

class MyHelp(commands.MinimalHelpCommand):

    def __init__(self):
        super().__init__(
            command_attrs={
                "cooldown": commands.Cooldown(1, 3, commands.BucketType.user),
                "aliases": ['h'],
                "description": "Command Help",
                "usage": f"{prefixo}help [command] or {prefixo}help [category]"
            }
        )

    async def send_bot_help(self, mapping):
        """Standard help command"""
        ctx = self.context
        embed = discord.Embed(title=f"{client.user.name} help", color=discord.Color.blurple())
        embed.set_thumbnail(url=client.user.avatar_url)
        embed.set_footer(text=f'use {prefixo}help [command] or {prefixo}help [category] for more information')
        usable = 0 
        for cog, commands in mapping.items():
                    if filtered_commands := await self.filter_commands(commands): 
                        
                        amount_commands = len(filtered_commands)
                        usable += amount_commands
                        if cog: 
                            name = cog.qualified_name
                            description = cog.description or "Without description"
                        else:
                            name = "Without category"
                            description = "Uncategorized Commands"

                        embed.add_field(name=f"{name} [{amount_commands}]", value=description, inline=True)


        await ctx.reply(embed=embed)

    async def send_command_help(self, command):
        """Send information about a command"""
        ctx = self.context
        embed = discord.Embed(title=command.name.upper(), description=command.description, color=discord.Color.green())
        alias = command.aliases
        if alias:
            embed.add_field(name="Aliases", value=", ".join(alias), inline=False)
        if command.usage != None:
            embed.add_field(name="How to use:", value=f'`{command.usage}`')

        await ctx.reply(embed=embed)

    async def send_error_message(self, error):
        """Error message"""
        ctx = self.context
        embed = discord.Embed(title="looks like something went wrong", description=error, colour=discord.Color.red())
        await ctx.reply(embed=embed)

    async def send_cog_help(self, cog):
        """Submit information about a category"""
        ctx = self.context
        title = cog.qualified_name
        embed = discord.Embed(
            title=title,
            description=cog.description,
            color=discord.Color.blue()
        )

        commands = cog.get_commands()

        if filtered_commands := await self.filter_commands(commands):
                    for command in filtered_commands:
                        embed.add_field(name=command, value=command.description or 'Without description')

        embed.set_footer(text=f'use {prefixo}help [command] for more information about commands')
        await ctx.reply(embed=embed)

client.help_command = MyHelp()

@client.command(aliases=['convite', 'convidar'], description='Bot invite', usage=f'{prefixo}invite')
async def invite(ctx):
    embed = discord.Embed(
        description=f'[click here to invite me](https://discord.com/oauth2/authorize?client_id={client.user.id}&scope=bot&permissions=3163144)',
        color = discord.Color.blurple()
    )
    await ctx.reply(embed=embed)

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')

client.run(TOKEN)
