import discord
from discord.ext import commands
import ujson
import os
import copy
import asyncio
import traceback
import time
import subprocess


class PerformanceMocker:
    """A mock object that can also be used in await expressions."""

    def __init__(self):
        self.loop = asyncio.get_event_loop()

    def permissions_for(self, obj):
        perms = discord.Permissions.all()
        perms.embed_links = False
        perms.add_reactions = False
        return perms

    def __getattr__(self, attr):
        return self

    def __call__(self, *args, **kwargs):
        return self

    def __repr__(self):
        return "<PerformanceMocker>"

    def __await__(self):
        future = self.loop.create_future()
        future.set_result(self)
        return future.__await__()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return self

    def __len__(self):
        return 0

    def __bool__(self):
        return False


class owner(commands.Cog):
    """Administrative commands."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.rrole = self.bot.db.prefixed_db(b"rrole-")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def toggle(self, ctx, command):
        """Toggles a command from being disabled or enabled.

        command: str
            The command to be toggled
        """
        command = self.bot.get_command(command)
        if command is None:
            await ctx.send("```No such command```")
        else:
            command.enabled = not command.enabled
            ternary = "enabled" if command.enabled else "disabled"
            await ctx.send(
                f"```Sucessfully {ternary} the {command.qualified_name} command```"
            )

    @commands.command(hidden=True)
    @commands.is_owner()
    async def presence(self, ctx, *, presence):
        """Changes the bots activity.

        presence: str
            The new activity.
        """
        await self.bot.change_presence(
            status=discord.Status.online,
            activity=discord.Game(name=presence),
        )

    @commands.command(hidden=True)
    @commands.is_owner()
    async def perf(self, ctx, *, command):
        """Checks the timing of a command, while attempting to suppress HTTP calls.

        command: str
            The command to run including arguments.
        """
        msg = copy.copy(ctx.message)
        msg.content = f"{ctx.prefix}{command}"

        new_ctx = await self.bot.get_context(msg, cls=type(ctx))

        # Intercepts the Messageable interface a bit
        new_ctx._state = PerformanceMocker()
        new_ctx.channel = PerformanceMocker()

        if new_ctx.command is None:
            return await ctx.send("```No command found```")

        start = time.perf_counter()
        try:
            await new_ctx.command.invoke(new_ctx)
            new_ctx.command.reset_cooldown(new_ctx)
        except commands.CommandError:
            end = time.perf_counter()
            success = "Failure"
            try:
                await ctx.send(f"```py\n{traceback.format_exc()}\n```")
            except discord.HTTPException:
                pass
        else:
            end = time.perf_counter()
            success = "Success"

        await ctx.send(f"```{success}; {(end - start) * 1000:.2f}ms```")

    @commands.command(hiiden=True)
    @commands.is_owner()
    async def prefix(self, ctx, prefix: str):
        """Changes the bots command prefix.

        prefix: str
            The new prefix.
        """
        self.bot.command_prefix = prefix
        await ctx.send(f"```Prefix changed to {prefix}```")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def sudo(
        self, ctx, channel: discord.TextChannel, member: discord.Member, *, command: str
    ):
        """Run a command as another user.

        channel: discord.TextChannel
            The channel to run the command.
        member: discord.Member
            The member to run the command as.
        command: str
            The command name.
        """
        msg = copy.copy(ctx.message)
        channel = channel or ctx.channel
        msg.channel = channel
        msg.author = member
        msg.content = f"{ctx.prefix}{command}"
        new_ctx = await self.bot.get_context(msg, cls=type(ctx))
        await self.bot.invoke(new_ctx)

    async def run_process(self, command):
        process = await asyncio.create_subprocess_shell(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        result = await process.communicate()

        return " ".join([output.decode() for output in result]).split()

    @commands.command(hidden=True, aliases=["pull"])
    @commands.is_owner()
    async def update(self, ctx):
        """Gets latest commits and applies them through git."""
        pull = await self.run_process("git pull")

        if pull == ["Already", "up", "to", "date."]:
            await ctx.send(
                embed=discord.Embed(
                    title="Bot Is Already Up To Date", color=discord.Color.blurple()
                )
            )
        else:
            await self.run_process("poetry install")

            await ctx.send(
                embed=discord.Embed(
                    title="Pulled latests commits, restarting.",
                    color=discord.Color.blurple(),
                )
            )

            await self.bot.logout()

            if os.name == "nt":
                await self.run_process("python ./bot.py")
            else:
                await self.run_process("nohup python3 bot.py &")

    @commands.command(hidden=True, aliases=["deletecmd", "removecmd"])
    @commands.is_owner()
    async def deletecommand(self, ctx, command):
        """Removes command from the bot.

        command: str
            The command to remove.
        """
        self.bot.remove_command(command)
        await ctx.send(embed=discord.Embed(title=f"```Removed command {command}```"))

    @commands.command(hidden=True)
    @commands.is_owner()
    async def kill(self, ctx):
        """Kills the bot."""
        await self.bot.change_presence(
            status=discord.Status.online, activity=discord.Game(name="Dying...")
        )
        await ctx.send(embed=discord.Embed(title="Killing bot"))
        await self.bot.logout()

    @commands.command(hidden=True)
    @commands.is_owner()
    async def load(self, ctx, extension: str):
        """Loads an extension.

        extension: str
            The extension to load.
        """
        extension = f"cogs.{extension}"
        try:
            self.bot.load_extension(extension)
        except (AttributeError, ImportError) as e:
            await ctx.send(
                embed=discord.Embed(
                    title="```py\n{}: {}\n```".format(type(e).__name__, str(e)),
                    color=discord.Color.blurple(),
                )
            )
            return
        await ctx.send(
            embed=discord.Embed(
                title=f"{extension} loaded.", color=discord.Color.blurple()
            )
        )

    @commands.command(hidden=True)
    @commands.is_owner()
    async def unload(self, ctx, extension: str):
        """Unloads an extension.

        extension: str
            The extension to unload.
        """
        extension = f"cogs.{extension}"
        self.bot.unload_extension(extension)
        await ctx.send(
            embed=discord.Embed(
                title=f"{extension} unloaded.", color=discord.Color.blurple()
            )
        )

    @commands.command(hidden=True)
    @commands.is_owner()
    async def reload(self, ctx, extension: str):
        """Reloads an extension.

        extension: str
            The extension to reload.
        """
        extension = f"cogs.{extension}"
        self.bot.reload_extension(extension)
        await ctx.send(
            embed=discord.Embed(
                title=f"{extension} reloaded.", color=discord.Color.blurple()
            )
        )

    @commands.command(hidden=True)
    @commands.is_owner()
    async def restart(self, ctx):
        """Restarts all extensions."""
        for extension in [
            f.replace(".py", "")
            for f in os.listdir("cogs")
            if os.path.isfile(os.path.join("cogs", f))
        ]:
            try:
                self.bot.reload_extension(f"cogs.{extension}")
            except Exception as e:
                if (
                    e
                    == f"ExtensionNotLoaded: Extension 'cogs.{extension}' has not been loaded."
                ):
                    self.bot.load_extension(f"cogs.{extension}")
                else:
                    await ctx.send(
                        embed=discord.Embed(
                            title="```{}: {}\n```".format(type(e).__name__, str(e)),
                            color=discord.Color.blurple(),
                        )
                    )
        await ctx.send(
            embed=discord.Embed(
                title="Extensions restarted.", color=discord.Color.blurple()
            )
        )

    @commands.command(hidden=True)
    @commands.is_owner()
    async def revive(self, ctx):
        """Kills the bot then revives it."""
        await ctx.send(
            embed=discord.Embed(
                title="Killing bot.",
                color=discord.Color.blurple(),
            )
        )
        await self.bot.logout()
        if os.name == "nt":
            os.system("python ./bot.py")
        else:
            os.system("nohup python3 bot.py &")

    @commands.command()
    @commands.is_owner()
    async def rrole(self, ctx, *emojis):
        """Starts a slightly interactive session to create a reaction role.

        emojis: tuple
            A tuple of emojis.
        """
        await ctx.message.delete()

        if emojis == ():
            return await ctx.send(
                "Put emojis as arguments in the command e.g rrole :fire:"
            )

        channel = await self.await_for_message(
            ctx, "Send the channel you want the message to be in"
        )
        breifs = await self.await_for_message(
            ctx, "Send an brief for every emote Seperated by ;"
        )
        roles = await self.await_for_message(
            ctx, "Send an role id/name for every role Seperated by ;"
        )

        roles = roles.content.split(";")

        for index, role in enumerate(roles):
            if not role.isnumeric():
                try:
                    role = discord.utils.get(ctx.guild.roles, name=role)
                    roles[index] = role.id
                except commands.errors.RoleNotFound:
                    return await ctx.send(f"Could not find role {index}")

        msg = "**Role Menu:**\nReact for a role.\n"

        for emoji, breif in zip(emojis, breifs.content.split(";")):
            msg += f"\n{emoji}: `{breif}`\n"
        message = await channel.channel.send(msg)

        for emoji in emojis:
            await message.add_reaction(emoji)

        self.rrole.put(
            str(message.id).encode(), ujson.dumps(dict(zip(emojis, roles))).encode()
        )

    @commands.command()
    @commands.is_owner()
    async def redit(self, ctx, message: discord.Message, *emojis):
        """Edit a reaction role message.

        message: discord.Message
            The id of the reaction roles message.
        emojis: tuple
            A tuple of emojis.
        """
        reaction = self.rrole.get(str(message.id).encode())

        if not reaction:
            return await ctx.send("```Message not found```")

        msg = message.content

        breifs = await self.await_for_message(
            ctx, "Send an brief for every emote Seperated by ;"
        )
        roles = await self.await_for_message(
            ctx, "Send an role id/name for every role Seperated by ;"
        )

        roles = roles.content.split(";")

        for index, role in enumerate(roles):
            if not role.isnumeric():
                try:
                    role = discord.utils.get(ctx.guild.roles, name=role)
                    roles[index] = role.id
                except commands.errors.RoleNotFound:
                    return await ctx.send(f"Could not find role {index}")

        msg += "\n"

        for emoji, breif in zip(emojis, breifs.content.split(";")):
            msg += f"\n{emoji}: `{breif}`\n"

        await message.edit(content=msg)

        for emoji in emojis:
            await message.add_reaction(emoji)

        reaction = ujson.loads(reaction.decode())

        for emoji, role in zip(emojis, roles):
            reaction[emoji] = role

        self.rrole.put(str(message.id).encode(), ujson.dumps(reaction).encode())

    @staticmethod
    async def await_for_message(ctx, message):
        def check(message: discord.Message) -> bool:
            return message.author.id == ctx.author.id and message.channel == ctx.channel

        tmp_msg = await ctx.send(message)

        try:
            message = await ctx.bot.wait_for("message", timeout=300.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send("Timed out")

        await tmp_msg.delete()
        await message.delete()

        return message


def setup(bot: commands.Bot) -> None:
    """Starts owner cog."""
    bot.add_cog(owner(bot))
